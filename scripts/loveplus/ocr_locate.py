#!/usr/bin/env python3
"""RapidOCR 定点识别：截图 → 文字+坐标 → 按 touch 坐标输出（点选专用）。

用途：替代肉眼估坐标。比如要点「削除」按钮或候选字「虚」，
直接查它的 dump 坐标 → 换算 touch = (1-y/320, x/240)。

依赖: rapidocr-onnxruntime（~15MB，本地 CPU，无 paddle 框架）

用法:
  # 识别指定图（u=上屏240x400 / b=下屏240x320 / all=拼接240x720）
  python3 ocr_locate.py --img /tmp/loveplus_shots/xx/1_b_xxx.jpg

  # 截当前下屏并识别（配合步骤目录存图）
  python3 ocr_locate.py --step 03_input --desc now --which b

  # 截当前上下屏并识别，按文字找点（如找「削除」和「虚」）
  python3 ocr_locate.py --step 03_input --desc now --which all --find 削除 虚
"""
import os
import sys
import time
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import loveplus_mcp as M
from PIL import Image

_ocr = None


def get_ocr():
    global _ocr
    if _ocr is None:
        from rapidocr_onnxruntime import RapidOCR
        _ocr = RapidOCR()
    return _ocr


def latest(suf):
    import glob
    fs = sorted(glob.glob(f"/tmp/az_live_*_{suf}.ppm"), key=os.path.getmtime, reverse=True)
    return fs[0] if fs else None


def ocr_arr(img, tag):
    res, _ = get_ocr()(img)
    out = []
    if not res:
        return out
    for box, text, conf in res:
        x = int(min(p[0] for p in box)); y = int(min(p[1] for p in box))
        w = int(max(p[0] for p in box) - x); h = int(max(p[1] for p in box) - y)
        out.append({"tag": tag, "text": text, "conf": float(conf),
                    "dump": (x, y, w, h)})
    return out


def run(which, step=None, desc="ocr", find=None):
    """识别 which='u'/'b'/'all'，输出坐标表；find 给文字子串过滤（返回 touch 坐标）。"""
    M._send("dump", timeout=5.0)
    time.sleep(0.35)
    results = []
    if which in ("u", "all"):
        p = latest("top_left")
        results += ocr_arr(Image.open(p).convert("RGB"), "u")
    if which in ("b", "all"):
        p = latest("bottom")
        results += ocr_arr(Image.open(p).convert("RGB"), "b")

    # 落盘
    if step:
        d = f"/tmp/loveplus_shots/{step}"
        os.makedirs(d, exist_ok=True)
        import glob as _g
        ids = [0] + [int(f.split("_", 1)[0]) for f in os.listdir(d)
                     if f.split("_", 1)[0].isdigit()]
        idx = max(ids) + 1
        if which in ("u", "all"):
            Image.open(latest("top_left")).convert("RGB").save(f"{d}/{idx}_u_{desc}.jpg", quality=85)
        if which in ("b", "all"):
            Image.open(latest("bottom")).convert("RGB").save(f"{d}/{idx}_b_{desc}.jpg", quality=85)

    print(f"{'屏':<3} {'dump(x,y)':<12} {'conf':<5} 文字")
    for r in results:
        x, y, w, h = r["dump"]
        print(f"{r['tag']:<3} ({x:3d},{y:3d}) {w}x{h}  {r['conf']:.2f}  {r['text']}")

    if find:
        print("\n--- 命中查询（touch = (1-y/320, x/240)，中心点）---")
        for q in find:
            hits = [r for r in results if q in r["text"]]
            if not hits:
                print(f"  '{q}': 未找到")
                continue
            for r in hits:
                x, y, w, h = r["dump"]
                cx, cy = x + w / 2, y + h / 2
                tx, ty = 1 - cy / 320, cx / 240
                print(f"  '{q}': {r['tag']}屏 dump({cx:.0f},{cy:.0f}) conf={r['conf']:.2f}"
                      f" -> touch({tx:.3f},{ty:.3f})  文字='{r['text']}'")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--img", help="识别已有图片（b=下屏内容 或 all 拼接图）")
    ap.add_argument("--step", help="步骤目录（顺带落盘截图）")
    ap.add_argument("--desc", default="ocr")
    ap.add_argument("--which", choices=["u", "b", "all"], default="b")
    ap.add_argument("--find", nargs="*", help="按文字查询并输出 touch 坐标")
    args = ap.parse_args()

    if args.img:
        res = ocr_arr(Image.open(args.img).convert("RGB"), "img")
        print(f"{'屏':<3} {'dump(x,y)':<12} {'conf':<5} 文字")
        for r in res:
            x, y, w, h = r["dump"]
            print(f"{r['tag']:<3} ({x:3d},{y:3d}) {w}x{h}  {r['conf']:.2f}  {r['text']}")
        if args.find:
            print("\n--- 命中查询 ---")
            for q in args.find:
                hits = [r for r in res if q in r["text"]]
                for r in hits:
                    x, y, w, h = r["dump"]
                    cx, cy = x + w / 2, y + h / 2
                    tag_y = 0 if r["tag"] == "u" else 0  # img 模式下拼接图需人工减 400
                    print(f"  '{q}': dump({cx:.0f},{cy:.0f}) conf={r['conf']:.2f}"
                          f" 文字='{r['text']}'")
        return

    run(args.which, args.step, args.desc, args.find)


if __name__ == "__main__":
    main()
