#!/usr/bin/env python3
"""对比：运行时的真实 .text 内存 vs 磁盘上的 code.bin。

目的：确认 code.bin 是否为压缩(BLZ)格式 —— 若是，静态反汇编会全是乱码，
必须以 guest 内存或以解压后的 .text 为准。
"""
import os
import subprocess
import sys
import time

from common_paths import *
from rsp_client import GDBClient
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM

BASE = 0x00100000
PORT = 24785


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
    code = open(CODE, 'rb').read()
    log = open('/tmp/cmp.log', 'wb')
    proc = subprocess.Popen(
        [HEADLESS, ROM, '--gdb', '--port', str(PORT), '--frames', '300000'],
        stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True,
        env={'SDL_AUDIODRIVER': 'dummy', 'AZAHAR_LOG': '*:Error', 'PATH': '/usr/bin:/bin'})
    try:
        time.sleep(12)
        c = connect(PORT)
        c.send('c', wait_ack=False)
        time.sleep(3)

        for va in (0x00100000, 0x00105b44, 0x00122a50, 0x0011b5f4):
            off = va - BASE
            disk = code[off:off + 32]
            try:
                live = c.read_mem(va, 32)
            except Exception as e:
                print(f"{va:#x}: live read failed {e}")
                continue
            same = disk[:len(live)] == live[:len(disk)]
            print(f"\n=== VA {va:#x} (file off {off:#x})  same={same} ===")
            print(f"  disk code.bin: {disk.hex()}")
            print(f"  guest memory : {live.hex()}")
            md = Cs(CS_ARCH_ARM, CS_MODE_ARM)
            print("  disasm(guest, ARM):")
            for insn in md.disasm(live, va):
                print(f"    {insn.address:#010x}: {insn.mnemonic}\t{insn.op_str}")

        # 反查：在 guest 中能否找到 code.bin 开头的字节（说明是否直接加载）
        print("\n=== does guest contain code.bin's start? ===")
        try:
            head = code[:16]
            m = c.read_mem(0x08000000, 0x1000)
            print(f"  code.bin[:16] = {head.hex()}")
            print(f"  mem@0x08000000 = {m[:16].hex()}")
        except Exception as e:
            print("  ", e)
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
