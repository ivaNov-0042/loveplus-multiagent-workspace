#!/usr/bin/env python3
"""从 NLP+ 卡带 (.3ds) 里按文件表提取文件到目录（自足实现，无第三方依赖）。

实测发现（2026-10-17，02_static-re）——这张 patched 卡带的布局不是标准 3DS RomFS：
- NCSD 头在文件偏移 0x100（不是 0），分区 0（主程序 NCCH）在 0x2E40400*0x200 处但已加密。
- 全文件只有一个 IVFC 头 @0x45E000（ RomFS 明文区），其 level1/2/3 结构与标准不符；
  但 0x4776xx 起是明文的「文件项表」：每项 = [0xffffffff, u32 nameBytes, UTF16 名,
  u32 id, u32 flags, u32 offset, 0, u32 size, 0]。
- 表里 offset 是虚拟地址；明文内容 = offset + 0x496F80（对脚本/Siren14 系列实测一致）。
- 明文锚点：Siren14voice.bin @0x2C7B3BF0、dpb {23,1,1,16} @0x2C868B70。

用法：
    .venv/bin/python romfs_extract.py [输出目录]
默认输出 data/loveplus/nlp_plus/script/，只提取 "SBN2" 开头的脚本文件。
"""
import os
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ROM = os.environ.get("NLP_PLUS_ROM", str(REPO / "data/loveplus/roms_patched/NLP_plus_patched.3ds"))
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else REPO / "data/loveplus/nlp_plus/script")
DELTA = 0x496F80
LO, HI = 0x45E000, 0x800000


def scan(f):
    """扫文件表，返回 [(name, off, size)]。"""
    f.seek(LO)
    b = f.read(HI - LO)
    items = []
    i = 0
    while True:
        i = b.find(b"\xff\xff\xff\xff", i)
        if i < 0:
            break
        ln = struct.unpack_from("<I", b, i + 4)[0]
        if 2 <= ln <= 0x40 and ln % 2 == 0 and i + 8 + ln + 0x18 <= len(b):
            try:
                nm = b[i + 8:i + 8 + ln].decode("utf-16-le")
                if nm.isprintable():
                    off, _, size, _ = struct.unpack_from("<IIII", b, i + 8 + ln + 8)
                    if size < 0x8000000:
                        items.append((nm, off, size))
                    i += 8 + ln
                    continue
            except UnicodeDecodeError:
                pass
        i += 4
    return items


def main():
    f = open(ROM, "rb")
    items = scan(f)
    print("文件项 %d 个" % len(items))
    OUT.mkdir(parents=True, exist_ok=True)
    ok = bad = 0
    for nm, off, size in items:
        f.seek(off + DELTA)
        data = f.read(size)
        if data[:4] != b"SBN2":
            # 逐文件头部另有 0x10-0x50 不等的 hash 块，试 ±0x10 对齐档
            got = None
            for d in (DELTA - 0x10, DELTA + 0x10):
                f.seek(off + d)
                d2 = f.read(size)
                if d2[:4] == b"SBN2":
                    data, got = d2, d
                    break
            if got is None:
                bad += 1
                continue
        (OUT / nm).write_bytes(data)
        ok += 1
    print("提取完成: %d 成功 %d 失败 → %s" % (ok, bad, OUT))


if __name__ == "__main__":
    main()
