#!/usr/bin/env python3
"""对话自动推进监控器：高频截 u/b（只保留最近一次）+ OCR 追加日志。

用法（后台常驻）:
  setsid python3 scripts/loveplus/dialog_monitor.py --interval 5 \
      --log output/loveplus/monitor_ocr.log > /tmp/dialog_monitor.log 2>&1 < /dev/null &

行为:
  - 每 interval 秒: dump 上/下屏 → 覆盖写 /tmp/loveplus_shots/latest_u.png、latest_b.png
  - OCR 下屏文字区, 与上条结果不同才追加写日志(时间戳+文字+坐标)
  - 画面文字连续 N 次无变化 → 打印 STABLE 提示(不退出)
  - PID 写 /tmp/dialog_monitor.pid
"""
import argparse
import glob
import os
import signal
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import loveplus_mcp as M  # noqa: E402

LATEST_B = "/tmp/loveplus_shots/latest_b.png"
LATEST_U = "/tmp/loveplus_shots/latest_u.png"


def dump_one(which):
    """dump 单屏到 latest_*.png。返回 PIL Image 或 None。"""
    try:
        M._send("dump", timeout=5.0)
        time.sleep(0.4)
        key = "bottom" if which == "b" else "top_left"
        fs = sorted(glob.glob(f"/tmp/az_live_*_{key}.ppm"),
                    key=os.path.getmtime, reverse=True)
        if not fs:
            return None
        from PIL import Image
        im = Image.open(fs[0]).convert("RGB")
        dst = LATEST_B if which == "b" else LATEST_U
        im.save(dst)
        # 清理本屏 ppm（同帧号全部）
        import re
        m = re.search(r"_live(\d+)?_(\d+)_", os.path.basename(fs[0]))
        for f in glob.glob("/tmp/az_live_*.ppm"):
            try:
                os.remove(f)
            except OSError:
                pass
        return im
    except Exception:
        return None


def ocr_text(img_path, which="b"):
    try:
        return M.ocr(img=img_path, which=which)
    except Exception as e:
        return f"ocr-err: {e}"


def ocr_dialog_zoomed(img_path, which="b"):
    """对话文字区裁剪放大 3x 再 OCR，提高小字命中率。"""
    try:
        from PIL import Image
        im = Image.open(img_path)
        w, h = im.size
        # 下屏对话框约在底部 1/4；上屏约在底部 1/5
        if which == "b":
            box = (0, int(h * 0.72), w, h)
        else:
            box = (0, int(h * 0.78), w, h)
        crop = im.crop(box)
        crop = crop.resize((crop.width * 3, crop.height * 3), Image.LANCZOS)
        zoom_path = img_path.replace(".png", "_zoom.png")
        crop.save(zoom_path)
        return M.ocr(img=zoom_path, which=which)
    except Exception as e:
        return f"zoom-ocr-err: {e}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", type=float, default=5.0)
    ap.add_argument("--log", default="output/loveplus/monitor_ocr.log")
    ap.add_argument("--max-stable", type=int, default=12,
                    help="连续 N 次无变化打印 STABLE")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.log) or ".", exist_ok=True)
    os.makedirs(os.path.dirname(LATEST_B), exist_ok=True)

    with open("/tmp/dialog_monitor.pid", "w") as f:
        f.write(str(os.getpid()))

    running = {"on": True}

    def stop(*_):
        running["on"] = False
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    last_txt = None
    stable = 0
    with open(args.log, "a", encoding="utf-8") as log:
        log.write(f"=== monitor start {time.strftime('%F %T')} ===\n")
        while running["on"]:
            t0 = time.time()
            dump_one("b")
            dump_one("u")
            txt = ocr_text(LATEST_B, "b")
            txt_u = ocr_text(LATEST_U, "u")
            # 整图 OCR 空时，用放大 OCR 兜底（对话小字）
            if (not txt) or txt == "(no text)":
                z_b = ocr_dialog_zoomed(LATEST_B, "b")
            else:
                z_b = ""
            if (not txt_u) or txt_u == "(no text)":
                z_u = ocr_dialog_zoomed(LATEST_U, "u")
            else:
                z_u = ""
            key = (txt or "") + (z_b or "") + "|" + (txt_u or "") + (z_u or "")
            if key != last_txt:
                stamp = time.strftime("%H:%M:%S")
                log.write(f"[{stamp}] B: {txt}\n")
                if z_b:
                    log.write(f"[{stamp}] Bz: {z_b}\n")
                log.write(f"[{stamp}] U: {txt_u}\n")
                if z_u:
                    log.write(f"[{stamp}] Uz: {z_u}\n")
                log.flush()
                last_txt = key
                stable = 0
            else:
                stable += 1
                if stable == args.max_stable:
                    log.write(f"[{time.strftime('%H:%M:%S')}] STABLE "
                              f"({args.max_stable}x no change)\n")
                    log.flush()
            # interval 扣除耗时
            dt = time.time() - t0
            if dt < args.interval:
                time.sleep(args.interval - dt)
        log.write(f"=== monitor stop {time.strftime('%F %T')} ===\n")


if __name__ == "__main__":
    main()
