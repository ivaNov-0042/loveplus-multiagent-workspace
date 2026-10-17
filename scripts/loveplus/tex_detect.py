#!/usr/bin/env python3
"""多卷积核纹理网格检测（grid_detect 的升级版）。

流程:
  1. 图像 → 灰度 float
  2. 多卷积核特征提取:
     - sobel_x / sobel_y : 纵横边缘能量
     - laplacian         : 细纹理能量
     - box_blur(k=9)     : 平均背景（原图 - 背景 = 大尺度对比）
  3. 各特征取绝对值能量图，加权融合为一张"显著性图"
  4. 行/列分别对显著性求和 → 投影曲线
  5. 平滑 + 双阈值(低阈值进、高阈值出)滞回 → 找连续段 = 行/列边界
  6. 按段切割，块文件名带 dump 坐标

用法:
  python3 tex_detect.py [--src IMG] [--out DIR] [--lo 低阈值] [--hi 高阈值]
                        [--no-th 启用背景差分] [--save-feat]
不依赖 scipy/opencv，纯 numpy 手写卷积（核小, 性能足够）。
"""
import os
import sys
import glob
import argparse
import numpy as np

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


def conv2(a, k):
    """2D 卷积（valid 部分再 pad 回原尺寸，kernel 需奇数边长）。"""
    kh, kw = k.shape
    ph, pw = kh // 2, kw // 2
    ap = np.pad(a, ((ph, ph), (pw, pw)), mode="edge")
    # 用 stride trick 做滑动窗口
    win = np.lib.stride_tricks.sliding_window_view(ap, (kh, kw))
    return np.einsum("ijkl,kl->ij", win, k)


def feature_maps(img_gray):
    a = np.asarray(img_gray, dtype=np.float64)
    kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64)   # sobel x
    ky = kx.T                                                                # sobel y
    lap = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float64)    # laplacian
    box = np.ones((9, 9), dtype=np.float64) / 81.0                           # 平均背景

    gx = conv2(a, kx)
    gy = conv2(a, ky)
    lp = conv2(a, lap)
    bg = conv2(a, box)          # 平均背景
    contrast = a - bg           # 大尺度对比（原 - 背景）

    feats = {
        "edge_x": np.abs(gx),
        "edge_y": np.abs(gy),
        "texture": np.abs(lp),
        "contrast": np.abs(contrast),
    }
    return feats, a


def saliency(feats, weights=None):
    if weights is None:
        weights = {"edge_x": 1.0, "edge_y": 1.0, "texture": 0.7, "contrast": 0.5}
    acc = None
    for name, w in weights.items():
        f = feats[name] / (feats[name].max() + 1e-9)   # 各通道归一化
        acc = w * f if acc is None else acc + w * f
    return acc


def hysteresis_segments(profile, lo, hi, min_gap=5):
    """滞回双阈值切分: 越过 hi 进入段, 低于 lo 退出段。返回 [(s,e),...]。"""
    p = np.asarray(profile, dtype=np.float64)
    n = len(p)
    segs = []
    in_seg = False
    start = 0
    for i in range(n):
        v = p[i]
        if not in_seg:
            if v >= hi:
                in_seg = True
                start = i
        else:
            if v < lo:
                in_seg = False
                if i - start >= min_gap:
                    segs.append((start, i - 1))
    if in_seg and n - start >= min_gap:
        segs.append((start, n - 1))
    return segs


def smooth(x, k=5):
    k = max(1, k | 1)
    ker = np.ones(k) / k
    return np.convolve(x, ker, mode="same")


def tex_detect_grid(img, lo=0.08, hi=0.18, min_gap=5, weights=None):
    feats, _ = feature_maps(img)
    sal = saliency(feats, weights)
    row_prof = smooth(sal.sum(axis=1), 5)   # 每行显著性和
    col_prof = smooth(sal.sum(axis=0), 5)   # 每列显著性和
    # 归一化到 0..1 以便阈值通用
    row_prof /= (row_prof.max() + 1e-9)
    col_prof /= (col_prof.max() + 1e-9)
    rows = hysteresis_segments(row_prof, lo, hi, min_gap)
    cols = hysteresis_segments(col_prof, lo, hi, min_gap)
    return rows, cols, row_prof, col_prof, sal


def crop_cells(img, rows, cols, out_dir, prefix="t", pad=1):
    os.makedirs(out_dir, exist_ok=True)
    out = []
    for ri, (y0, y1) in enumerate(rows):
        for ci, (x0, x1) in enumerate(cols):
            bx0, by0 = max(0, x0 - pad), max(0, y0 - pad)
            bx1, by1 = min(img.width, x1 + 1 + pad), min(img.height, y1 + 1 + pad)
            if bx1 <= bx0 or by1 <= by0:
                continue
            cell = img.crop((bx0, by0, bx1, by1))
            name = f"{prefix}_r{ri:02d}_c{ci:02d}_x{x0}_y{y0}_w{x1-x0+1}_h{y1-y0+1}.png"
            cell.save(os.path.join(out_dir, name))
            out.append((ri, ci, x0, y0, x1 - x0 + 1, y1 - y0 + 1))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=None)
    ap.add_argument("--out", default="/tmp/img_preview/tex_cells")
    ap.add_argument("--lo", type=float, default=0.08)
    ap.add_argument("--hi", type=float, default=0.18)
    ap.add_argument("--gap", type=int, default=5)
    ap.add_argument("--save-feat", action="store_true")
    args = ap.parse_args()
    src = args.src or latest_bottom()
    if not src:
        print("no source"); return
    img = _load(src)
    print(f"source: {src} size={img.size}")
    rows, cols, rp, cp, sal = tex_detect_grid(img, lo=args.lo, hi=args.hi, min_gap=args.gap)
    print(f"rows={len(rows)} cols={len(cols)}")
    print("row y-bands:", rows)
    print("col x-bands:", cols)
    if args.save_feat:
        base = os.path.splitext(os.path.basename(src))[0]
        for name, arr in [("rowprof", rp), ("colprof", cp), ("sal", sal)]:
            a = (arr / (arr.max() + 1e-9) * 255).astype(np.uint8)
            Image.fromarray(a).save(os.path.join("/tmp/img_preview", f"{base}_{name}.png"))
        print("feat maps saved to /tmp/img_preview/<src>_{rowprof,colprof,sal}.png")
    cells = crop_cells(img, rows, cols, args.out)
    print(f"saved {len(cells)} cells -> {args.out}")
    for ri, ci, x, y, w, h in cells[:12]:
        print(f"  r{ri:02d} c{ci:02d} x={x} y={y} w={w} h={h}")
    if len(cells) > 12:
        print(f"  ...(+{len(cells)-12} more)")


if __name__ == "__main__":
    main()
