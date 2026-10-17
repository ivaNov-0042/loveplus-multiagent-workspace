#!/usr/bin/env python3
"""启动无头模拟器(带 GDB stub)并采样 PC，验证运行时可以看到真实执行流。"""
import os
import subprocess
import sys
import time
from collections import Counter

from common_paths import *
from rsp_client import GDBClient

PORT = 24798


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
    log = open('/tmp/sample_gdb.log', 'wb')
    proc = subprocess.Popen([HEADLESS, ROM, '--gdb', '--port', str(PORT)],
                            stdout=log, stderr=subprocess.STDOUT,
                            stdin=subprocess.DEVNULL, start_new_session=True)
    try:
        time.sleep(14)
        c = connect(PORT)
        c.send('qXfer:threads:read::0,1000')
        _ = c.recv_packet()

        # 让程序跑一会，再逐次 interrupt 采样 PC
        c.send('c', wait_ack=False)
        pcs = []
        for i in range(20):
            time.sleep(0.4)
            c.send('\x03', wait_ack=False)   # interrupt
            try:
                c.sock.settimeout(2)
                c.sock.recv(4096)
            except Exception:
                pass
            # 读取 PC（偶尔首次读可能失败，重试）
            p = None
            for _ in range(5):
                try:
                    regs = c.read_registers()
                    if 'pc' in regs:
                        p = regs['pc']
                        break
                except Exception:
                    time.sleep(0.2)
            if p is None:
                continue
            pcs.append(p)
            c.send('c', wait_ack=False)
        print("[sample] distinct PCs:", len(set(pcs)))
        for p, n in Counter(pcs).most_common(10):
            print(f"   {p:#010x}  x{n}")
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
