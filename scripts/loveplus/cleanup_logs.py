#!/usr/bin/env python3
"""定时清理 azahar(citra) 运行产生的日志，避免磁盘写满。

清理目标（2026-10-16 用户要求"定时清理citra的日志"）：
  - /tmp/emu_live.log              : run_emu.sh 重定向的运行 stdout/stderr
  - /tmp/emu_*.log / /tmp/mcp_*.log: 其它运行期日志
  - ~/.local/share/azahar/**/*.log : azahar 数据目录日志
  - ~/.config/azahar/**/*.log      : azahar 配置目录日志
  - /tmp/az_live_*.ppm 残留        : 截图源（转 jpg 后应删，这里兜底）
  - /tmp/loveplus_shots 最旧步骤    : 截图累积，超阈值时按时间删最旧

行为：
  - 普通日志直接按 mtime 超过 max_age_days(默认7天) 删除；
  - 同时磁盘占用超 threshold_pct(默认90%) 时，无视年龄强制清到阈值以下；
  - 仅删除日志与截图缓存，不碰 ROM/代码/脚本。

用法:
  python3 cleanup_logs.py                 # 用默认阈值清理
  python3 cleanup_logs.py --dry           # 只打印将要删除的，不真正删
  python3 cleanup_logs.py --threshold 85 --age 5
"""
import os
import sys
import glob
import argparse
import shutil

HOME = os.path.expanduser("~")
# azahar / citra 运行与数据日志位置
LOG_TARGETS = [
    "/tmp/emu_live.log",
    "/tmp/emu_*.log",
    "/tmp/mcp_*.log",
    os.path.join(HOME, ".local/share/azahar/**/*.log"),
    os.path.join(HOME, ".local/share/citra/**/*.log"),
    os.path.join(HOME, ".config/azahar/**/*.log"),
    os.path.join(HOME, ".config/citra/**/*.log"),
]
PPM_GLOB = "/tmp/az_live_*.ppm"
SHOTS_DIR = "/tmp/loveplus_shots"


def iter_log_files():
    seen = set()
    for pat in LOG_TARGETS:
        for f in glob.glob(pat, recursive=True):
            if os.path.isfile(f) and f not in seen:
                seen.add(f)
                yield f


def disk_pct():
    try:
        st = shutil.disk_usage("/")
        return int(100.0 * st.used / st.total)
    except Exception:
        return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="只打印，不删除")
    ap.add_argument("--threshold", type=int, default=90,
                    help="磁盘占用超此百分比则强制清到阈值以下（默认90）")
    ap.add_argument("--age", type=int, default=7,
                    help="普通日志按 mtime 超过 N 天删除（默认7）")
    args = ap.parse_args()

    import time
    now = time.time()
    age_sec = args.age * 86400
    removed = []
    kept = []

    # 1) 普通日志：超龄即删
    for f in iter_log_files():
        try:
            if now - os.path.getmtime(f) > age_sec:
                if not args.dry:
                    os.remove(f)
                removed.append(f)
            else:
                kept.append(f)
        except OSError as e:
            kept.append(f"{f} (err {e})")

    # 2) 残留 ppm 兜底删（截图源）
    for f in glob.glob(PPM_GLOB):
        try:
            if not args.dry:
                os.remove(f)
            removed.append(f)
        except OSError:
            pass

    # 3) 磁盘超阈值：清最旧 shots 步骤目录，直到降到阈值或清空
    forced = []
    while disk_pct() >= args.threshold:
        if not os.path.isdir(SHOTS_DIR):
            break
        subs = [
            os.path.join(SHOTS_DIR, d) for d in os.listdir(SHOTS_DIR)
            if os.path.isdir(os.path.join(SHOTS_DIR, d))
        ]
        if not subs:
            break
        subs.sort(key=os.path.getmtime)
        oldest = subs[0]
        if not args.dry:
            shutil.rmtree(oldest)
        forced.append(oldest)

    pct = disk_pct()
    print(f"[{'DRY' if args.dry else 'RUN'}] disk={pct}% threshold={args.threshold}% age>{args.age}d")
    print(f"  logs removed({len(removed)}):")
    for f in removed:
        print("    -", f)
    print(f"  logs kept({len(kept)}):")
    for f in kept:
        print("    =", f)
    if forced:
        print(f"  force-removed shots dirs({len(forced)}):")
        for f in forced:
            print("    -", f)
    print(f"  => disk now {disk_pct()}%")


if __name__ == "__main__":
    main()
