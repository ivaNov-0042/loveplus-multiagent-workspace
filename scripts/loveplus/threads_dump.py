#!/usr/bin/env python3
"""启动无头模拟器，等它"卡住"后，枚举所有线程的 PC 与所在函数(反汇编上下文)。

用于定位游戏卡在何处(如等待某个未就绪的服务/事件)。
"""
import os
import re
import struct
import subprocess
import sys
import time

from common_paths import *
from rsp_client import GDBClient
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM

PORT = 24790
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
    log = open('/tmp/threads.log', 'wb')
    proc = subprocess.Popen([H, R, '--gdb', '--port', str(PORT), '--frames', '200000'],
                            stdout=log, stderr=subprocess.STDOUT,
                            stdin=subprocess.DEVNULL, start_new_session=True)
    try:
        time.sleep(14)
        c = connect(PORT)
        # 让游戏跑一段，进入"卡住"状态
        c.send('c', wait_ack=False)
        time.sleep(25)

        # 枚举线程
        c.send('qXfer:threads:read::0,4000')
        th = c.recv_packet()
        ids = re.findall(r'<thread id="(\d+)"', th)
        print("[i] threads:", ids)

        code = open(CODE, 'rb').read()
        md = Cs(CS_ARCH_ARM, CS_MODE_ARM)

        infos = []
        for tid in ids:
            c.send('H g' + tid)
            c.recv_packet()
            try:
                rp = c.cmd('p f')       # pc
                rs = c.cmd('p d')       # sp (reg 13 = 'd')
                pc = le_hex_to_int(rp)
                sp = le_hex_to_int(rs)
            except Exception:
                pc = sp = 0
            infos.append((tid, pc, sp))

        for tid, pc, sp in infos:
            print(f"\n=== thread {tid}: pc={pc:#010x} sp={sp:#010x} ===")
            if BASE <= pc < BASE + len(code):
                off = pc - BASE
                for insn in md.disasm(code[off:off + 32], pc):
                    print(f"    {insn.address:#010x}: {insn.mnemonic}\t{insn.op_str}")
            else:
                print("    (pc outside code.bin .text)")

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
