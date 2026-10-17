#!/usr/bin/env python3
"""Siren14 码本 / 帧消耗核验（对 code.bin 内置 G.722.1 实现的静态还原结论做实证）。

两个子命令：

`codebook`（判定性）：游戏 0x75e000 一带的实现用「堆式码树（节点 n 的子节点在
tree[2n]、tree[2n+1]，值 ≤0 为叶，码 = -值）+ 按 mlt_quant 行长整除拆码字」，与
FFmpeg/ITU 的「值即下标、奇数为叶 + 2 的幂掩码」表面不同。本命令枚举所有比特路径，
比较两套码本给出的**分量元组**：若逐路径一致，则二者语义等价（游戏的流 = 标准流）。

`bits`（统计性）：用游戏表逐帧解码，报告
  * 实际用位 vs 理论需求（expected_bits_table 之和）的差；
  * 帧尾剩余 bit 数与其是否全零（编码器未填满时通常留零填充）。
  注意：编码器**不必**把 368 bit 填满，故「精确闭合」不是有效判据（实测留 0~20 bit）。

用法：
  .venv/bin/python scripts/loveplus/siren14_framecheck.py codebook
  .venv/bin/python scripts/loveplus/siren14_framecheck.py bits --voice 0 --convention game
"""
import argparse
import struct
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_paths import REPO, CODE_UNPACKED  # noqa: E402

AUDIO = Path(REPO) / "data/loveplus/nlp_plus/audio"
INDEX_BIN = AUDIO / "Siren14voice.bin"
SPP = AUDIO / "Siren14Voice.spp"

# code_text_unpacked.bin：VA = 0x00100000 + 偏移；表地址见 memory/loveplus/reverse_code_bin.md §5d/§5e
VA_BASE = 0x00100000
A_STD_DEV = 0x801d34     # i32 Q0 ×54：round(2^((i-24)/2))，索引 i = arp+24（arp 上限 +29）
A_VDIM = 0x801e34        # i32[8]：每码字维数
A_ROWLEN_M1 = 0x801e54   # i32[8]：mlt_quant 行长-1
A_NVEC = 0x801e94        # i32[8]：每区域码字数
A_DIFF = 0x8bbb38        # i32[28][23][2]：差分码树；行 i 对应区域 i，行 0 为占位全零
A_MLT = 0x8bcf58         # i32 Q12 [7][16]：量化电平（行距 16 i32）
A_EXP_BITS = 0x8bd118    # i32[8]：expected_bits_table
DEC_TREES = [0x8bd138, 0x8bd6d8, 0x8bd9c0, 0x8bdb38, 0x8beb70, 0x8bf1f0, 0x8bf7e8]
TREE_ENDS = [0x8bd6d8, 0x8bd9c0, 0x8bdb38, 0x8beb70, 0x8bf1f0, 0x8bf7e8, 0x8bf8e0]
DIFF_ROW_STRIDE = 0xb8   # 23 对
FRAME_SIZE = 46          # 字节/帧（实测）
FRAME_BITS = FRAME_SIZE * 8
ESF_ADJUSTMENT = 7
NREGIONS = 28            # dpb[1]=1 → 7000<<1=14000 → 28 region / 640 样本 / 32 kHz
RATE_CONTROL_BITS = 5    # 28 region 支 5 bit（14 region 支 4 bit）
RATE_CONTROL_POSS = 32   # 对应 32 种可能（14 region 支为 16）


def load_game_tables(bin_path=CODE_UNPACKED):
    data = Path(bin_path).read_bytes()

    def rd(va, n):
        return list(struct.unpack_from("<%di" % n, data, va - VA_BASE))

    return {
        "std_dev": rd(A_STD_DEV, 54),
        "vdim": rd(A_VDIM, 8),
        "rowlen": [x + 1 for x in rd(A_ROWLEN_M1, 8)],
        "nvec": rd(A_NVEC, 8),
        "mlt": [rd(A_MLT + c * 64, 16) for c in range(7)],
        "exp_bits": rd(A_EXP_BITS, 8),
        "diff": [rd(A_DIFF + i * DIFF_ROW_STRIDE, 46) for i in range(NREGIONS)],
        "tree": [rd(a, (e - a) // 4) for a, e in zip(DEC_TREES, TREE_ENDS)],
    }


def load_ffmpeg_tables():
    import siren_tables as st
    return {
        "exp_bits": list(st.EXPECTED_BITS_TABLE),
        "vdim": list(st.VECTOR_DIMENSION),
        "nvec": list(st.NUMBER_OF_VECTORS),
        "idx_table": list(st.INDEX_TABLE),
        "trees": [list(t) for t in st.DECODER_TREES],
        "mlt": [list(r) for r in st.MLT_QUANT],
    }


class BitReader:
    """16 位小端字、字内 MSB-first，与游戏 0x75e0c0 的读位循环同构。"""

    def __init__(self, data, nbits):
        self.d = data
        self.left = nbits
        self.word = 0
        self.bitpos = -1
        self.read = 0

    def bit(self):
        if self.left <= 0:
            raise EOFError("out of bits")
        if self.bitpos < 0:
            i = (self.read // 16) * 2
            self.word = self.d[i] | (self.d[i + 1] << 8)
            self.bitpos = 15
        b = (self.word >> self.bitpos) & 1
        self.bitpos -= 1
        self.read += 1
        self.left -= 1
        return b

    def bits(self, n):
        v = 0
        for _ in range(n):
            v = (v << 1) | self.bit()
        return v


def clip_u3(i):
    return 0 if i < 0 else (7 if i > 7 else i)


def decode_envelope(br, t, nregions):
    """游戏约定：叶值 ≤0，功率增量 = -叶值（FFmpeg 直接使用叶值，等价）。"""
    arp = [0] * nregions
    arp[0] = br.bits(5) - ESF_ADJUSTMENT
    for i in range(1, nregions):
        idx = 0
        while True:
            idx = t["diff"][i][idx * 2 + br.bit()]
            if idx <= 0:
                break
        arp[i] = arp[i - 1] - idx - 12
    return arp


def categorize(t, nregions, available, arp, n_rc):
    """二分阈值 + min/max 调整，与 FFmpeg categorize_regions 同构（可能性数参数化）。

    含游戏特有的「可用位数上限」：cap = 320·(nregions/14)，超出部分按 5/8 压缩。
    """
    exp = t["exp_bits"]
    cap = 320 * (nregions // 14)
    if available > cap:
        available = cap + ((available - cap) * 5 >> 3)
    offset, delta, cats = -32, 32, [0] * nregions
    while delta > 0:
        expected = 0
        for r in range(nregions):
            i = clip_u3((delta + offset - arp[r]) >> 1)
            cats[r] = i
            expected += exp[i]
        if expected >= available - 32:
            offset += delta
        delta //= 2
    expected = 0
    maxc = [0] * nregions
    for r in range(nregions):
        i = clip_u3((offset - arp[r]) >> 1)
        maxc[r] = cats[r] = i
        expected += exp[i]
    minc = list(maxc)
    mn = mx = expected
    tmp = [0] * (2 * n_rc)
    min_ptr = max_ptr = n_rc
    for _ in range(n_rc - 1):
        if mn + mx > available * 2:
            raw, idx = -99, 0
            for r in range(nregions - 1, -1, -1):
                if minc[r] < 7:
                    v = offset - arp[r] - 2 * minc[r]
                    if v > raw:
                        raw, idx = v, r
            if raw == -99:
                raise ValueError("no min candidate")
            tmp[min_ptr] = idx
            min_ptr += 1
            mn += exp[minc[idx] + 1] - exp[minc[idx]]
            minc[idx] += 1
        else:
            raw, idx = 99, 0
            for r in range(nregions):
                if maxc[r] > 0:
                    v = offset - arp[r] - 2 * maxc[r]
                    if v < raw:
                        raw, idx = v, r
            if raw == 99:
                raise ValueError("no max candidate")
            max_ptr -= 1
            tmp[max_ptr] = idx
            mx += exp[maxc[idx] - 1] - exp[maxc[idx]]
            maxc[idx] -= 1
    for r in range(nregions):
        cats[r] = maxc[r]
    return cats, tmp[max_ptr:max_ptr + n_rc - 1], offset


def apply_rate_control(cats, balance, rate_control):
    """游戏 0x75e69c：跳过已为 7 的区域，最多走 len(balance) 步。"""
    i = 0
    while rate_control > 0 and i < len(balance):
        r = balance[i]
        i += 1
        if 0 <= r < len(cats) and cats[r] < 7:
            rate_control -= 1
            cats[r] += 1
    return cats


def count_region_bits_game(br, t, cat):
    """游戏约定：堆式树 + 按行长整除（按码字分别计符号位）。"""
    bits = 0
    if cat < 7:
        tree, dim, d = t["tree"][cat], t["vdim"][cat], t["rowlen"][cat]
        for _ in range(t["nvec"][cat]):
            idx = 0
            while True:
                idx = tree[idx * 2 + br.bit()]
                bits += 1
                if idx <= 0:
                    break
            c, nz = -idx, 0
            for _j in range(dim):
                if c % d:
                    nz += 1
                c //= d
            for _ in range(nz):
                br.bit()
                bits += 1
    return bits


def count_region_bits_ffmpeg(br, cat, ff):
    """FFmpeg 约定：值即下标、奇数为叶 + 2 的幂掩码。"""
    bits = 0
    if cat < 7:
        tree, nel = ff["trees"][cat], len(ff["trees"][cat])
        for _ in range(ff["nvec"][cat]):
            idx = 0
            while True:
                b = br.bit()
                bits += 1
                if idx + b >= nel:
                    raise ValueError("tree overflow")
                idx = tree[idx + b]
                if idx & 1:
                    break
            idx >>= 1
            for _j in range(ff["vdim"][cat]):
                dv = idx & ((1 << ff["idx_table"][cat]) - 1)
                idx >>= ff["idx_table"][cat]
                if dv:
                    br.bit()
                    bits += 1
    return bits


def decode_frame_bits(frame, t, ff, convention):
    """返回 (用位, 理论需求, 帧尾剩余位, 尾部保留串, 类别表)。"""
    if len(frame) < FRAME_SIZE:
        raise ValueError("短帧")
    br = BitReader(frame[:FRAME_SIZE], FRAME_BITS)
    arp = decode_envelope(br, t, NREGIONS)
    rate_control = br.bits(RATE_CONTROL_BITS)
    cats, balance, _ = categorize(t, NREGIONS, br.left, arp, RATE_CONTROL_POSS)
    cats = apply_rate_control(cats, balance, rate_control)
    need = sum(t["exp_bits"][c] for c in cats)
    for r in range(NREGIONS):
        if convention == "game":
            count_region_bits_game(br, t, cats[r])
        else:
            count_region_bits_ffmpeg(br, cats[r], ff)
    used = FRAME_BITS - br.left
    tail = "".join(str(br.bit()) for _ in range(br.left))
    return used, need, len(tail), tail, cats


def load_frames(voice_id, nframes):
    off, size = struct.unpack_from("<ii", INDEX_BIN.read_bytes(), voice_id * 8)
    with open(SPP, "rb") as f:
        f.seek(off)
        raw = f.read(size)
    total = size // FRAME_SIZE
    n = total if nframes <= 0 else min(nframes, total)
    return off, size, total, [raw[i * FRAME_SIZE:(i + 1) * FRAME_SIZE] for i in range(n)]


def enum_ffmpeg_tuples(ff, cat):
    it, dim, tree, out = ff["idx_table"][cat], ff["vdim"][cat], ff["trees"][cat], {}

    def rec(n, path):
        for b in (0, 1):
            v = tree[n + b]
            if v & 1:
                code = v >> 1
                out[path + (b,)] = tuple((code >> (j * it)) & ((1 << it) - 1) for j in range(dim))
            else:
                rec(v, path + (b,))
    rec(0, ())
    return out


def enum_game_tuples(t, cat):
    tree, d, dim, out = t["tree"][cat], t["rowlen"][cat], t["vdim"][cat], {}

    def rec(n, path, depth=0):
        if depth > 40:
            raise RuntimeError("码树成环")
        for b in (0, 1):
            v = tree[n * 2 + b]
            if v <= 0:
                c, dig = -v, []
                for _j in range(dim):
                    dig.append(c % d)
                    c //= d
                # 游戏把 digit0 写在输出数组末位（str [r1],#-4）
                out[path + (b,)] = tuple(dig[dim - 1 - j] for j in range(dim))
            else:
                rec(v, path + (b,), depth + 1)
    rec(0, ())
    return out


def cmd_codebook(_args):
    t, ff = load_game_tables(), load_ffmpeg_tables()
    print("按比特路径比较两套码本给出的分量元组（一致 ⇒ 语义等价，游戏流 = 标准流）")
    all_ok = True
    for cat in range(7):
        a, b = enum_ffmpeg_tuples(ff, cat), enum_game_tuples(t, cat)
        keys = set(a) | set(b)
        same = sum(1 for k in keys if a.get(k) == b.get(k))
        all_ok &= same == len(keys)
        print("  cat%d: 路径 %d/%d，元组一致 %d/%d%s"
              % (cat, len(a), len(b), same, len(keys), "" if same == len(keys) else "  ← 不一致"))
    # mlt_quant：游戏 Q12 定点 vs FFmpeg float
    print("mlt_quant 定点/浮点比对：")
    for cat in range(7):
        g = t["mlt"][cat]
        fv = ff["mlt"][cat]
        dev = [round(g[i] / 4096.0 - fv[i], 4) for i in range(len(fv))]
        print("  cat%d: 最大偏差 %.4f" % (cat, max(abs(x) for x in dev)))
    return 0 if all_ok else 1


def cmd_bits(args):
    t, ff = load_game_tables(), load_ffmpeg_tables()
    off, size, total, frames = load_frames(args.voice, args.frames)
    print("voice %d: off=%d size=%d 共 %d 帧（本次 %d 帧），帧长 %d B"
          % (args.voice, off, size, total, len(frames), FRAME_SIZE))
    for conv in (["game", "ffmpeg"] if args.convention == "both" else [args.convention]):
        slack, tails, tails_zero, errs = Counter(), Counter(), 0, 0
        for fr in frames:
            try:
                used, need, left, tail, _cats = decode_frame_bits(fr, t, ff, conv)
            except (EOFError, ValueError) as e:
                errs += 1
                if args.verbose:
                    print("   [%s] 异常：%s" % (conv, e))
                continue
            slack[FRAME_BITS - used] += 1
            tails[len(tail)] += 1
            tails_zero += all(c == "0" for c in tail)
        n = len(frames) - errs
        print("  约定 %-6s 成功 %d/%d（异常 %d）；用位 = 368 − k 的分布 %s"
              % (conv, n, len(frames), errs, dict(sorted(slack.items())[:8])))
        print("              帧尾剩余位数分布 %s；其中全零 %d/%d"
              % (dict(sorted(tails.items())), tails_zero, n))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("codebook", help="两套码本的语义等价性判定")
    p1.set_defaults(func=cmd_codebook)
    p2 = sub.add_parser("bits", help="逐帧位消耗统计")
    p2.add_argument("--voice", type=int, default=0)
    p2.add_argument("--frames", type=int, default=0, help="0=全部")
    p2.add_argument("--convention", choices=["game", "ffmpeg", "both"], default="both")
    p2.add_argument("--verbose", action="store_true")
    p2.set_defaults(func=cmd_bits)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
