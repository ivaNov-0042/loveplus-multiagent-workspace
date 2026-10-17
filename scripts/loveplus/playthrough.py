#!/usr/bin/env python3
"""推进游戏：验证「はじめから」正确坐标并截屏记录各阶段。

用法: playthrough.py --frames N --dump-every M --prefix P --script "..."
"""
import argparse
import os
import subprocess
import sys
import time



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--frames', type=int, default=300000)
    ap.add_argument('--dump-every', type=int, default=20000)
    ap.add_argument('--prefix', default='/tmp/play')
    ap.add_argument('--script', default='')
    args = ap.parse_args()

    log = open('/tmp/play.log', 'wb')
    cmd = [HEADLESS, ROM, '--frames', str(args.frames),
           '--dump-every', str(args.dump_every), '--dump-prefix', args.prefix]
    if args.script:
        cmd += ['--input-script', args.script]
    proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT,
                            stdin=subprocess.DEVNULL, start_new_session=True,
                            env={'SDL_AUDIODRIVER': 'dummy', 'AZAHAR_LOG': '*:Error',
                                 'PATH': '/usr/bin:/bin'})
    print(f"[i] pid={proc.pid} frames={args.frames} dump_every={args.dump_every}")
    try:
        # 等待结束或超时（frames/3000 秒的经验速率，再放宽）
        est = max(60, args.frames // 2500)
        for _ in range(est):
            if proc.poll() is not None:
                break
            time.sleep(1)
        if proc.poll() is None:
            print("[i] timeout, killing")
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
    finally:
        log.close()


if __name__ == '__main__':
    main()
