#!/usr/bin/env python3
"""「はじめから」推进 + 断点 + 截图（一次跑完）。

1. 启动无头模拟器(带 stub)；
2. 在存档引继菜单点「はじめから」（多点几次，容忍时序）；
3. 期间在热点函数下断点并命中断一次（证明断点调试可用）；
4. 结束前截图，看是否进入主流程。
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=24790)
    ap.add_argument('--frames', type=int, default=600000)
    args = ap.parse_args()

    # 「はじめから」：菜单约在 frame ~110k 出现，之后多次点 (0.569, 0.50)，再点确认
    taps = ';'.join(f'{f}:14:0:0.569:0.50'
                    for f in range(105000, 205000, 12000))
    log = open('/tmp/hajime.log', 'wb')
    proc = subprocess.Popen(
        [HEADLESS, ROM, '--gdb', '--port', str(args.port), '--frames', str(args.frames),
         '--input-script', taps, '--dump-every', '25000', '--dump-prefix', '/tmp/hj'],
        stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True,
        env={'SDL_AUDIODRIVER': 'dummy', 'AZAHAR_LOG': '*:Error', 'PATH': '/usr/bin:/bin'})

    code = open(CODE, 'rb').read()
    try:
        time.sleep(12)
        c = connect(args.port)
        samples_done = False
        hot = Counter()
        # 让游戏推进到菜单之后，同时采样热点
        for _ in range(14):
            c.send('c', wait_ack=False)
            time.sleep(6)
            c.send('\x03', wait_ack=False)
            time.sleep(0.4)
            try:
                c.sock.settimeout(2)
                surf = c.sock.recv(4096)
            except Exception:
                pass
            c.send('qXfer:threads:read::0,4000')
            ids = re.findall(r'<thread id="(\d+)"', c.recv_packet())
            for tid in ids:
                c.send('H g' + tid)
                try:
                    c.recv_packet()
                    hot[le_hex_int(c.cmd('p f'))] += 1
                except Exception:
                    pass

        cand = [a for a, _ in hot.most_common() if BASE <= a < 0x00800000]
        target = cand[0] if cand else 0x00122a50
        print(f"[i] hot .text: {[hex(a) for a in cand[:6]]}")
        print(f"[i] set bp @ {target:#010x} -> {c.set_break(target)}")
        c.send('Hc-1')
        try:
            c.recv_packet()
        except Exception:
            pass

        # 命中一次
        for attempt in range(4):
            c.sock.settimeout(25)
            rep = c.cmd('c')
            print(f"[bp] try {attempt}: {rep[:56]!r}")
            if rep[:1] in ('T', 'S'):
                m = re.search(r'thread:([0-9a-fA-F]+);', rep)
                tid = m.group(1) if m else None
                if tid:
                    c.send('H g' + tid)
                    try:
                        c.recv_packet()
                    except Exception:
                        pass
                regs = c.read_registers()
                thumb = bool(regs.get('cpsr', 0) & 0x20)
                md = Cs(CS_ARCH_ARM, CS_MODE_THUMB if thumb else CS_MODE_ARM)
                print(f"[bp] HIT pc={regs['pc']:#010x} lr={regs['lr']:#010x} "
                      f"sp={regs['sp']:#010x} mode={'THUMB' if thumb else 'ARM'} thread={tid}")
                off = regs['pc'] - BASE
                for insn in md.disasm(code[off:off + 16], regs['pc']):
                    print(f"      {insn.address:#010x}: {insn.mnemonic}\t{insn.op_str}")
                break

        # 让游戏继续跑一阵，最后 dump
        c.send('c', wait_ack=False)
        time.sleep(30)
        c.send('\x03', wait_ack=False)
        time.sleep(0.5)
        try:
            c.sock.settimeout(2)
            c.sock.recv(4096)
        except Exception:
            pass
        c.close()
        print("[OK] done")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        log.close()


if __name__ == '__main__':
    main()
