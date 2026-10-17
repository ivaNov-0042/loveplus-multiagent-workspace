#!/usr/bin/env python3
"""从 guest 内存 dump 出解压后的 .text（真实指令），保存供反汇编/分析。

- 从加载日志知 Entry=0x00100000, CodeSize=0x0068F7FC。
- 分块通过 GDB stub 读回，写入 data/loveplus/nlp_plus/code_unpacked.bin。
"""
import os
import subprocess
import sys
import time

from common_paths import *
from rsp_client import GDBClient

BASE = 0x00100000
SIZE = 0x0068F7FC
PORT = 24786


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
    log = open('/tmp/dump.log', 'wb')
    proc = subprocess.Popen(
        [HEADLESS, ROM, '--gdb', '--port', str(PORT), '--frames', '300000'],
        stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True,
        env={'SDL_AUDIODRIVER': 'dummy', 'AZAHAR_LOG': '*:Error', 'PATH': '/usr/bin:/bin'})
    try:
        time.sleep(12)
        c = connect(PORT)
        c.send('c', wait_ack=False)
        time.sleep(2)

        # 分块读取（每块 0x1000，避免单包过大）
        chunk = 0x1000
        total = 0
        with open(OUT, 'wb') as f:
            va = BASE
            while va < BASE + SIZE:
                n = min(chunk, BASE + SIZE - va)
                try:
                    data = c.read_mem(va, n)
                    f.write(data)
                    total += len(data)
                except Exception as e:
                    print(f"  read {va:#x} failed: {e}; padding zeros")
                    f.write(b'\x00' * n)
                    total += n
                va += n
                if (va - BASE) % 0x200000 == 0:
                    print(f"  {va - BASE:#x} / {SIZE:#x}")
        print(f"[OK] dumped {total:#x} bytes -> {OUT}")
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
