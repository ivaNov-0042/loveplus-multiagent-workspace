#!/usr/bin/env python3
"""双屏截图脚本：一次触摸 + 同时抓上屏(u)/下屏(b)，按命名规范归档。

用途：输入文字（键盘在下屏、已输入内容显示在上屏）时，必须同时看两屏，
脚本输出 u 图 + b 图到当前步骤目录，命名 `<id>_u|b_描述.jpg`。

帧语义：headless 每帧 = 一次 RunLoop，60fps → 1 帧 ≈ 16.67ms。
长按时长用帧数描述（hold_frames=90 ≈ 1.5s）。

用法:
  # 1) 只截图（当前画面）
  python3 shot_ub.py --step 02_profile --desc input_board

  # 2) 触摸 + 截图（按下态 / 放开态都截）
  python3 shot_ub.py --step 02_profile --desc kanji_ki \
      --touch 0.753 0.254 --hold 90 --also-release

  # 3) 连续多个点（自动递增 id）
  python3 shot_ub.py --step 02_profile --desc type_kana \
      --touch 0.688 0.358 --hold 60 --touch 0.497 0.254 --hold 60
输出: /tmp/<项目>_shots/<step>/NN_u_描述.jpg + NN_b_描述.jpg
id 在步骤目录内自动递增（扫描已有最大 id）。
"""
import os
import sys
import glob
import time
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import loveplus_mcp as M


def shots_dir(step, root="/tmp/loveplus_shots"):
    d = os.path.join(root, step)
    os.makedirs(d, exist_ok=True)
    return d


def next_id(d):
    """扫描目录里已有 `NN_*` 取最大 id，返回下一个。"""
    mx = 0
    for f in os.listdir(d):
        if len(f) >= 2 and f[:2].isdigit() and f[2:3] == "_":
            mx = max(mx, int(f[:2]))
    return mx + 1


def wait_frames(n):
    """等 n 帧推进（轮询 frame 命令）。"""
    try:
        f0 = int(M._send("frame", timeout=5.0).split()[-1])
    except Exception:
        time.sleep(max(0.1, n / 60.0))
        return
    t0 = time.time()
    while time.time() - t0 < 15:
        try:
            f = int(M._send("frame", timeout=2.0).split()[-1])
            if f >= f0 + n:
                return
        except Exception:
            pass
        time.sleep(0.15)


def capture(d, nid, desc):
    """抓上屏+下屏，存 <nid>_u_desc.jpg / <nid>_b_desc.jpg，返回两路径。"""
    u = os.path.join(d, f"{nid:02d}_u_{desc}.jpg")
    b = os.path.join(d, f"{nid:02d}_b_{desc}.jpg")
    M.screenshot(which="top", out_dir=d, filename=f"{nid:02d}_u_{desc}.jpg",
                 fmt="jpg", quality=80)
    M.screenshot(which="bottom", out_dir=d, filename=f"{nid:02d}_b_{desc}.jpg",
                 fmt="jpg", quality=80)
    return u, b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", required=True, help="步骤目录名，如 02_profile")
    ap.add_argument("--desc", default="shot", help="描述词（无空格）")
    ap.add_argument("--root", default="/tmp/loveplus_shots")
    ap.add_argument("--touch", nargs=2, type=float, metavar=("X", "Y"),
                    help="按下触摸坐标 (x y)")
    ap.add_argument("--hold", type=int, default=90, help="按住帧数 (≈1.5s)")
    ap.add_argument("--also-release", action="store_true",
                    help="松开后再截一组（释放态）")
    args = ap.parse_args()

    d = shots_dir(args.step, args.root)
    nid = next_id(d)

    if args.touch:
        x, y = args.touch
        # 按下态
        M.touch(x, y)
        wait_frames(args.hold)
        capture(d, nid, f"{args.desc}_press")
        if args.also_release:
            M.release()
            wait_frames(45)
            capture(d, nid + 1, f"{args.desc}_release")
            nid += 1
        else:
            M.release()
            wait_frames(10)
        wait_frames(30)
    else:
        wait_frames(5)
        capture(d, nid, args.desc)

    # 打印本步骤目录最新文件，便于 read
    for f in sorted(glob.glob(os.path.join(d, f"{nid:02d}_*.jpg"))):
        print(f)


if __name__ == "__main__":
    main()
