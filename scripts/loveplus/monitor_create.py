#!/usr/bin/env python3
"""轮询下屏特征，检测存档创建进度画面是否变化；变化时保存截图。"""
import sys, os, glob, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import loveplus_mcp as M
from PIL import Image
import numpy as np

OUT = "/tmp/loveplus_shots"
REF = os.path.join(OUT, "_ref_sig.npy")
ref = np.load(REF)

def bottom_grid():
    M._send("dump", timeout=5.0); time.sleep(0.5)
    f = sorted(glob.glob(f"{M.DUMP_PREFIX}_live_*_bottom.ppm"), key=os.path.getmtime, reverse=True)[0]
    a = np.array(Image.open(f).convert("L"))
    H, W = a.shape
    g = a.reshape(H // 8, 8, W // 8, 8).mean(axis=(1, 3)).astype(np.uint8)
    return g, f

def diff(g):
    return int(np.abs(g.astype(int) - ref.astype(int)).sum())

def main(max_checks=30, interval=20):
    log = []
    last_grid, _ = bottom_grid()
    for i in range(max_checks):
        time.sleep(interval)
        g, f = bottom_grid()
        fr = M._send("frame")
        d = diff(g)
        changed = d > 4000
        print(f"[{i}] {fr} diff={d} {'CHANGED' if changed else ''}", flush=True)
        if changed:
            name = f"create_check_{i}.png"
            dst = os.path.join(OUT, name)
            Image.open(f).convert("RGB").save(dst, format="PNG")
            print(f"    saved {dst}", flush=True)
            # 再拍个上屏对比
            try:
                M.screenshot(which="all", out_dir=OUT, filename=f"create_check_{i}_all.png")
            except Exception as e:
                print("    all-shot err", e, flush=True)
        if i > 0 and changed:
            # 连续两次变化通常意味着进入了新流程；多留几张后退出
            pass
    print("monitor done (max checks reached)", flush=True)

if __name__ == "__main__":
    main()
