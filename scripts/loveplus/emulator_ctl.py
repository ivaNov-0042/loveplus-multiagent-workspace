#!/usr/bin/env python3
"""无头 azahar 模拟器的实时控制客户端（TCP 控制通道）。

配合 `azahar_headless ... --live-port N` 使用。模拟器每帧把触摸/按键覆盖到
全局原子变量上，并响应本客户端的文本命令：

  tap <x> <y> [frames]   按一下 (归一化 0..1)，若干帧后松开（默认 12）
  touch <x> <y>          按住触摸，直到 release
  release                松开触摸
  buttons <hexmask>      额外按住按键位掩码（与脚本计划 OR）
  buttons_off            松开所有 live 按键
  dump                   立即导出当前三屏到 <prefix>_live_<frame>.ppm
  frame                  返回当前帧号
  status                 返回 frame / touch / buttons
  pause / resume         暂停/继续主循环（便于调试器附着）
  ping -> pong

屏幕坐标说明：3DS 下屏原生 320x240（x,y）。azahar 软渲染 bottom 缓冲是
240x320（竖屏，旋转后的显示）。本客户端统一用**原生归一化坐标** (x/320, y/240)，
由模拟器直接乘到 HID。触摸点 (0.428, 0.496) 已验证对应「はじめから」按钮。
"""
import socket
import sys
import time


class EmuControl:
    def __init__(self, host="127.0.0.1", port=24777, timeout=5.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.s = None

    def connect(self):
        self.s = socket.create_connection((self.host, self.port), timeout=self.timeout)
        self.s.settimeout(self.timeout)
        return self

    def _cmd(self, line):
        if self.s is None:
            self.connect()
        self.s.sendall((line + "\n").encode())
        # 读取一行响应（部分命令无响应，靠超时结束）
        self.s.settimeout(self.timeout)
        parts = []
        try:
            while True:
                chunk = self.s.recv(4096)
                if not chunk:
                    break
                parts.append(chunk)
                if b"\n" in chunk:
                    break
        except socket.timeout:
            pass
        data = b"".join(parts)
        return data.decode(errors="replace").strip()

    # ---- 高层 API ----
    def ping(self):
        return self._cmd("ping")

    def frame(self):
        return int(self._cmd("frame").split()[-1])

    def status(self):
        return self._cmd("status")

    def tap(self, x, y, frames=12):
        return self._cmd(f"tap {x:.6f} {y:.6f} {frames}")

    def touch(self, x, y):
        return self._cmd(f"touch {x:.6f} {y:.6f}")

    def release(self):
        return self._cmd("release")

    def buttons(self, hexmask):
        return self._cmd(f"buttons {hexmask}")

    def buttons_off(self):
        return self._cmd("buttons_off")

    def dump(self):
        return self._cmd("dump")

    def pause(self):
        return self._cmd("pause")

    def resume(self):
        return self._cmd("resume")

    def wait_frame(self, target, timeout=60):
        """阻塞直到帧号 >= target。"""
        t0 = time.time()
        while time.time() - t0 < timeout:
            try:
                f = self.frame()
            except Exception:
                f = -1
            if f >= target:
                return f
            time.sleep(0.2)
        return -1

    def close(self):
        if self.s:
            try:
                self.s.close()
            except Exception:
                pass
            self.s = None


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=24777)
    ap.add_argument("cmd", nargs="+", help="要发送的原始命令（如 frame / tap 0.5 0.5 / status）")
    args = ap.parse_args()
    c = EmuControl(port=args.port).connect()
    print(c._cmd(" ".join(args.cmd)))
    c.close()


if __name__ == "__main__":
    main()
