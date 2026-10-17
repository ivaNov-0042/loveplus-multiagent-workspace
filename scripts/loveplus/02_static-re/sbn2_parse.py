#!/usr/bin/env python3
"""NLP+ SBN2/DBIN2 → SDL2/SOB2 全解密解析（移植 gdkchan/NLPTextTool EncryptedBinary 语义）。

层结构（每层）：
  magic(4, 明文) + Key(u32 LE 存放，= key3B + seed) + 加密区
  XOr 流：out[i] = data[i] ^ (KeyBytes[i%3] + Seed*(i//3))，i 为**本层缓冲区内**位置。
  DBN2: @8 BE u32 nEntries, BE u32 unknown; @0x10 每项 16B BE(u0,u1,off,len)
  SBN2: @8 BE u32 nEntries; @0x10 每项 16B BE(off,len,u0,u1)（以 t050/a000 实测校准）
  内层块（SOB2/SDL2）再各自解一层，Header: magic(4)+Key(4)。

用法: sbn2_full.py <file.dbin2> [--dialogs]
"""
import struct
import sys
from pathlib import Path


def xor_stream(data, key, seed, start=0):
    out = bytearray(data)
    kb = (key & 0xFF, (key >> 8) & 0xFF, (key >> 16) & 0xFF)
    sd = (key >> 24) & 0xFF
    for i in range(start, len(data)):
        out[i] = data[i] ^ ((kb[i % 3] + sd * (i // 3)) & 0xFF)
    return bytes(out)


class R:
    """带解密流位置的读取器（模拟 EncryptedBinary）。"""

    def __init__(self, buf, key):
        self.buf = buf
        self.pos = 0
        self.key = key

    def _dec(self):
        i = self.pos
        kb = (self.key & 0xFF, (self.key >> 8) & 0xFF, (self.key >> 16) & 0xFF)
        sd = (self.key >> 24) & 0xFF
        v = self.buf[i] ^ ((kb[i % 3] + sd * (i // 3)) & 0xFF)
        self.pos += 1
        return v

    def u8(self):
        return self._dec()

    def u16(self):
        a, b = self._dec(), self._dec()
        return a | (b << 8)

    def u16be(self):
        a, b = self._dec(), self._dec()
        return (a << 8) | b

    def u32(self):
        return self.u16() | (self.u16() << 16)

    def u32be(self):
        return (self.u16be() << 16) | self.u16be()

    def utf8(self):
        n = self.u16be()
        raw = bytes(self._dec() for _ in range(n))
        return raw.decode("utf-8", errors="replace")

    def seek(self, p):
        self.pos = p


def parse_container(data):
    """SBN2/DBN2 头 → [(off, size)]；无容器头则整块返回。"""
    magic = data[:4]
    if magic in (b"SBN2", b"DBN2"):
        key = struct.unpack("<I", data[4:8])[0]
        r = R(data, key)
        r.seek(8)
        n = r.u32be()
        if magic == b"DBN2":
            unk = r.u32be()
        # 每项 16B: BE u32 hash0, hash1, off, len（t050/a000 实测；前两值疑为校验）
        items = []
        for i in range(n):
            r.seek(0x10 + i * 0x10)
            h0, h1, off, ln = r.u32be(), r.u32be(), r.u32be(), r.u32be()
            items.append((h0, h1, off, ln))
        return magic, key, items
    return None, None, [(0, 0, 0, len(data))]


def parse_block(data):
    """内层块（SOB2/SDL2）：解密并解析。返回 (magic, key, dict)。"""
    magic = data[:4]
    key = struct.unpack("<I", data[4:8])[0]
    r = R(data, key)
    r.seek(8)
    out = {}
    if magic == b"SDL2":
        t0 = r.u16be()
        nd = r.u16be()
        tables = []
        for i in range(t0):
            sb_off = r.u32be()
            sa_off = r.u32be()
            pos = r.pos
            r.seek(sa_off)
            n = r.u32be()
            vals = [(r.u32be(), r.u32be()) for _ in range(n)]
            r.seek(sb_off)
            v0, v1 = r.u32be(), r.u32be()
            tables.append({"values": vals, "b": (v0, v1)})
            r.seek(pos)
        dialogs = []
        for i in range(nd):
            doff = r.u32be()
            pos = r.pos
            r.seek(doff)
            dialogs.append(r.utf8())
            r.seek(pos)
        out = {"tables": tables, "dialogs": dialogs}
    return magic, key, out


def main():
    src = Path(sys.argv[1])
    data = src.read_bytes()
    magic, key, items = parse_container(data)
    print("%s: container=%s key=%#x entries=%d" % (src.name, magic, key or 0, len(items)))
    for i, it in enumerate(items):
        u0, u1, off, ln = it
        blk = data[off:off + ln]
        bm, bk, info = parse_block(blk)
        print("  [%d] u0=%#x u1=%#x off=%#x len=%#x block=%s key=%#x" % (i, u0, u1, off, ln, bm, bk))
        if isinstance(info, dict) and info.get("dialogs"):
            for j, d in enumerate(info["dialogs"][:6]):
                print("      dlg[%d] %r" % (j, d[:60]))
            print("      ... 共 %d 条" % len(info["dialogs"]))


if __name__ == "__main__":
    main()
