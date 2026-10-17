#!/usr/bin/env python3
"""验证断点真的会在 guest 代码里命中：
1. 启动无头模拟器 + GDB stub；
2. 采样多个线程的 PC，挑一个出现频率高的 guest 地址；
3. 在该地址下断点，continue，确认命中。
"""
import os
import re
import subprocess
import sys
import time
from collections import Counter

from common_paths import *
from rsp_client import GDBClient

PORT = 24795


def le_hex_to_int(s):
    """RSP 'p' 寄存器返回小端十六进制 -> 目标 u32 值。"""
    b = bytes.fromhex(s)
    b = b + b'\x00' * (4 - len(b))
    return int.from_bytes(b[:4], 'little')


def connect(port, tries=40):
    last = None
    for _ in range(tries):
        try:
            return GDBClient(port=port, timeout=15)
        except OSError as e:
            last = e
            time.sleep(0.5)
    raise last


def main():
    log = open('/tmp/bp_hit.log', 'wb')
    proc = subprocess.Popen([H, R, '--gdb', '--port', str(PORT)],
                            stdout=log, stderr=subprocess.STDOUT,
                            stdin=subprocess.DEVNULL, start_new_session=True)
    try:
        time.sleep(14)
        c = connect(PORT)
        c.send('qXfer:threads:read::0,4000')
        th = c.recv_packet()
        ids = re.findall(r'<thread id="(\d+)"', th)
        print("[i] threads:", ids)

        # 采样：多次选不同线程，收集 PC
        hot = Counter()
        for _ in range(15):
            for tid in ids:
                c.send('H g' + tid)
                c.recv_packet()
                r = c.cmd('p f')
                try:
                    hot[le_hex_to_int(r)] += 1
                except Exception:
                    pass
            time.sleep(0.2)
        print("[i] top PCs:")
        for a, n in hot.most_common(6):
            print(f"    {a:#010x} x{n}")

        # 选一个落在可执行段(0x00100000..0x00800000)的高频地址
        cand = [a for a, _ in hot.most_common() if 0x00100000 <= a < 0x00800000]
        if not cand:
            print("[!] no hot address in text; sampling again")
            return
        addr = cand[0]
        print(f"[i] breakpoint target = {addr:#010x}")
        print("[i] set bp ->", c.set_break(addr))

        # 确保线程 1 处于 continue 状态，然后 continue 等命中
        c.send('Hc-1')
        c.recv_packet()
        c.sock.settimeout(15)
        rep = c.cmd('c')
        print(f"[bp] stop reply={rep[:50]!r}")
        # 读命中处的 PC
        r = c.cmd('p f')
        pcv = le_hex_to_int(r)
        print(f"[bp] hit pc={pcv:#010x}  match={pcv == addr}")
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
