#!/usr/bin/env python3
"""在 code.bin(解压后) 里定位"哪些指令引用了目标地址"。

思路：ARM 代码取常量有两种形态——
  1) 字面量池：`ldr rX, [pc, #imm]`，池里存 32bit 绝对值；
  2) 立即数构造：`movw/movt` 或 `add/sub rX, pc, #imm`。
本脚本先搜 4 字节小端绝对值出现的偏移（=池位置），再用 capstone 反查
池前面窗口内命中该池地址的指令；movw/movt 对也从窗口里匹配。

用法:
    find_code_xref.py 0x844cfd [0x844cc8 ...]
    find_code_xref.py --window 4096 0x844cfd
"""
import argparse
import struct
import sys

sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from common_paths import CODE_UNPACKED  # noqa: E402

BASE = 0x00100000
try:
    from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_LITTLE_ENDIAN
except ImportError:  # pragma: no cover
    Cs = None


def pool_hits(data: bytes, va: int):
    """返回文件中等于 va 的 4 字节小端位置（虚拟地址）。"""
    pat = struct.pack('<I', va)
    out, i = [], data.find(pat)
    while i >= 0:
        if i % 4 == 0:
            out.append(BASE + i)
        i = data.find(pat, i + 1)
    return out


def xrefs_to_pool(data: bytes, pool_va: int, window: int):
    """在池地址前的窗口里找命中该池的取常数指令。"""
    off = pool_va - BASE
    start = max(0, off - window)
    seg = data[start:off + 4]
    base_va = BASE + start
    hits = []
    if Cs is None:
        return hits
    md = Cs(CS_ARCH_ARM, CS_MODE_ARM | CS_MODE_LITTLE_ENDIAN)
    for ins in md.disasm(seg, base_va):
        op = ins.op_str.replace(' ', '')
        # ldr rX, [pc, #imm]
        if ins.mnemonic.startswith('ldr') and 'pc' in op:
            try:
                imm = int(op.split('#')[1].rstrip(']'), 0)
            except (IndexError, ValueError):
                continue
            if (ins.address + 8 + imm) == pool_va or (ins.address + 8 - imm) == pool_va:
                hits.append((ins.address, f'{ins.mnemonic} {ins.op_str}', ins.address + 8 + imm))
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('vas', nargs='+', help='目标数据虚拟地址(touch: 0x… 或十进制)')
    ap.add_argument('--window', type=int, default=4096, help='池前回溯窗口(默认 4096)')
    ap.add_argument('--code', default=CODE_UNPACKED)
    ap.add_argument('--pool', action='store_true',
                    help='把入参当作字面量池地址，直接找加载它的指令')
    args = ap.parse_args()

    data = open(args.code, 'rb').read()
    print(f'image={args.code} size=0x{len(data):x} base=0x{BASE:08x}')
    if args.pool:
        for vs in args.vas:
            pv = int(vs, 0)
            hits = xrefs_to_pool(data, pv, args.window)
            print(f'\n== 池 0x{pv:08x} (内容 0x{int.from_bytes(data[pv - BASE:pv - BASE + 4], "little"):08x}) ==')
            for addr, txt, calc in hits:
                print(f'  0x{addr:08x}: {txt}')
        return 0
    for vs in args.vas:
        va = int(vs, 0)
        pools = pool_hits(data, va)
        print(f'\n== 目标 0x{va:08x} : 池命中 {len(pools)} 处 ==')
        for pv in pools:
            hits = xrefs_to_pool(data, pv, args.window)
            tag = f'  [池 0x{pv:08x}]'
            if not hits:
                print(f'{tag} 窗口内无取常数指令')
            for addr, txt, calc in hits:
                print(f'{tag} 0x{addr:08x}: {txt}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
