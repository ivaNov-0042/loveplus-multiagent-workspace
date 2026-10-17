#!/usr/bin/env python3
"""解析 NLP+ 的 .sbin2（PAK 归档）内层子文件，提取叶子节点并扫描日文文本/语音id。

用法: .venv/bin/python sbin2_pak_parse.py [sbin2路径] [--dump DIR]
"""
import struct, sys, os, re

def find_all(buf, pat):
    res = []
    i = buf.find(pat)
    while i >= 0:
        res.append(i)
        i = buf.find(pat, i+1)
    return res

def u16le(b, o): return struct.unpack_from("<H", b, o)[0]
def u32le(b, o): return struct.unpack_from("<I", b, o)[0]

def parse_pak(buf, base=0, depth=0, out=None):
    """递归解析 PAK 结构。PAK 标记 = b'PAK '。"""
    if out is None: out = []
    # 在 buf 里找所有 'PAK ' 标记
    marks = find_all(buf, b"PAK ")
    seen = set()
    for m in marks:
        if m in seen: continue
        seen.add(m)
        # 标记后结构未知，先记录上下文
        ctx = buf[m:m+0x20]
        out.append((base+m, ctx[:0x20].hex(), depth))
    return out

def scan_text(buf):
    """扫描 UTF-16LE 日文 与 Shift-JIS 日文 片段。"""
    hits = []
    # UTF-16LE: 连续 hiragana/katakana/kanji
    i = 0
    run = 0
    best = []
    while i+2 <= len(buf):
        w = u16le(buf, i)
        if (0x3040<=w<=0x309f) or (0x30a0<=w<=0x30ff) or (0x4e00<=w<=0x9fff):
            run += 1
            if run>=3:
                best.append(i-run*2)
        else:
            run = 0
        i += 2
    for s in best[:10]:
        # 抽取一段 utf-16le 文本
        txt = buf[s:s+0x40].decode("utf-16-le", errors="ignore")
        hits.append(("utf16", s, txt[:30]))
    # Shift-JIS: 双字节 0x81-0x9f / 0xe0-0xfc lead
    sj = re.findall(rb"[\x81-\x9f\xe0-\xfc][\x40-\xfc]", buf)
    if sj:
        hits.append(("sjis_pairs", len(sj), ""))
    return hits

def main():
    path = sys.argv[1] if len(sys.argv)>1 else "data/loveplus/nlp_plus/sbin2/a000.sbin2"
    buf = open(path,"rb").read()
    print("file=%s size=%d" % (path, len(buf)))
    print("\n-- 'PAK ' markers (前 30 个, 带上下文) --")
    marks = find_all(buf, b"PAK ")
    print("PAK marker count =", len(marks))
    for m in marks[:30]:
        print("  @%#08x: %s" % (m, buf[m:m+0x18].hex()))
    print("\n-- 文本扫描 --")
    hits = scan_text(buf)
    for h in hits:
        print("  ", h)

if __name__ == "__main__":
    main()
