#!/usr/bin/env python3
"""每 5 分钟用 MCP screenshot 抓一张创建画面，存 /tmp/loveplus_shots/monitor/。
退出条件：画面从创建文本变为其他（可能完成）或超时 3 小时。"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import loveplus_mcp as M

OUT = "/tmp/loveplus_shots/monitor"
os.makedirs(OUT, exist_ok=True)

def run(hours=3.0, interval=300):
    t0 = time.time()
    i = 0
    while time.time() - t0 < hours * 3600:
        time.sleep(interval)
        i += 1
        try:
            p = M.screenshot(which="all", out_dir=OUT, filename=f"mon_{i:03d}.png")
            fr = M.frame()
            print(f"[{i}] {time.strftime('%H:%M:%S')} frame={fr} -> {p}", flush=True)
        except Exception as e:
            print(f"[{i}] err: {e}", flush=True)

if __name__ == "__main__":
    run()
