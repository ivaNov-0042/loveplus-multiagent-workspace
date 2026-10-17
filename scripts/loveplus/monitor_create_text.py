#!/usr/bin/env python3
"""通过检测「SDカードに追加データを作成しています」文字区域是否消失来判断创建是否完成。"""
import sys, os, glob, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import loveplus_mcp as M
from PIL import Image
import numpy as np

OUT = "/tmp/loveplus_shots"
TEXT_Y = (148, 178)
TEXT_X = (40, 200)

def text_dark_count():
    M._send("dump", timeout=5.0); time.sleep(0.5)
    f = sorted(glob.glob(f"{M.DUMP_PREFIX}_live_*_bottom.ppm"), key=os.path.getmtime, reverse=True)[0]
    a = np.array(Image.open(f).convert("L"))
    region = a[TEXT_Y[0]:TEXT_Y[1], TEXT_X[0]:TEXT_X[1]]
    return int((region < 150).sum()), f

def main(max_checks=120, interval=300):
    miss = 0
    for i in range(max_checks):
        time.sleep(interval)
        dark, f = text_dark_count()
        fr = M._send("frame")
        # 连续两次 dark<200 才判定完成，防动画抖动误报
        miss = miss + 1 if dark < 200 else 0
        print(f"[{i}] {fr} text_dark={dark} miss={miss} {'DONE?' if miss >= 2 else 'creating'}", flush=True)
        if miss >= 2:
            M.screenshot(which="all", out_dir=OUT, filename=f"create_done_text_{i}.png")
            print(f"    saved create_done_text_{i}.png", flush=True)
            return
    print("monitor done (still creating)", flush=True)

if __name__ == "__main__":
    main()
