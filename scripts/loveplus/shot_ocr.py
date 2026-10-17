#!/usr/bin/env python3
"""截图 + 自动 OCR（输入文字专用：上屏回显 + 下屏键盘/候选）。

要点（2026-10-15 用户指明）：
  - **上屏(u,240x400)显示已输入内容，下屏(b,240x320)是键盘/候选**；两个屏像素尺寸不同，
    **禁止用 all 拼接**（拼接后 OCR 坐标全错位）。脚本分别 dump u / b 两张图、分别 OCR，
    各屏坐标各自套换算公式。
  - 脚本全程走标准 MCP 接口（mcp_client → screenshot / ocr），不直连 _send。

命名遵循 skill `loveplus-emu-ops`「截图归档」: /tmp/loveplus_shots/<step>/N_u_描述.jpg + N_b_描述.jpg

用法:
  # 截上下双屏并 OCR，列出全部文字+坐标
  python3 shot_ocr.py --step 03_input --desc now
  # OCR 并直接找候选字/按钮的 touch 坐标（上屏用 --find-u，下屏用 --find-b）
  python3 shot_ocr.py --step 03_input --desc cand --find-b 削除 漢字 虚 --find-u 苗字
"""
import os
import sys
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mcp_client import screenshot, ocr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", default="03_input")
    ap.add_argument("--desc", default="now")
    ap.add_argument("--find-b", nargs="*", default=[], help="下屏文字查找 → 给 touch 坐标")
    ap.add_argument("--find-u", nargs="*", default=[], help="上屏文字查找 → 给 touch 坐标")
    ap.add_argument("--no-shot", action="store_true", help="不重新截屏，用 --img-u/--img-b")
    ap.add_argument("--img-u", default="")
    ap.add_argument("--img-b", default="")
    args = ap.parse_args()

    out_dir = os.path.join("/tmp/loveplus_shots", args.step)
    os.makedirs(out_dir, exist_ok=True)

    # 取序号 N（自动递增）
    ids = [0] + [int(f.split("_", 1)[0]) for f in os.listdir(out_dir)
                 if f.split("_", 1)[0].isdigit()]
    n = max(ids) + 1

    if args.no_shot:
        ub = args.img_u or ""
        bb = args.img_b or ""
    else:
        ub = screenshot(which="top_left", out_dir=out_dir,
                        filename=f"{n}_u_{args.desc}.jpg", fmt="jpg", quality=85)
        bb = screenshot(which="bottom", out_dir=out_dir,
                        filename=f"{n}_b_{args.desc}.jpg", fmt="jpg", quality=85)
        print(f"[{n}] u={ub}\n    b={bb}")

    if args.img_u:
        print("\n===== 上屏 OCR =====")
        print(ocr(img=args.img_u, which="u", find=args.find_u))
    elif not args.no_shot or True:
        print(f"\n===== 上屏 OCR (u) =====")
        print(ocr(which="u", find=args.find_u))

    if args.img_b:
        print("\n===== 下屏 OCR =====")
        print(ocr(img=args.img_b, which="b", find=args.find_b))
    else:
        print(f"\n===== 下屏 OCR (b) =====")
        print(ocr(which="b", find=args.find_b))


if __name__ == "__main__":
    main()
