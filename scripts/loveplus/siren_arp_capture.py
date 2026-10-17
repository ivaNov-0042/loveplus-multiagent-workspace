#!/usr/bin/env python3
"""抓取游戏 Siren 解码器的内部中间量，用于校准 Python 移植。

断点：
  0x00142454  逐帧解码入口：r0=对象, r1=流号, r2=压缩帧指针(46B)
  0x0075e6d8  帧解码器内、decode_envelope 返回后：sp 起是栈帧，
              sp+0xf8 = arp(区域功率指数)  sp+0x168 = 标准偏差

产物（<out>/）：
  NN_frame.bin    46B 压缩帧（就是被解的那帧）
  NN_stack.bin    [sp, sp+0x1f0) 的原始栈内容（含 arp/std/power_categories）
  NN_cfg.bin      对象 this+0x1440 起 0x40 字节（解码器配置：码率/每帧位数/区域数）
  manifest.csv    行号, 流号, 帧指针, sp
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rsp_client import GDBClient  # noqa: E402

BP_ENTRY = 0x00142454
BP_ENV = 0x0075E6D8
FRAME_LEN = 46
STACK_LEN = 0x1F0
CFG_OFF = 0x1440
CFG_LEN = 0x40


def connect(port, tries=120, timeout=30.0):
    last = None
    for _ in range(tries):
        try:
            return GDBClient(port=port, timeout=timeout)
        except OSError as e:
            last = e
            time.sleep(1.0)
    raise last


class Cap:
    def __init__(self, port, out, timeout=30.0):
        self.c = connect(port, timeout=timeout)
        self.out = out
        os.makedirs(out, exist_ok=True)
        self.rows = []
        self.n = 0

    def step_over(self, bp):
        self.c.clear_break(bp)
        self.c.step()
        self.c.set_break(bp)

    def run(self, frames=25, budget=200):
        c = self.c
        c.set_break(BP_ENTRY)
        c.set_break(BP_ENV)
        pending = None
        for _ in range(budget):
            if self.n >= frames:
                break
            try:
                c.continue_()
            except Exception as e:
                print('[!] continue: %s' % e)
                break
            r = c.read_registers()
            pc = r['pc']
            if pc == BP_ENTRY:
                fb = c.read_mem(r['r2'], FRAME_LEN)
                cfg = c.read_mem(r['r0'] + CFG_OFF, CFG_LEN)
                pending = (r['r0'], r['r1'], r['r2'], fb)
                idx = self.n
                open(os.path.join(self.out, '%02d_frame.bin' % idx), 'wb').write(fb)
                open(os.path.join(self.out, '%02d_cfg.bin' % idx), 'wb').write(cfg)
                import struct
                cf = struct.unpack('<16I', cfg[:64])
                print('[E] stream=%d fp=%08x cfg=%s' % (r['r1'], r['r2'], cf[:6]))
                print('      frame %s' % fb[:12].hex(' '))
                self.step_over(BP_ENTRY)
            elif pc == BP_ENV:
                st = c.read_mem(r['sp'], STACK_LEN)
                idx = self.n
                open(os.path.join(self.out, '%02d_stack.bin' % idx), 'wb').write(st)
                sp = r['sp']
                import struct
                arp32 = struct.unpack('<28i', st[0xf8:0xf8 + 112])
                arp16 = struct.unpack('<28h', st[0xf8:0xf8 + 56])
                print('[V] sp=%08x arp32[0:14]=%s' % (sp, arp32[:14]))
                print('      arp32[14:28]=%s' % (arp32[14:],))
                print('      arp16[0:28]=%s' % (arp16,))
                if pending is not None:
                    self.rows.append([self.n, pending[1], pending[2], sp])
                    pending = None
                self.n += 1
                self.step_over(BP_ENV)
            else:
                print('[?] unexpected pc=%08x' % pc)
                break
        with open(os.path.join(self.out, 'manifest.csv'), 'w') as f:
            f.write('idx,stream,frame_ptr,sp\n')
            for row in self.rows:
                f.write('%d,%d,0x%08x,0x%08x\n' % tuple(row))
        print('[i] captured %d frames -> %s' % (self.n, self.out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=int(os.environ.get('EMU_GDB_PORT', '24689')))
    ap.add_argument('--frames', type=int, default=25)
    ap.add_argument('--out', default='/tmp/siren_arp')
    ap.add_argument('--timeout', type=float, default=30.0)
    a = ap.parse_args()
    cap = Cap(a.port, a.out, a.timeout)
    try:
        cap.run(a.frames)
    finally:
        cap.c.close()


if __name__ == '__main__':
    main()
