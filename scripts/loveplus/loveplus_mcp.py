#!/usr/bin/env python3
"""LovePlus+ 无头模拟器 MCP 服务。

把 azahar_headless 当作一个可交互的"游戏机"暴露成 MCP 工具：
  - 随时下发触摸/按键（实时 TCP 控制通道）
  - 随时抓取当前三屏画面（在 MCP 服务端保存为 PNG 并返回完整路径，可用 read 工具查看）
  - 暂停/继续主循环，便于配合 GDB stub 调试

启动方式（stdio 传输）：
  ./.venv/bin/python scripts/loveplus/loveplus_mcp.py

工具一览：
  start_emulator / stop_emulator / is_running
  tap(x,y,frames) / touch(x,y) / release() / buttons(hex) / buttons_off()
  screenshot(which) / frame() / status() / pause() / resume()
"""
import os
import signal
import shutil
import socket  # _send 的 except socket.timeout 依赖此导入（缺失会 NameError 掩盖真实超时）
import subprocess
import sys
import time
from typing import Union

from PIL import Image

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
# 从项目根 .env 载入本地路径（含机器绝对目录），避免硬编码隐私路径
load_dotenv(os.path.join(REPO, ".env"))
HEADLESS = os.environ.get(
    "AZAHAR_HEADLESS",
    os.path.join(REPO, "tools", "azahar", "build_headless", "bin", "Release", "azahar_headless"))
ROM = os.environ.get(
    "NLP_PLUS_ROM",
    os.path.join(REPO, "data", "loveplus", "roms_patched", "NLP_plus_patched.3ds"))

LIVE_PORT = int(os.environ.get("EMU_LIVE_PORT", "24777"))
DUMP_PREFIX = os.environ.get("EMU_DUMP_PREFIX", "/tmp/az")
GDB_PORT = int(os.environ.get("EMU_GDB_PORT", "24689"))

mcp = FastMCP("loveplus-emu")

# ---- 模拟器进程管理 ----
_proc = None


def _control_connect(timeout=5.0):
    import socket
    s = socket.create_connection(("127.0.0.1", LIVE_PORT), timeout=timeout)
    s.settimeout(timeout)
    return s


def _send(line, timeout=5.0):
    s = _control_connect(timeout)
    try:
        s.sendall((line + "\n").encode())
        parts = []
        try:
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                parts.append(chunk)
                if b"\n" in chunk:
                    break
        except socket.timeout:
            pass
        return b"".join(parts).decode(errors="replace").strip()
    finally:
        s.close()


@mcp.tool()
def start_emulator(frames: int = 2000000, gdb: bool = False, gdb_port: int = GDB_PORT,
                   live_port: int = LIVE_PORT) -> str:
    """启动无头模拟器（后台）。若已在运行则复用。返回控制端口就绪信息。"""
    global _proc
    # 复用已运行的实例
    try:
        r = _send("ping", timeout=2.0)
        if r == "pong":
            return f"already running; live port={live_port} (ping->pong)"
    except Exception:
        pass
    cmd = [HEADLESS, ROM, "--live-port", str(live_port),
           "--dump-prefix", DUMP_PREFIX, "--frames", str(frames)]
    if gdb:
        cmd += ["--gdb", "--port", str(gdb_port)]
    env = dict(os.environ)
    env.update({"SDL_AUDIODRIVER": "dummy", "AZAHAR_LOG": "*:Error"})
    _proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             stdin=subprocess.DEVNULL, start_new_session=True, env=env)
    # 等待控制端口就绪
    for _ in range(60):
        try:
            if _send("ping", timeout=1.5) == "pong":
                return f"started pid={_proc.pid} live_port={live_port} gdb={gdb}({gdb_port})"
        except Exception:
            time.sleep(1.0)
    return f"launched pid={_proc.pid} but control port not ready yet (check emu log)"


@mcp.tool()
def stop_emulator() -> str:
    """停止后台模拟器。"""
    global _proc
    if _proc is None:
        return "no managed process"
    try:
        _proc.terminate()
        _proc.wait(timeout=10)
    except Exception as e:
        try:
            _proc.kill()
        except Exception:
            pass
        return f"killed: {e}"
    finally:
        _proc = None
    return "stopped"


@mcp.tool()
def is_running() -> str:
    """模拟器是否在运行（控制端口可达）。"""
    try:
        return "yes" if _send("ping", timeout=2.0) == "pong" else "no"
    except Exception:
        return "no"


@mcp.tool()
def frame() -> str:
    """返回当前帧号。"""
    return _send("frame", timeout=5.0)


@mcp.tool()
def status() -> str:
    """返回 frame / touch / buttons 状态。"""
    return _send("status", timeout=5.0)


@mcp.tool()
def tap(x: float, y: float, frames: int = 14, wait: bool = True) -> str:
    """在归一化坐标 (x,y) 处点触 `frames` 帧后松开。x,y∈[0,1]（原生 320x240）。
    wait=True 会阻塞到触摸窗口结束，保证稳定触发。"""
    r = _send(f"tap {x:.6f} {y:.6f} {frames}", timeout=5.0)
    if wait:
        # 轮询帧号直到【增长 >= frames】才算触摸窗口结束（旧实现 `f >= 0` 恒真，
        # 等于没等待，tap 后立刻返回 → 后续 screenshot 可能截到按下前画面）
        try:
            f0 = int(_send("frame", timeout=2.0).split()[-1])
        except Exception:
            f0 = -1
        t0 = time.time()
        while time.time() - t0 < frames / 60.0 + 5:
            try:
                f = int(_send("frame", timeout=2.0).split()[-1])
                if f0 < 0 or f >= f0 + frames:
                    break
            except Exception:
                pass
            time.sleep(0.15)
    return r


@mcp.tool()
def touch(x: float, y: float) -> str:
    """按住触摸 (x,y)，直到 release()。"""
    return _send(f"touch {x:.6f} {y:.6f}", timeout=5.0)


@mcp.tool()
def move(x: float, y: float) -> str:
    """在保持当前按下状态不变的前提下，把触摸点移动到 (x,y)。配合 touch() 实现拖拽/滑动。"""
    return _send(f"move {x:.6f} {y:.6f}", timeout=5.0)


@mcp.tool()
def swipe(x0: float, y0: float, x1: float, y1: float, steps: int = 8, step_frames: int = 3) -> str:
    """从 (x0,y0) 按住并拖到 (x1,y1)：touch -> 分步 move -> release。用于滚屏/滑块/摇杆。"""
    return drag_path([[x0, y0], [x1, y1]], hold_frames=step_frames,
                     move_frames=steps * step_frames, release_at_end=True)


def _interpolate_move(x0, y0, x1, y1, frames):
    """在约 frames 帧内从 (x0,y0) 平滑移动到 (x1,y1)，逐段下发 move 让游戏采样到轨迹。"""
    sub = max(2, min(int(frames), 40))
    total = max(frames, 1) / 60.0
    for i in range(1, sub + 1):
        t = i / sub
        _send(f"move {x0 + (x1 - x0) * t:.6f} {y0 + (y1 - y0) * t:.6f}", timeout=5.0)
        time.sleep(total / sub)


def _as_list(v, n):
    """把标量/列表统一成列表：标量重复 n 次；列表原样返回（长度应≈n）。"""
    if isinstance(v, list):
        return [float(x) for x in v]
    return [float(v)] * n


@mcp.tool()
def drag_path(points: list, hold_frames: "Union[int, list]" = 6,
              move_frames: "Union[int, list]" = 12,
              release_at_end: bool = True) -> str:
    """任意长度路径点拖拽。points 为 [[x,y],...]（归一化 0..1）；
    在第一个点按下，依次 move 到后续各点（相邻点间移动 move_frames 帧、到达后停留 hold_frames 帧），
    最后按 release_at_end 决定是否松开。

    hold_frames / move_frames 可为标量（所有点相同）或列表（逐点指定）：
      - hold_frames 长度 = len(points)（每点停留时长，含首点按下、末点结束）
      - move_frames 长度 = len(points)-1（相邻点间移动时长）
    用于复杂手势：滚屏、滑块、列表滑动、键盘擦写等。"""
    if not points or len(points) < 1:
        return "err: points empty"
    pts = [[float(p[0]), float(p[1])] for p in points]
    holds = _as_list(hold_frames, len(pts))
    moves = _as_list(move_frames, max(len(pts) - 1, 0)) if len(pts) > 1 else []
    # 首点按下
    _send(f"touch {pts[0][0]:.6f} {pts[0][1]:.6f}", timeout=5.0)
    time.sleep(holds[0] / 60.0)
    for i in range(1, len(pts)):
        _interpolate_move(pts[i - 1][0], pts[i - 1][1], pts[i][0], pts[i][1], moves[i - 1])
        time.sleep(holds[i] / 60.0)
    if release_at_end:
        r = _send("release", timeout=5.0)
    else:
        r = "kept pressed"
    return (f"ok drag_path n={len(pts)} hold={holds} move={moves} -> {r}")


@mcp.tool()
def release() -> str:
    """松开触摸。"""
    return _send("release", timeout=5.0)


@mcp.tool()
def buttons(hexmask: str) -> str:
    """额外按住按键位掩码（十六进制，例如 '1' = A 键）。与脚本计划 OR。"""
    return _send(f"buttons {hexmask}", timeout=5.0)


@mcp.tool()
def buttons_off() -> str:
    """松开所有 live 按键。"""
    return _send("buttons_off", timeout=5.0)


@mcp.tool()
def _cleanup_disk(threshold_pct: int = 90):
    """磁盘空间监控（2026-10-16 用户要求）：/ 分区占用超过 threshold_pct% 时，
    清理 /tmp 下堆积的 az_live_*.ppm（截图源，转 jpg 后本应删但兜底）与
    最旧的 loveplus_shots 步骤目录，直到降到阈值以下。返回清理说明。"""
    import glob as _g
    try:
        st = shutil.disk_usage("/")
        pct = int(100.0 * st.used / st.total)
    except Exception:
        return "skip: disk usage unknown"
    if pct < threshold_pct:
        return f"ok: disk {pct}% < {threshold_pct}%"
    msgs = [f"warn: disk {pct}% >= {threshold_pct}%, cleaning /tmp"]
    # 1) 删残留 ppm（含所有前缀）
    for pat in (_g.glob("/tmp/az_live_*.ppm"), _g.glob("/tmp/az_*.ppm")):
        for f in pat:
            try:
                os.remove(f)
                msgs.append("rm ppm " + os.path.basename(f))
            except OSError:
                pass
    # 2) 删最旧的 loveplus_shots 步骤目录，直到降到阈值或清空
    shots = "/tmp/loveplus_shots"
    while True:
        try:
            st = shutil.disk_usage("/")
            if int(100.0 * st.used / st.total) < threshold_pct:
                break
        except Exception:
            break
        if not os.path.isdir(shots):
            break
        subs = sorted(
            [os.path.join(shots, d) for d in os.listdir(shots)
             if os.path.isdir(os.path.join(shots, d))],
            key=os.path.getmtime,
        )
        if not subs:
            break
        oldest = subs[0]
        try:
            shutil.rmtree(oldest)
            msgs.append("rmdir " + oldest)
        except OSError:
            break
    return "; ".join(msgs)


@mcp.tool()
def screenshot(which: str = "bottom",
               out_dir: str = "/tmp/loveplus_shots",
               filename: str = "",
               fmt: str = "jpg",
               quality: int = 80,
               wait_frames: int = 0) -> str:
    """抓取当前画面并**在 MCP 服务端保存为图片文件**，返回完整文件路径（可直接用 read 工具查看）。

    which: bottom | top_left | top_right | top | all（top=上屏左，all=上屏+下屏上下拼接）。
    out_dir: 保存目录（默认 /tmp/loveplus_shots，不存在则自动创建）。
    filename: 文件名；留空则自动按 which+帧号命名（如 bottom_1234567.jpg）。
    fmt: "jpg"（默认，省数据量）| "png"（无损）。
    quality: JPEG 质量 1-100（默认 80）。
    wait_frames: 截图前先等到帧号增长 ≥ N 帧（用于等转场/动画结束），0=不等待。
    返回: 成功->完整路径字符串；失败->错误信息字符串。"""
    _cleanup_disk()  # 截图前先按阈值清 /tmp，防磁盘写满
    import glob
    from PIL import Image as _PILImage  # 函数内取模块对象，避免进程内 Image 名被遮蔽
    def _save(img, dst, src_ppm=None):
        if fmt.lower() in ("jpg", "jpeg"):
            img.convert("RGB").save(dst, format="JPEG", quality=quality)
        else:
            img.convert("RGB").save(dst, format="PNG")
        # ppm 转 jpg/png 完成后删除【同帧号】所有 ppm（dump 一次产出 bottom/top_left/
        # top_right 三张，只删请求的会漏），避免 /tmp 堆积占满磁盘（2026-10-16 用户要求）
        if src_ppm:
            _rm_frame_ppms(src_ppm)
        return dst

    def _rm_frame_ppms(src_ppm):
        import glob as _g
        import re as _re
        base = os.path.basename(src_ppm)
        # 形如 az_live_live_232213_top_left.ppm / az_live_live_232213_bottom.ppm
        # 帧号 = 文件名里最后一段纯数字（后缀段数不同：bottom 1 段 / top_left 2 段）
        m = _re.search(r"_(\d+)_(?:bottom|top_left|top_right)\.ppm$", base)
        if not m:
            # 退路：直接删自身
            if os.path.exists(src_ppm):
                try:
                    os.remove(src_ppm)
                except OSError:
                    pass
            return
        frame_id = m.group(1)
        d = os.path.dirname(src_ppm)
        for cand in _g.glob(os.path.join(d, f"{DUMP_PREFIX}_live_{frame_id}_*.ppm")):
            try:
                os.remove(cand)
            except OSError:
                pass
    def _ext():
        return ".jpg" if fmt.lower() in ("jpg", "jpeg") else ".png"
    if wait_frames > 0:
        try:
            f0 = int(_send("frame", timeout=5.0).split()[-1])
        except Exception:
            f0 = -1
        t0 = time.time()
        while time.time() - t0 < 60:
            try:
                f = int(_send("frame", timeout=2.0).split()[-1])
            except Exception:
                break
            if f >= f0 + wait_frames:
                break
            time.sleep(0.2)
    _send("dump", timeout=5.0)
    time.sleep(0.4)
    try:
        os.makedirs(out_dir, exist_ok=True)
    except Exception as e:
        return f"err: cannot create out_dir {out_dir}: {e}"
    cand = {
        "bottom": f"{DUMP_PREFIX}_live_*_bottom.ppm",
        "top_left": f"{DUMP_PREFIX}_live_*_top_left.ppm",
        "top_right": f"{DUMP_PREFIX}_live_*_top_right.ppm",
    }
    if which in cand:
        files = sorted(glob.glob(cand[which]), key=os.path.getmtime, reverse=True)
        if not files:
            return "err: no dump file for " + which
        src = files[0]
        frame = os.path.basename(src).split("_")[-1].split(".")[0]
        name = filename or (f"{which}_{frame}" + _ext())
        if not name.lower().endswith(_ext()):
            name += _ext()
        return _save(_PILImage.open(src), os.path.join(out_dir, name), src_ppm=src)
    if which == "top":
        files = sorted(glob.glob(f"{DUMP_PREFIX}_live_*_top_left.ppm"), key=os.path.getmtime, reverse=True)
        if not files:
            return "err: no dump file for top"
        src = files[0]
        frame = os.path.basename(src).split("_")[-1].split(".")[0]
        name = filename or ("top_" + frame + _ext())
        if not name.lower().endswith(_ext()):
            name += _ext()
        return _save(_PILImage.open(src), os.path.join(out_dir, name), src_ppm=src)
    # all -> 拼上下屏
    b = sorted(glob.glob(cand["bottom"]), key=os.path.getmtime, reverse=True)
    t = sorted(glob.glob(cand["top_left"]), key=os.path.getmtime, reverse=True)
    imgs = []
    if t:
        imgs.append(_PILImage.open(t[0]).convert("RGB"))
    if b:
        imgs.append(_PILImage.open(b[0]).convert("RGB"))
    if not imgs:
        return "err: no dump file for all"
    W = max(im.width for im in imgs)
    H = sum(im.height for im in imgs)
    canvas = _PILImage.new("RGB", (W, H))
    y = 0
    for im in imgs:
        canvas.paste(im, (0, y))
        y += im.height
    frame = os.path.basename((t or b)[0]).split("_")[-1].split(".")[0]
    name = filename or ("all_" + frame + _ext())
    if not name.lower().endswith(_ext()):
        name += _ext()
    # 传 top/bottom 任一源给 _save，由其统一删除同帧号所有 ppm
    src_for_clean = (t or b)[0]
    return _save(canvas, os.path.join(out_dir, name), src_ppm=src_for_clean)


@mcp.tool()
def pause() -> str:
    """暂停主循环（便于 GDB 附着/单步）。"""
    return _send("pause", timeout=5.0)


@mcp.tool()
def resume() -> str:
    """继续主循环。"""
    return _send("resume", timeout=5.0)


@mcp.tool()
def ocr(img: str = "", which: str = "b") -> str:
    """本地 OCR（RapidOCR/PaddleOCR ONNX 模型）：识别模拟器截图，返回【文字+坐标】列表。

    用途：点选按钮/候选字不再肉眼估坐标——先 ocr 看目标文字在哪，
    直接用返回的 touch 坐标点。

    设计（2026-10-16 用户要求）：**不做 find 过滤，一律返回全部识别结果**。
    由调用方（LLM）自行从结果里挑需要的文字与坐标——find 需要预先猜词，
    按钮/候选字常猜不中（如"OK"是图形按钮、未识别到就整项丢失），
    全量返回更可靠。每行同时给出 dump 坐标与换算好的 touch 坐标。

    img: 图片路径（空=先 dump 模拟器当前屏）。
    which: b=下屏(240x320) | u=上屏(240x400) | all=双屏。
    返回: 每行 "屏 dump(x,y) WxH conf 文字 -> touch(tx,ty)"。"""
    import glob as _glob
    from PIL import Image as _I
    from math import inf
    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError:
        return "err: rapidocr_onnxruntime 未安装（pip install rapidocr-onnxruntime）"
    # ocr 自己 dump 时会读 ppm（screenshot 会删但 ocr 不会）→ 记录并在读完删除，防泄漏
    _to_del = []

    def _rm_ppms(paths):
        import re as _re
        import glob as _g2
        for p in paths:
            if not p:
                continue
            _re_m = _re.search(r"_(\d+)_(?:bottom|top_left|top_right)\.ppm$",
                               os.path.basename(p))
            if _re_m:
                for c in _g2.glob(os.path.join(
                        os.path.dirname(p),
                        f"{DUMP_PREFIX}_live_{_re_m.group(1)}_*.ppm")):
                    try:
                        os.remove(c)
                    except OSError:
                        pass
            else:
                try:
                    os.remove(p)
                except OSError:
                    pass

    if img:
        im = _I.open(img).convert("RGB")
        tag = "img"
        h_img = im.height
    else:
        _send("dump", timeout=5.0)
        time.sleep(0.35)
        if which in ("b", "all"):
            fs = sorted(_glob.glob(f"{DUMP_PREFIX}_live_*_bottom.ppm"),
                        key=os.path.getmtime, reverse=True)
            if not fs:
                return "err: no bottom dump"
            im = _I.open(fs[0]).convert("RGB")  # convert 已把像素读进内存，源 ppm 可删
            _to_del.append(fs[0])
            h_img = 0  # 下屏
            tag = "b"
        if which in ("u", "all"):
            fu = sorted(_glob.glob(f"{DUMP_PREFIX}_live_*_top_left.ppm"),
                        key=os.path.getmtime, reverse=True)
            if not fu:
                return "err: no top dump"
            im_u = _I.open(fu[0]).convert("RGB")
            _to_del.append(fu[0])
            if which == "all" and im.height and im.width:
                canvas = _I.new("RGB", (max(im.width, im_u.width),
                                        im.height + im_u.height))
                canvas.paste(im_u, (0, 0))
                canvas.paste(im, (0, im_u.height))
                im, tag, h_img = canvas, "all", im_u.height
            else:
                im, tag, h_img = im_u, "u", 0
    res, _ = RapidOCR()(im) if img or True else (None, None)
    out = []
    for box, text, conf in (res or []):
        x = int(min(p[0] for p in box)); y = int(min(p[1] for p in box))
        w = int(max(p[0] for p in box) - x); h = int(max(p[1] for p in box) - y)
        # 中心点 → touch 坐标（全量返回，不做 find 过滤）
        cx, cy = x + w / 2, y + h / 2
        cy_eff = cy - h_img if tag == "all" else cy   # 拼接图下屏部分 y 减上屏高
        tx, ty = 1 - cy_eff / 320.0, cx / 240.0
        out.append(f"{tag} ({x},{y}) {w}x{h} {conf:.2f} {text} "
                   f"-> touch({tx:.3f},{ty:.3f})")
    return "\n".join(out) if out else "(no text)"


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
