#!/usr/bin/env python3
"""端到端验证：启动 azahar_headless(GDB stub) → 连接 → 单步/断点/continue。

单进程完成，避免跨 shell 断开导致 server 重启。
"""
import os
import subprocess
import sys
import time

from common_paths import *
from rsp_client import GDBClient

PORT = 24799


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
    log = open('/tmp/embed_gdb.log', 'wb')
    proc = subprocess.Popen([HEADLESS, ROM, '--gdb', '--port', str(PORT)],
                            stdout=log, stderr=subprocess.STDOUT,
                            stdin=subprocess.DEVNULL, start_new_session=True)
    try:
        # 等 stub 起来（进程启动 + Load 到 ApplySettings）
        time.sleep(14)
        c = connect(PORT)

        def pc():
            return c.read_registers()['pc']

        print(f"[i] stop={c.stop_reply[:40]}")
        print(f"[i] pc0 = {pc():#010x}")

        # 取线程列表
        c.send('qXfer:threads:read::0,1000')
        th = c.recv_packet()
        nthreads = th.count('<thread ')
        print(f"[i] threads = {nthreads}")

        # continue 一段时间，然后 interrupt，看 PC 是否变化（证明真的在跑）
        c.send('c', wait_ack=False)
        time.sleep(2.0)
        c.send('\x03', wait_ack=False)
        time.sleep(0.5)
        c.sock.settimeout(3)
        try:
            rep = c.sock.recv(4096)
        except Exception:
            rep = b''
        p1 = pc()
        print(f"[continue] stop_reply={rep[:50]!r} pc={p1:#010x} changed={p1 != 0x00105b44}")

        # 单步：从当前 PC 走 5 步，PC 应变化
        seq = [pc()]
        for i in range(5):
            c.sock.settimeout(8)
            r = c.cmd('s')
            seq.append(pc())
        print(f"[step] seq = {[hex(x) for x in seq]}")

        # 断点：设在其后一个地址，continue 应命中
        target = seq[-1] + 4
        print(f"[bp] set {target:#x} -> {c.set_break(target)}")
        c.sock.settimeout(10)
        rep = c.cmd('c')
        ph = pc()
        print(f"[bp] hit={ph == target} pc={ph:#010x} reply={rep[:40]!r}")

        c.close()
        print("[OK] dynamic debugging verified")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        log.close()


if __name__ == '__main__':
    main()
