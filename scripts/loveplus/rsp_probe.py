#!/usr/bin/env python3
"""在单个会话内：连接 GDB stub，验证 单步 / 断点 / continue 的行为。

用法: rsp_probe.py <port> [bp_addr]
"""
import os
import sys
import time

from common_paths import *
from rsp_client import GDBClient


def main():
    port = int(sys.argv[1])
    bp = int(sys.argv[2], 0) if len(sys.argv) > 2 else None
    c = GDBClient(port=port, timeout=20)

    def pc():
        return c.read_registers()['pc']

    print(f"[i] connect ok, stop_reply={c.stop_reply[:40]}")
    p0 = pc()
    print(f"[i] pc0 = {p0:#010x}")

    # 单步 3 次
    for i in range(3):
        c.sock.settimeout(10)
        rep = c.cmd('s')
        p = pc()
        print(f"[step {i}] reply={rep[:16]!r} pc={p:#010x}")

    # 断点：设两个相隔一定距离的地址，continue 看是否命中
    if bp is not None:
        print(f"[i] set bp at {bp:#x} -> {c.set_break(bp)}")
        c.sock.settimeout(15)
        rep = c.cmd('c')
        p = pc()
        print(f"[continue] reply={rep[:60]!r} pc={p:#010x}")
        print(f"[continue] hit={'YES' if p == bp else 'NO'}")

    c.close()


if __name__ == '__main__':
    main()
