#!/usr/bin/env python3
"""在 code.bin 中查找对指定虚地址(字符串等)的 ARM 引用(LDR literal)。

3DS ARM11 code.bin 为裸 .text，加载基址 0x00100000。
ARM 的 PC 相对字面量池: LDR Rn,[PC,#imm] => 目标地址 = (指令地址+8) 对齐后 + imm，
其中 imm 为无符号(可正可负，取 4 字节对齐)。反之，给定目标 VA，可搜索字面量池里
出现的 4 字节值等于目标，并回溯指令。
"""
import os
import struct
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_paths import *

BASE = 0x00100000


def load():
    return open(CODE, 'rb').read()


def find_literal_xrefs(data, target_va):
    """返回 (literal_off, instr_off) 列表：字面量池里存有 target_va 的位置，以及可能的 LDR 指令位置。"""
    le = struct.pack('<I', target_va)
    hits = []
    i = data.find(le)
    while i >= 0:
        # 回溯 <=1024 字节内的 ARM LDR 指令：字面量地址 = (pc+8) & ~3 + imm12*4
        lit_va = BASE + i
        found_instr = None
        for back in range(0, 1024, 4):
            off = i - back
            if off < 0:
                break
            w = struct.unpack('<I', data[off:off + 4])[0]
            # LDR (imm) : bits[27:26]=01, bit[24]=1(P), bit[23]=U, bits[20]=1(L)
            if ((w >> 26) & 3) == 1 and ((w >> 24) & 1) == 1 and ((w >> 23) & 1) == 1 \
                    and ((w >> 20) & 1) == 1:
                imm = w & 0xFFF
                pc = BASE + off + 8
                if (w >> 23) & 1:
                    addr = (pc & ~3) + imm
                else:
                    addr = (pc & ~3) - imm
                if addr == lit_va:
                    found_instr = off
                    break
        hits.append((i, found_instr))
        i = data.find(le, i + 1)
    return hits


def main():
    data = load()
    targets = {
        '0x004f8905 Voice': 0x004f8905,
        '0x004f8923 /Plus/': 0x004f8923,
        '0x004f88ce dpb': 0x004f88ce,
        '0x002a037d Voice': 0x002a037d,
        '0x00431183 Voice': 0x00431183,
        '0x004f57ee Voice': 0x004f57ee,
        '0x00297aef SoundOpt': 0x00297aef,
    }
    for name, va in targets.items():
        hits = find_literal_xrefs(data, va)
        print(f"\n{name}: literal 出现 {len(hits)} 次")
        for lit, instr in hits[:10]:
            if instr is not None:
                print(f"  literal@0x{BASE + lit:08x}  <- LDR instr@0x{BASE + instr:08x}")
            else:
                print(f"  literal@0x{BASE + lit:08x}  (未定位 LDR)")


if __name__ == '__main__':
    sys.exit(main())
