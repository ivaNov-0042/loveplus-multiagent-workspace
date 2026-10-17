#!/usr/bin/env python3
"""code.bin 静态侦察：定位 Siren14 语音相关字符串与引用。"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_paths import *

BASE = 0x00100000


def find_all(data, pat):
    res, i = [], data.find(pat)
    while i >= 0:
        res.append(i)
        i = data.find(pat, i + 1)
    return res


def main():
    d = open(CODE, 'rb').read()
    print(f"code.bin size = {len(d)} (0x{len(d):x}), load base = 0x{BASE:08x}")
    targets = ['Voice', 'Siren', 'spp', 'dpb', '.bin', '/Plus/', 'Sound', 'DSP', 'AT9', 'bcsar']
    for s in targets:
        for name, pat in [('ascii', s.encode()), ('utf16le', s.encode('utf-16-le'))]:
            hits = find_all(d, pat)
            if hits:
                va = [f"0x{BASE + h:08x}" for h in hits[:6]]
                print(f"  {s:8s} [{name:7s}] n={len(hits):3d} va={va}")


if __name__ == '__main__':
    sys.exit(main())
