#!/usr/bin/env python3
"""ARM32 模式扫描（直接读 code_text_unpacked.bin，不依赖 r2）。

用途：在 8 MB 的 .text 里快速定位
  - immoffs : 以 imm12 为字段偏移的 LDR/STR（找「谁在读某结构体的某字段」）
  - vfp     : VFP(cp10/cp11) 指令密度直方图（G.722.1 这类 MLT 编解码器是 VFP 重灾区）
  - shift3  : `..., lsl #3` 的索引寻址（找 stride=8 的查表，例如 (off,size) 表消费点）
  - lslk    : 任意常数左移 `mov Rd,Rm,lsl #k` / `add Rd,Rn,Rm,lsl #k` 统计
  - xrefin  : 谁 `bl` 进某区间（按「调用者窗 → 目标窗」聚合）→ 判定模块边界/归属
  - ptrtab  : 池里存着某区间地址的 4 字节字 → 找函数指针表/跳转表（间接调用目标）

坐标：VA = 0x00100000 + 文件偏移。
"""
import argparse
import collections
import struct
import sys

from common_paths import CODE_UNPACKED  # noqa: F403

BASE_VA = 0x00100000


def words(path):
    data = open(path, "rb").read()
    n = len(data) // 4
    return struct.unpack_from("<%dI" % n, data, 0)


def va(off_bytes):
    return BASE_VA + off_bytes


def is_ldrstr_imm(w):
    # cond 01 P U B W L Rn Rt imm12  (I=0, immediate offset)
    if (w >> 26) & 3 != 1:
        return None
    if (w >> 25) & 1:
        return None
    p, u, b, wb, l = (w >> 24) & 1, (w >> 23) & 1, (w >> 22) & 1, (w >> 21) & 1, (w >> 20) & 1
    if (p, u, wb) != (1, 1, 0):
        return None
    op = ("LDR" if l else "STR") + ("B" if b else "")
    return op, (w >> 16) & 0xF, (w >> 12) & 0xF, w & 0xFFF


def is_vfp(w):
    if (w >> 24) & 0xF != 0xE:
        return False
    return (w >> 8) & 0xF in (0xA, 0xB)


def is_reg_shift(w, shift):
    """`op Rd, Rn, Rm, lsl #shift` —— 含 ldr/str 寄存器偏移与 add/mov。"""
    if (w >> 4) & 1:
        return None
    imm5 = (w >> 7) & 0x1F
    typ = (w >> 5) & 3
    if typ != 0 or imm5 != shift:
        return None
    rn, rd, rm = (w >> 16) & 0xF, (w >> 12) & 0xF, w & 0xF
    if (w >> 26) & 3 == 3:
        op = "LDR" if (w >> 20) & 1 else "STR"
        if ((w >> 24) & 1, (w >> 23) & 1, (w >> 21) & 1) != (1, 1, 0):
            return None
        return "%s[Rn,Rm,lsl#%d]" % (op, shift), rn, rd, rm
    if (w >> 25) & 7 == 0 and (w >> 21) & 0xF in (4, 13):  # ADD / MOV
        return ("add" if (w >> 21) & 0xF == 4 else "mov") + "[lsl#%d]" % shift, rn, rd, rm
    return None


def cmd_immoffs(args):
    vals = {int(v, 0) for v in args.vals.split(",")}
    hits = collections.Counter()
    for i, w in enumerate(words(args.bin)):
        r = is_ldrstr_imm(w)
        if not r:
            continue
        op, rn, rt, imm = r
        if imm not in vals:
            continue
        if args.range:
            lo, hi = (int(x, 0) for x in args.range.split("-"))
            if not (lo <= va(i * 4) < hi):
                continue
        hits[(op, imm)] += 1
        if len(hits) <= args.limit:
            print("0x%08x  %-5s r%d, [r%d, #0x%x]" % (va(i * 4), op, rt, rn, imm))
    print("--- 统计 ---")
    for (op, imm), c in sorted(hits.items(), key=lambda x: -x[1]):
        print("  %-5s imm=0x%-5x 命中 %d" % (op, imm, c))


def cmd_vfp(args):
    wins = collections.Counter()
    total = 0
    for i, w in enumerate(words(args.bin)):
        if is_vfp(w):
            wins[(i * 4) // args.window] += 1
            total += 1
    print("VFP(cp10/11) 指令总数 %d，窗口 0x%x" % (total, args.window))
    top = wins.most_common(args.top)
    for wnd, c in top:
        base = wnd * args.window
        print("  0x%08x-0x%08x  %5d 条  密度 %.1f%%"
              % (va(base), va(base + args.window), c, 100.0 * c / (args.window / 4)))


def cmd_shift3(args):
    for i, w in enumerate(words(args.bin)):
        r = is_reg_shift(w, args.shift)
        if not r:
            continue
        op, rn, rd, rm = r
        if args.range:
            lo, hi = (int(x, 0) for x in args.range.split("-"))
            if not (lo <= va(i * 4) < hi):
                continue
        print("0x%08x  %-22s rn=r%d rd=%d rm=r%d" % (va(i * 4), op, rn, rd, rm))


def cmd_prologue(args):
    """找 `push {...,lr}` / `push {lr}` 序幕 → 函数起点候选。"""
    lo = hi = None
    if args.range:
        lo, hi = (int(x, 0) for x in args.range.split("-"))
    n = 0
    for i, w in enumerate(words(args.bin)):
        a = va(i * 4)
        if lo is not None and not (lo <= a < hi):
            continue
        stmdb = (w & 0xFFFF0000) == 0xE92D0000 and (w & 0x4000)
        single = w == 0xE52DE004
        if stmdb or single:
            regs = ""
            if stmdb:
                mask = w & 0xFFFF
                regs = ",".join(["r%d" % b for b in range(16) if mask >> b & 1])
            else:
                regs = "lr"
            print("0x%08x  push {%s}" % (a, regs))
            n += 1
    print("--- 共 %d 个序幕 ---" % n)


def cmd_bl(args):
    """区间内所有 `bl` 的目标聚合（含落在区间外的），用于看模块依赖谁。"""
    lo, hi = _split_range(args.range)
    tgt = collections.Counter()
    inside = 0
    for i, w in enumerate(words(args.bin)):
        a = va(i * 4)
        if not (lo <= a < hi):
            continue
        t = _bl_target(w, a)
        if t is None:
            continue
        tgt[t] += 1
        if lo <= t < hi:
            inside += 1
    print("bl 指令 %d 条，其中目标在区间内 %d 条" % (sum(tgt.values()), inside))
    for t, c in tgt.most_common():
        tag = "内" if lo <= t < hi else "外"
        if args.external_only and lo <= t < hi:
            continue
        print("  [%s] 0x%08x  ×%d" % (tag, t, c))


def cmd_findbl(args):
    """反查谁 `bl` 到目标地址（跨全仓）。"""
    want = int(args.target, 0)
    n = 0
    for i, w in enumerate(words(args.bin)):
        a = va(i * 4)
        if _bl_target(w, a) == want:
            print("0x%08x" % a)
            n += 1
    print("--- 共 %d 处调用 0x%x ---" % (n, want))


def _split_range(s):
    lo, hi = (int(x, 0) for x in s.split("-"))
    return lo, hi


def _bl_target(w, a):
    """若是 BL 指令，返回目标 VA；否则 None。"""
    if (w >> 28) == 0xF or (w >> 24) & 0xF != 0xB:
        return None
    imm = w & 0xFFFFFF
    if imm & 0x800000:
        imm -= 0x1000000
    return a + 8 + imm * 4


def cmd_xrefin(args):
    """谁 `bl` 进这个区间：按 (调用者窗口 → 目标窗口) 聚合。

    用途：判定「某段代码属于谁」。没有调用者、又不在任何函数序幕上的区段，
    往往只能经函数指针表被间接调用（配合 `ptrtab`）。
    """
    lo, hi = _split_range(args.range)
    win = args.window
    edges = collections.defaultdict(list)
    for i, w in enumerate(words(args.bin)):
        a = va(i * 4)
        t = _bl_target(w, a)
        if t is None or not (lo <= t < hi):
            continue
        edges[(a & ~(win - 1), t & ~(win - 1))].append((a, t))
    total = sum(len(v) for v in edges.values())
    print("落入 0x%x-0x%x 的 bl 调用点 %d 个，%d 组(调用者窗→目标窗)，窗口 0x%x"
          % (lo, hi, total, len(edges), win))
    if not total:
        print("  （无 BL 直接调用 → 该区只能经函数指针表/回落路径进入，试 `ptrtab --range`）")
    for (cw, tw), lst in sorted(edges.items()):
        print("  0x%08x → 0x%08x  ×%d   例: 0x%08x→0x%08x" % (cw, tw, len(lst), lst[0][0], lst[0][1]))


def cmd_ptrtab(args):
    """池里存着区间内地址的 4 字节字 → 函数指针表候选（间接调用目标）。"""
    lo, hi = _split_range(args.range)
    win = args.window
    hits = [(va(i * 4), w) for i, w in enumerate(words(args.bin)) if lo <= w < hi]
    grp = collections.defaultdict(list)
    for a, v in hits:
        grp[a & ~(win - 1)].append((a, v))
    print("存有 0x%x-0x%x 地址的 4 字节字 %d 个，位于 %d 个窗口（窗口 0x%x）"
          % (lo, hi, len(hits), len(grp), win))
    for base in sorted(grp):
        lst = grp[base]
        print("  池窗 0x%08x  %d 个" % (base, len(lst)))
        for a, v in (lst if args.all else lst[:args.limit]):
            print("     0x%08x → 0x%08x" % (a, v))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bin", default=CODE_UNPACKED)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("immoffs")
    p.add_argument("--vals", required=True, help="逗号分隔 imm12，如 0x1bc,0x1bd")
    p.add_argument("--range", help="VA 范围 lo-hi（十六进制）")
    p.add_argument("--limit", type=int, default=60)
    p.set_defaults(func=cmd_immoffs)

    p = sub.add_parser("vfp")
    p.add_argument("--window", type=lambda x: int(x, 0), default=0x1000)
    p.add_argument("--top", type=int, default=20)
    p.set_defaults(func=cmd_vfp)

    p = sub.add_parser("shift3")
    p.add_argument("--shift", type=int, default=3)
    p.add_argument("--range")
    p.set_defaults(func=cmd_shift3)

    p = sub.add_parser("findbl")
    p.add_argument("--target", required=True)
    p.set_defaults(func=cmd_findbl)

    p = sub.add_parser("bl")
    p.add_argument("--range", required=True)
    p.add_argument("--external-only", action="store_true")
    p.set_defaults(func=cmd_bl)

    p = sub.add_parser("prologue")
    p.add_argument("--range")
    p.set_defaults(func=cmd_prologue)

    p = sub.add_parser("xrefin")
    p.add_argument("--range", required=True, help="VA 范围 lo-hi（十六进制）")
    p.add_argument("--window", type=lambda x: int(x, 0), default=0x1000)
    p.set_defaults(func=cmd_xrefin)

    p = sub.add_parser("ptrtab")
    p.add_argument("--range", required=True, help="VA 范围 lo-hi（十六进制）")
    p.add_argument("--window", type=lambda x: int(x, 0), default=0x1000)
    p.add_argument("--limit", type=int, default=8)
    p.add_argument("--all", action="store_true")
    p.set_defaults(func=cmd_ptrtab)

    args = ap.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
