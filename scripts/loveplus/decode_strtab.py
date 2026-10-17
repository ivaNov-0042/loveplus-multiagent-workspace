#!/usr/bin/env python3
"""code.bin 字符串表解码：观察到 [len_byte][chars] 的形式。

扫描 code.bin 中所有 "长度字节 + 可打印 ASCII" 序列，输出其中的字符串，
用于定位 Siren14 语音 bank 的路径/相关字符串。
"""
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_paths import *

BASE = 0x00100000


def decode_len_prefixed(data):
    """yield (offset, text)：长度字节 1..63 后跟等长可打印 ASCII。"""
    out = []
    i = 0
    n = len(data)
    while i < n:
        L = data[i]
        if 1 <= L <= 63 and i + 1 + L <= n:
            seg = data[i + 1:i + 1 + L]
            if all(0x20 <= c < 0x7f for c in seg):
                out.append((i, seg.decode('latin1')))
                i += 1 + L
                continue
        i += 1
    return out


def main():
    data = open(CODE, 'rb').read()
    strings = decode_len_prefixed(data)
    print(f"total len-prefixed strings: {len(strings)}")
    kw = ['siren', 'spp', 'voice', 'sound', 'plus', 'bcstm', 'bcsar', 'strm', 'dsp',
          'at9', 'stream', 'bank', 'sd', 'vx', 'se', 'bgm']
    for off, s in strings:
        low = s.lower()
        if any(k in low for k in kw) or '/' in s or '.' in s:
            print(f"  0x{BASE + off:08x}: {s!r}")


if __name__ == '__main__':
    sys.exit(main())
