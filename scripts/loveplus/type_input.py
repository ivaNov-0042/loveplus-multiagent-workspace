#!/usr/bin/env python3
"""NLP+ 文字输入驱动：每步自动落盘 u(上屏=输入回显)+b(下屏=键盘) 两张图。

背景（2026-10-15 用户指明）：文字输入时**上屏显示你输入了什么**，下屏是键盘——
必须 u/b 成对落盘才能核对输入结果（见 skill `loveplus-emu-ops`「截图归档」）。
全程走 MCP 公开工具（drag_path/touch/release/screenshot），不直接 _send。

命名: /tmp/loveplus_shots/<step>/NN_b_描述.jpg + NN_u_描述.jpg（NN 自动递增）

用法:
  # 长按某键并落盘 u/b（press 相 + rel 相共 4 张）
  python3 type_input.py --step 03_input --touch 0.753 0.254 --desc kana_ki
  # 连续按键（touch 坐标序列），每键 press+rel 各落盘一对
  python3 type_input.py --step 03_input --seq 0.753,0.254,ki 0.688,0.358,su
  # 只看当前状态（不按键）
  python3 type_input.py --step 03_input --desc state
"""
import os
import sys
import time
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import loveplus_mcp as M

SHOTS = "/tmp/loveplus_shots"


def next_id(step_dir):
    os.makedirs(step_dir, exist_ok=True)
    ids = [0]
    for f in os.listdir(step_dir):
        head = f.split("_", 1)[0]
        if head.isdigit():
            ids.append(int(head))
    return max(ids) + 1


def save_ub(step_dir, nid, desc):
    """截图并成对保存 NN_b_desc.jpg + NN_u_desc.jpg。返回 (u, b) 路径。"""
    b = M.screenshot(which="bottom", out_dir=step_dir,
                     filename=f"{nid}_b_{desc}.jpg", fmt="jpg", quality=85)
    u = M.screenshot(which="top", out_dir=step_dir,
                     filename=f"{nid}_u_{desc}.jpg", fmt="jpg", quality=85)
    return u, b


def wait_frames(n, timeout=60.0):
    try:
        f0 = int(M.frame().split()[-1])
    except Exception:
        f0 = -1
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            f = int(M.frame().split()[-1])
            if f >= f0 + n:
                return True
        except Exception:
            pass
        time.sleep(0.15)
    return False


def press_and_capture(step_dir, nid, desc, x, y, hold=150, wait=400):
    """长按 (x,y) → press 相落盘 → release → 等 wait 帧 → rel 相落盘。"""
    M.touch(x, y)
    wait_frames(hold)
    u1, b1 = save_ub(step_dir, nid, f"{desc}_press")
    M.release()
    wait_frames(wait)
    u2, b2 = save_ub(step_dir, nid + 1, desc)
    print(f"[{nid}] '{desc}' touch({x:.3f},{y:.3f})")
    print(f"  press u={u1}\n  press b={b1}\n  rel   u={u2}\n  rel   b={b2}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", required=True)
    ap.add_argument("--desc", default="op")
    ap.add_argument("--touch", nargs=2, type=float, metavar=("X", "Y"))
    ap.add_argument("--seq", nargs="*", metavar="X,Y,DESC",
                    help="连续按键: '0.753,0.254,ki' ...")
    ap.add_argument("--hold", type=int, default=150)
    ap.add_argument("--wait", type=int, default=400)
    args = ap.parse_args()

    step_dir = os.path.join(SHOTS, args.step)
    nid = next_id(step_dir)

    if args.seq:
        for item in args.seq:
            x_s, y_s, d = item.split(",")
            press_and_capture(step_dir, nid, d, float(x_s), float(y_s),
                              args.hold, args.wait)
            nid += 2
            time.sleep(1.0)
    elif args.touch:
        press_and_capture(step_dir, nid, args.desc,
                          args.touch[0], args.touch[1], args.hold, args.wait)
    else:
        u, b = save_ub(step_dir, nid, args.desc)
        print(f"[{nid}] state u={u}\n       b={b}")


if __name__ == "__main__":
    main()
