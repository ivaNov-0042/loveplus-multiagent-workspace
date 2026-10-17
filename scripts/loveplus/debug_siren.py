#!/usr/bin/env python3
"""断点调试(实践·稳健版)：无头模拟器 + GDB stub，用「はじめから」进入主流程后断点。

改进：
- 读取寄存器失败时重试；
- 命中线程可能不是 current，先 `H g<tid>` 选中再读；
- 结束前 dump 截屏，确认已进入主流程。
"""
import os
import argparse
import re
import subprocess
import sys
import time
from collections import Counter

from common_paths import *
from rsp_client import GDBClient
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_THUMB

BASE = 0x00100000


def le_hex_int(s):
    b = bytes.fromhex(s)
    b += b'\x00' * (-len(b) % 4)
    return int.from_bytes(b[:4], 'little')


def connect(port, tries=80):
    last = None
    for _ in range(tries):
        try:
            return GDBClient(port=port, timeout=20)
        except OSError as e:
            last = e
            time.sleep(0.5)
    raise last


def get_regs(c, retries=5):
    for _ in range(retries):
        try:
            r = c.read_registers()
            if 'pc' in r:
                return r
        except Exception:
            pass
        time.sleep(0.2)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=24782)
    ap.add_argument('--bp', type=lambda x: int(x, 0), default=None)
    ap.add_argument('--frames', type=int, default=500000)
    ap.add_argument('--settle', type=int, default=50)
    args = ap.parse_args()

    script = '115000:12:0:0.569:0.50;140000:12:0:0.569:0.50;170000:12:0:0.569:0.50'
    log = open('/tmp/debug_siren2.log', 'wb')
    proc = subprocess.Popen(
        [HEADLESS, ROM, '--gdb', '--port', str(args.port), '--frames', str(args.frames),
         '--input-script', script, '--dump-every', '30000', '--dump-prefix', '/tmp/dbg'],
        stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True,
        env={'SDL_AUDIODRIVER': 'dummy', 'AZAHAR_LOG': '*:Error', 'PATH': '/usr/bin:/bin'})

    code = open(CODE, 'rb').read()
    try:
        print(f"[i] emulator pid={proc.pid}")
        time.sleep(12)
        c = connect(args.port)
        print(f"[i] stop_reply={c.stop_reply[:40]}")

        c.send('c', wait_ack=False)
        print(f"[i] running {args.settle}s ...")
        time.sleep(args.settle)

        c.send('qXfer:threads:read::0,4000')
        ids = re.findall(r'<thread id="(\d+)"', c.recv_packet())
        print(f"[i] threads = {ids}")

        hot = Counter()
        for _ in range(10):
            c.send('\x03', wait_ack=False)
            time.sleep(0.25)
            try:
                c.sock.settimeout(2)
                c.sock.recv(4096)
            except Exception:
                pass
            for tid in ids:
                c.send('H g' + tid)
                try:
                    c.recv_packet()
                    hot[le_hex_int(c.cmd('p f'))] += 1
                except Exception:
                    pass
            c.send('c', wait_ack=False)
            time.sleep(0.4)

        cand = [a for a, _ in hot.most_common() if BASE <= a < 0x00800000]
        target = args.bp if args.bp is not None else (cand[0] if cand else None)
        print(f"[i] target bp = {target:#010x}")
        print("[i] set bp ->", c.set_break(target))
        c.send('Hc-1')
        try:
            c.recv_packet()
        except Exception:
            pass

        rep = ''
        for _ in range(3):
            c.sock.settimeout(25)
            rep = c.cmd('c')
            print(f"[bp] stop_reply={rep[:64]!r}")
            if rep[:1] in ('T', 'S'):
                break

        m = re.search(r'thread:([0-9a-fA-F]+);', rep)
        hit_tid = m.group(1) if m else None
        if hit_tid:
            c.send('H g' + hit_tid)
            try:
                c.recv_packet()
            except Exception:
                pass

        print("\n=== BREAKPOINT HIT ===")
        regs = get_regs(c)
        if not regs:
            print("[!] could not read registers")
            c.close()
            return
        names = ['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10', 'r11',
                 'r12', 'sp', 'lr', 'pc']
        for i in range(0, 16, 4):
            print("  " + "  ".join(f"{names[j]}={regs[names[j]]:#010x}" for j in range(i, i + 4)))
        thumb = bool(regs.get('cpsr', 0) & 0x20)
        print(f"  pc={regs['pc']:#010x} match={regs['pc'] == target}  "
              f"cpsr={regs.get('cpsr',0):#010x} mode={'THUMB' if thumb else 'ARM'}"
              f"  thread={hit_tid}")

        off = target - BASE
        md = Cs(CS_ARCH_ARM, CS_MODE_THUMB if thumb else CS_MODE_ARM)
        print(f"\n--- disasm @ pc ({'THUMB' if thumb else 'ARM'}) ---")
        for insn in md.disasm(code[off:off + 24], target):
            print(f"    {insn.address:#010x}: {insn.mnemonic}\t{insn.op_str}")

        print("\n--- stack scan (.text return addrs) ---")
        try:
            region = c.read_mem(regs['sp'] & ~3, 0x200)
            n = 0
            for i in range(0, len(region), 4):
                v = int.from_bytes(region[i:i + 4], 'little')
                if BASE <= v < BASE + len(code):
                    print(f"    [sp+{i:#05x}] -> {v:#010x} (.text+{v - BASE:#x})")
                    n += 1
                    if n >= 16:
                        break
            if n == 0:
                print("    (none on top 0x200)")
        except Exception as e:
            print("  stack read failed:", e)

        if BASE <= regs['lr'] < BASE + len(code):
            lo = regs['lr'] - BASE
            print(f"\n--- caller via lr={regs['lr']:#010x} ---")
            for insn in md.disasm(code[max(0, lo - 12):lo + 8], regs['lr'] - 12):
                mark = ">>>" if insn.address == regs['lr'] else "   "
                print(f"  {mark} {insn.address:#010x}: {insn.mnemonic}\t{insn.op_str}")

        for rname in ('r0', 'r1'):
            a = regs[rname]
            if 0x08000000 <= a < 0x30000000:
                try:
                    mem = c.read_mem(a, 0x40)
                    print(f"\n--- mem @ {rname}={a:#010x} ---")
                    for i in range(0, 0x40, 16):
                        print(f"    {a+i:#010x}: {mem[i:i+16].hex()}")
                except Exception:
                    pass

        # 让游戏继续跑，最后再 dump 一帧确认主流程
        c.send('c', wait_ack=False)
        time.sleep(20)
        c.send('\x03', wait_ack=False)
        time.sleep(0.5)
        try:
            c.sock.settimeout(2)
            c.sock.recv(4096)
        except Exception:
            pass
        c.close()
        print("\n[OK] breakpoint debugging done")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        log.close()


if __name__ == '__main__':
    main()
