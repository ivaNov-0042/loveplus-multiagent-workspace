#!/usr/bin/env python3
"""动态抓 Siren14 解码真值（输入压缩帧 + 输出 PCM）。

断点位置（NLP+ code.bin，基址 0x00100000）：
  - 0x00142454  逐帧解码函数入口：r0=对象, r1=流号, r2=压缩帧指针(46B), r3=PCM 输出缓冲
  - 0x001424b8  同一函数内、帧解码返回后：r4=对象, r5=流号, r6=PCM 输出缓冲

关键坑：azahar 的断点是**内存 BKPT 打桩**，直接 continue 会原地再命中。
        必须「删断点 → 单步 → 重设断点」越过（本脚本 _step_over 实现）。

用法：
  ./.venv/bin/python scripts/loveplus/siren_capture.py --frames 40 --out /tmp/siren_ref
产物：
  <out>/frame_%04d.bin  (46B 压缩帧)   <out>/pcm_%04d.raw (1280B=640×s16le)
  <out>/manifest.csv    (序号, this, idx, 帧指针, 输出指针)
"""
import argparse
import os
import struct
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rsp_client import GDBClient  # noqa: E402

BP_ENTRY = 0x00142454
BP_POST = 0x001424b8
FRAME_LEN = 46
PCM_LEN = 1280


def rms_s16(b):
    n = len(b) // 2
    if n == 0:
        return 0
    v = struct.unpack('<%dh' % n, b)
    return int((sum(x * x for x in v) / n) ** 0.5)


def connect(port, tries=90, timeout=30.0):
    last = None
    for _ in range(tries):
        try:
            return GDBClient(port=port, timeout=timeout)
        except OSError as e:
            last = e
            time.sleep(1.0)
    raise last


class Capture:
    def __init__(self, port, out, timeout=30.0):
        self.c = connect(port, timeout=timeout)
        self.out = out
        os.makedirs(out, exist_ok=True)
        self.rows = []

    def step_over(self, bp):
        """删断点→单步→重设断点，越过 BKPT 桩。"""
        self.c.clear_break(bp)
        self.c.step()
        self.c.set_break(bp)

    def run(self, want_frames=40, budget=200):
        c = self.c
        c.set_break(BP_ENTRY)
        c.set_break(BP_POST)
        n_pcm = 0
        for _ in range(budget):
            if n_pcm >= want_frames:
                break
            try:
                c.continue_()
            except Exception as e:
                print('[!] continue: %s' % e)
                break
            r = c.read_registers()
            pc = r['pc']
            if pc == BP_ENTRY:
                this, idx, fp = r['r0'], r['r1'], r['r2']
                data = c.read_mem(fp, FRAME_LEN)
                self.rows.append(['entry', this, idx, fp, ''])
                print('[A] this=%08x idx=%d fp=%08x %s' % (this, idx, fp, data[:8].hex(' ')))
                self.step_over(BP_ENTRY)
            elif pc == BP_POST:
                this, idx, src = r['r4'], r['r5'], r['r6']
                pcm = c.read_mem(src, PCM_LEN)
                n = len([x for x in self.rows if x[0] == 'post'])
                open(os.path.join(self.out, 'pcm_%04d.raw' % n), 'wb').write(pcm)
                # 同时把该流最近的输入帧存下（entry 行里最近一条同流号的帧指针）
                fp = None
                for row in reversed(self.rows):
                    if row[0] == 'entry' and row[2] == idx:
                        fp, fptr = row[1], row[3]
                        break
                self.rows.append(['post', this, idx, src, 'rms=%d' % rms_s16(pcm)])
                print('[B] this=%08x idx=%d src=%08x rms=%6d' % (this, idx, src, rms_s16(pcm)))
                if fp is not None:
                    open(os.path.join(self.out, 'frame_%04d.bin' % n), 'wb').write(
                        c.read_mem(fp, FRAME_LEN))
                n_pcm += 1
                self.step_over(BP_POST)
            else:
                print('[?] unexpected pc=0x%08x (entry=0x%08x post=0x%08x)'
                      % (pc, BP_ENTRY, BP_POST))
                break
        # manifest
        with open(os.path.join(self.out, 'manifest.csv'), 'w') as f:
            f.write('kind,this,idx,ptr,note\n')
            for row in self.rows:
                f.write('%s,0x%08x,%d,0x%08x,%s\n' % tuple(row))
        print('[i] captured %d pcm frames -> %s' % (n_pcm, self.out))

    def close(self):
        self.c.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=int(os.environ.get('EMU_GDB_PORT', '24689')))
    ap.add_argument('--frames', type=int, default=40)
    ap.add_argument('--out', default='/tmp/siren_ref')
    ap.add_argument('--timeout', type=float, default=30.0)
    a = ap.parse_args()
    cap = Capture(a.port, a.out, a.timeout)
    try:
        cap.run(a.frames)
    finally:
        cap.close()


if __name__ == '__main__':
    main()
