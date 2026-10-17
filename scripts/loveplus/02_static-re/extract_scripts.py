#!/usr/bin/env python3
"""提取 NLP+ 卡带里全部非脚本的其它大文件（bcsar/bcstm/csidbin/spp/dpb 等）。

与 romfs_extract.py 同一张文件表（0x45E000 起），但这里不做 SBN2 校验，
凡是 (offset+DELTA) 处能读出 size 字节的就直接落盘，供后续逐类分析。

用法：
    .venv/bin/python extract_scripts.py [输出目录] [--all]
默认输出 data/loveplus/nlp_plus/romfs_misc/；--all 时连脚本一起提。
"""
import os
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ROM = os.environ.get("NLP_PLUS_ROM", str(REPO / "data/loveplus/roms_patched/NLP_plus_patched.3ds"))
OUT = Path(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-")
           else REPO / "data/loveplus/nlp_plus/romfs_misc")
DELTA = 0x496F80
LO, HI = 0x45E000, 0x800000


def scan(f):
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
                    if 0 < size < 0x8000000:
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
    ok = 0
    for nm, off, size in items:
        if not nm.endswith(".dbin2") and "all" not in sys.argv:
            continue
        f.seek(off + DELTA)
        data = f.read(size)
        (OUT / nm).write_bytes(data)
        ok += 1
    print("提取完成: %d → %s" % (ok, OUT))


if __name__ == "__main__":
    main()
