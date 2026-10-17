#!/usr/bin/env python3
"""交互网格自动识别 + 切块。

对模拟器 dump 的下屏 PPM(240x320) 做横向/纵向投影，找按钮/键位的行/列边界
（dark 像素密度跳变），切成小格，每块存一张 PNG，文件名后缀标注其在 dump 图中的
起止坐标，便于后续触摸坐标换算 touch=(1-y/320, x/240)。

用法:
  python3 grid_detect.py [--src <ppm或png>] [--out <dir>] [--th 阈值]
  不带 --src 时自动取最新一张 /tmp/az_live_*_bottom.ppm。
  也可作为库:  from grid_detect import detect_grid, crop_cells
"""
import os
import sys
import glob
import argparse
import numpy as np
from collections import defaultdict

try:
    from PIL import Image
except ImportError:
    Image = None


def latest_bottom():
    fs = sorted(glob.glob("/tmp/az_live_*_bottom.ppm"), key=os.path.getmtime, reverse=True)
    return fs[0] if fs else None


def _load(path):
    if Image is None:
        raise SystemExit("Pillow 未安装")
    return Image.open(path).convert("L")


def _project(img, axis):
    """axis=0 每列 dark 像素数; axis=1 每行 dark 像素数。numpy 向量化。"""
    a = np.asarray(img)
    if axis == 0:
        return (a < 128).sum(axis=1)  # 每列(长度=宽)
    else:
        return (a < 128).sum(axis=0)  # 每行(长度=高)


def _edges(proj, min_gap=4, min_strength=2):
    """在投影数组里找显著跳变的段，返回 [(start,end),...]。

    dark 像素数 > min_strength 视为有内容(按钮笔画/边框)，连续非零段即一格的行/列区间。
    """
    proj = np.asarray(proj, dtype=int)
    active = (proj > min_strength).astype(np.int8)
    edges = []
    i = 0
    n = len(active)
    while i < n:
        if active[i]:
            j = i
            while j < n and active[j]:
                j += 1
            if j - i >= min_gap:
                edges.append((i, j - 1))
            i = j
        else:
            i += 1
    return edges


def detect_grid(img, min_gap=5, min_strength=2):
    """返回 (rows, cols)，每个是 [(y0,y1),...] / [(x0,x1),...]。"""
    rows = _edges(_project(img, 1), min_gap=min_gap, min_strength=min_strength)
    cols = _edges(_project(img, 0), min_gap=min_gap, min_strength=min_strength)
    return rows, cols


def crop_cells(img, rows, cols, out_dir, prefix="cell", pad=1):
    """按行列切块，每块文件名带 dump 坐标: {prefix}_r{ri}_c{ci}_x{x0}_y{y0}_w{w}_h{h}.png"""
    os.makedirs(out_dir, exist_ok=True)
    saved = []
    col_anchor = defaultdict(int)
    for ri, (y0, y1) in enumerate(rows):
        for ci, (x0, x1) in enumerate(cols):
            bx0 = max(0, x0 - pad)
            by0 = max(0, y0 - pad)
            bx1 = min(img.width, x1 + 1 + pad)
            by1 = min(img.height, y1 + 1 + pad)
            if bx1 <= bx0 or by1 <= by0:
                continue
            box = (bx0, by0, bx1, by1)
            cell = img.crop(box)
            w = box[2] - box[0]; h = box[3] - box[1]
            name = f"{prefix}_r{ri:02d}_c{ci:02d}_x{x0}_y{y0}_w{w}_h{h}.png"
            dst = os.path.join(out_dir, name)
            cell.save(dst)
            saved.append((dst, (x0, y0, w, h), (ri, ci)))
    return saved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=None)
    ap.add_argument("--out", default="/tmp/img_preview/cells")
    ap.add_argument("--th", type=int, default=2, dest="min_strength")
    ap.add_argument("--gap", type=int, default=5, dest="min_gap")
    args = ap.parse_args()
    src = args.src or latest_bottom()
    if not src:
        print("no source"); return
    img = _load(src)
    print(f"source: {src}  size={img.size}")
    rows, cols = detect_grid(img, min_gap=args.min_gap, min_strength=args.min_strength)
    print(f"rows={len(rows)} cols={len(cols)}")
    print("row y-bands:", rows)
    print("col x-bands:", cols)
    saved = crop_cells(img, rows, cols, args.out)
    print(f"saved {len(saved)} cells -> {args.out}")
    for dst, rect, (ri, ci) in saved[:12]:
        print(f"  r{ri:02d} c{ci:02d} rect={rect} -> {os.path.basename(dst)}")
    if len(saved) > 12:
        print(f"  ...(+{len(saved)-12} more)")


if __name__ == "__main__":
    main()
