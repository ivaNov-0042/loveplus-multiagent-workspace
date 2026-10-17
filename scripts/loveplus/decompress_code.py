#!/usr/bin/env python3
"""解压 3DS ExeFS 的 LZSS 压缩 code.bin（算法照搬 citra ncch_container.cpp）。

LZSS_GetDecompressedSize: size = u32@(end-4) + file_size
LZSS_Decompress: 从尾部向前解码（3DS ExeFS 特有方向）。

用法: decompress_code.py <in_code.bin> <out_text.bin>
"""
import struct
import sys


def decompressed_size(buf: bytes) -> int:
    if len(buf) < 4:
        return len(buf)
    (offset_size,) = struct.unpack_from('<I', buf, len(buf) - 4)
    return offset_size + len(buf)


def lzss_decompress(compressed: bytes, out_size: int) -> bytes:
    if len(compressed) < 8 or out_size < len(compressed):
        raise ValueError("bad sizes")
    cs = len(compressed)
    (footer_top,) = struct.unpack_from('<I', compressed, cs - 8)
    top = (footer_top >> 24) & 0xFF
    bottom = footer_top & 0xFFFFFF
    if top > cs or bottom > cs:
        raise ValueError("footer out of range")

    out = bytearray(out_size)
    # memcpy(decompressed, compressed, compressed.size)
    out[:cs] = compressed[:cs]

    o = out_size            # 输出指针(从尾部向前)
    index = cs - top        # 输入读取位置
    stop_index = cs - bottom

    while index > stop_index:
        index -= 1
        control = compressed[index]
        for _ in range(8):
            if index <= stop_index or index <= 0 or o <= 0:
                break
            if control & 0x80:
                index -= 2
                segment_offset = compressed[index] | (compressed[index + 1] << 8)
                segment_size = ((segment_offset >> 12) & 15) + 3
                segment_offset = (segment_offset & 0x0FFF) + 2
                for _j in range(segment_size):
                    data = out[o + segment_offset]
                    o -= 1
                    out[o] = data
            else:
                index -= 1
                o -= 1
                out[o] = compressed[index]
            control = (control << 1) & 0xFF
    return bytes(out)


def main():
    src, dst = sys.argv[1], sys.argv[2]
    buf = open(src, 'rb').read()
    size = decompressed_size(buf)
    print(f"compressed={len(buf):#x} decompressed={size:#x}")
    text = lzss_decompress(buf, size)
    open(dst, 'wb').write(text)
    print(f"wrote {dst}: {len(text)} bytes")


if __name__ == '__main__':
    main()
