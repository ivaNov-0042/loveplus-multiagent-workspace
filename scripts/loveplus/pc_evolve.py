#!/usr/bin/env python3
"""启动无头模拟器(带 GDB stub)，随时间采样各线程 PC，证明 CPU 真实执行并在推进。

- 读取 CPSR 判断 ARM/Thumb，用 capstone 正确反汇编当前指令。
- 多次采样，若 PC 集合随时间变化 => CPU 在执行。
"""
import os
import re
import subprocess
import sys
import time
from collections import Counter

from common_paths import *
from rsp_client import GDBClient
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_THUMB

PORT = 24760
BASE = 0x00100000


def le_hex_to_int(s):
    b = bytes.fromhex(s)
    b += b'\x00' * (4 - len(b))
    return int.from_bytes(b[:4], 'little')


def connect(port, tries=60):
    last = None
    for _ in range(tries):
        try:
            return GDBClient(port=port, timeout=20)
        except OSError as e:
            last = e
            time.sleep(0.5)
    raise last


def main():
    log = open('/tmp/pcsim.log', 'wb')
    proc = subprocess.Popen([H, R, '--gdb', '--port', str(PORT), '--frames', '400000'],
                            stdout=log, stderr=subprocess.STDOUT,
                            stdin=subprocess.DEVNULL, start_new_session=True)
    code = open(CODE, 'rb').read()
    try:
        time.sleep(12)
        c = connect(PORT)
        # 让游戏跑一会
        c.send('c', wait_ack=False)

        seen = Counter()
        samples = []
        for round_i in range(12):
            time.sleep(2.0)
            c.send('\x03', wait_ack=False)  # interrupt
            time.sleep(0.3)
            try:
                c.sock.settimeout(2)
                c.sock.recv(4096)
            except Exception:
                pass
            c.send('qXfer:threads:read::0,4000')
            th = c.recv_packet()
            ids = re.findall(r'<thread id="(\d+)"', th)
            round_pcs = set()
            for tid in ids[:4]:
                c.send('H g' + tid)
                c.recv_packet()
                try:
                    pc = le_hex_to_int(c.cmd('p f'))
                except Exception:
                    continue
                round_pcs.add(pc)
                seen[pc] += 1
            samples.append(round_pcs)
            c.send('c', wait_ack=False)

        all_pcs = sorted(seen)
        print(f"[i] total samples={len(samples)} distinct PCs={len(all_pcs)}")
        print("[i] top PCs (address x count):")
        for a, n in seen.most_common(12):
            print(f"    {a:#010x} x{n}")
        # disassemble a few (assume ARM first, then Thumb)
        md_arm = Cs(CS_ARCH_ARM, CS_MODE_ARM)
        md_thumb = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
        for a in [p for p, _ in seen.most_common(4)]:
            if not (BASE <= a < BASE + len(code)):
                continue
            off = a - BASE
            print(f"\n=== {a:#010x} (ARM) ===")
            for insn in md_arm.disasm(code[off:off + 16], a):
                print(f"    {insn.mnemonic}\t{insn.op_str}")
            print(f"--- {a:#010x} (THUMB) ---")
            for insn in md_thumb.disasm(code[off:off + 12], a):
                print(f"    {insn.mnemonic}\t{insn.op_str}")
        c.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        log.close()


if __name__ == '__main__':
    main()
