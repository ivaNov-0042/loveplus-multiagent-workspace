#!/usr/bin/env python3
"""监控追加数据创建过程；画面发生大变化时保存三屏并退出。"""
import sys, os, glob, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import loveplus_mcp as M
from PIL import Image
import numpy as np

OUT = "/tmp/loveplus_shots"
REF = os.path.join(OUT, "_ref_sig2.npy")
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

def main(max_checks=90, interval=20):
    for i in range(max_checks):
        time.sleep(interval)
        g, f = bottom_grid()
        fr = M._send("frame")
        d = diff(g)
        print(f"[{i}] {fr} diff={d} {'CHANGED' if d > 8000 else ''}", flush=True)
        if d > 8000:
            M.screenshot(which="all", out_dir=OUT, filename=f"create_done_{i}.png")
            print(f"    saved all-shot create_done_{i}.png", flush=True)
            return
    print("monitor done (max checks reached, still creating)", flush=True)

if __name__ == "__main__":
    main()
