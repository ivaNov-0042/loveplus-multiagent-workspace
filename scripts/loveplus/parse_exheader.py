#!/usr/bin/env python3
"""解析 NLP+ 的 ExHeader，输出权威的段基址/大小（text/ro/data/bss）。

ExHeader 位于 NCCH 头部偏移 0x200 处，长度 0x400。
CodeSetInfo 结构（azahar ncch_container.h）：
  name[8], flags(5+1+2), text{address,num_max_pages,code_size}, stack_size,
  ro{...}, reserved[4], data{...}, bss_size
"""
import os
import struct
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_paths import *

# NCSD 分区0 起始 = 0x4000（见此前分析）；NCCH 头 0x100 起，ExHeader 在 NCCH+0x200。
NCSD_P0 = 0x4000
NCCH_EXHEADER = NCSD_P0 + 0x200
EXHEADER_SIZE = 0x400


def main():
    with open(ROM, 'rb') as f:
        f.seek(NCCH_EXHEADER)
        eh = f.read(EXHEADER_SIZE)
    # ExHeader_Header 前 0x400: sci 在偏移 0 起
    # ExHeader_CodeSetInfo 从 ExHeader 偏移 0x0 开始
    base = 0x0
    name = eh[base:base + 8]
    off = base + 8 + 5 + 1 + 2  # name + flags(5+1+2)
    text_addr, text_pages, text_size = struct.unpack_from('<III', eh, off)
    off += 12
    stack_size, = struct.unpack_from('<I', eh, off); off += 4
    ro_addr, ro_pages, ro_size = struct.unpack_from('<III', eh, off); off += 12
    off += 4  # reserved
    data_addr, data_pages, data_size = struct.unpack_from('<III', eh, off); off += 12
    bss_size, = struct.unpack_from('<I', eh, off)

    print("=== ExHeader CodeSetInfo (NLP+) ===")
    print(f"  name      : {name!r}")
    print(f"  text      : addr={text_addr:#010x} size={text_size:#x} pages={text_pages}")
    print(f"  stack     : size={stack_size:#x}")
    print(f"  ro        : addr={ro_addr:#010x} size={ro_size:#x} pages={ro_pages}")
    print(f"  data      : addr={data_addr:#010x} size={data_size:#x} pages={data_pages}")
    print(f"  bss       : size={bss_size:#x}")


if __name__ == '__main__':
    sys.exit(main())
