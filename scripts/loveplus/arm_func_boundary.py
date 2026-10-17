#!/usr/bin/env python3
"""ARM32 静态辅助：定位函数边界。

用途：字面量池紧跟函数末尾，给定池地址 P（池前一条指令 = 该函数的返回指令），
推断**拥有该池的函数起点**，供 r2 `af @ start; pdf` 使用。

判定：从候选起点线性走到 P-4，若中途出现返回指令或另一个序言，则该候选是内层
片段，继续向更早处找；取最靠近 P 的合格候选。

序言（ARM，小端）：
  e92d4xxx/e92d5xxx/e92d8xxx/e92d9xxx  push {..., lr}   (bit14 = lr)
  e52de004                            str lr, [sp, #-4]!
  e1a0c00d 后接 e92dxxxx              mov ip, sp + stmdb
返回指令：
  e8bd****（带 pc 位 0x8000）、e12fff1e(bx lr)、e12fff3e(blx lr)、e1a0f00e(mov pc,lr)

用法:
    arm_func_boundary.py 0x6d73dc            # 池地址
    arm_func_boundary.py --at 0x6d73d8       # 直接给代码地址
"""
import argparse
import struct
import sys

sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from common_paths import CODE_UNPACKED  # noqa: E402

BASE = 0x00100000
ENDERS = ('e12fff1e', 'e12fff3e', 'e1a0f00e')


def w(data, va):
    return struct.unpack_from('<I', data, va - BASE)[0]


def is_end(word):
    h = f'{word:08x}'
    if h.startswith('e8bd') and (word & 0x8000):
        return 'pop{...,pc}'
    if h in ENDERS:
        return 'bx_lr/mov_pc_lr'
    return ''


def is_prologue(word):
    h = f'{word:08x}'
    if h.startswith('e92d') and (word & 0x4000):
        return 'push{...,lr}'
    if h == 'e52de004':
        return 'str lr,[sp,#-4]!'
    return ''


def find_end(data, pool, span=0x80):
    """池可能含多个字（一个函数可有连续多池字）；向前找最近的返回指令。"""
    for back in range(4, span, 4):
        va = pool - back
        tag = is_end(w(data, va))
        if tag:
            return va, tag
    return None, ''


def find_start(data, end_va, span=0x10000):
    """end_va = 该函数最后一条指令地址。"""
    best = None
    for back in range(0, span, 4):
        cand = end_va - back
        if cand < BASE:
            break
        tag = is_prologue(w(data, cand))
        if not tag:
            continue
        ok = True
        for cur in range(cand + 4, end_va, 4):
            word = w(data, cur)
            if is_end(word) or is_prologue(word):
                ok = False
                break
        if ok:
            best = (cand, tag)
            break
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('addr', nargs='+', help='字面量池地址（池前一指令视为函数末尾）')
    ap.add_argument('--at', action='store_true', help='入参直接当作函数最后一条指令地址')
    ap.add_argument('--code', default=CODE_UNPACKED)
    args = ap.parse_args()
    data = open(args.code, 'rb').read()
    for s in args.addr:
        pool = int(s, 0)
        if args.at:
            end_va = pool
            tag = is_end(w(data, end_va))
        else:
            end_va, tag = find_end(data, pool)
        if not end_va:
            print(f'池 0x{pool:08x}: 池前 0x80 字节内没有返回指令')
            continue
        r = find_start(data, end_va)
        if not r:
            print(f'池 0x{pool:08x}: 末 0x{end_va:08x} 未能定位函数起点')
            continue
        start, ptag = r
        print(f'池 0x{pool:08x}: 函数末 0x{end_va:08x}({tag}) '
              f'→ 起点 0x{start:08x} [{ptag}]  长度 0x{end_va - start + 4:x}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
