#!/usr/bin/env python3
"""单会话 GDB RSP 调试器：在一次连接内顺序执行多条命令。

为什么必须单会话：azahar stub 是单客户端，**客户端断开后 stub 重启、断点全丢**。
所以「设断点 → 跑 → 看命中 → dump」必须在同一个连接里做完。

用法:
  ./.venv/bin/python scripts/loveplus/gdb_session.py -c "bp 0x6d6f04; c 30; regs"
  ./.venv/bin/python scripts/loveplus/gdb_session.py -f /tmp/plan.txt

命令一览:
  bp  0xADDR            执行断点 (Z0, len=4)
  rbp 0xADDR            读 watchpoint (Z3)
  wbp 0xADDR            写 watchpoint (Z2)
  abp 0xADDR            读写 watchpoint (Z4)
  dbp 0xADDR            删除执行断点 (z0)
  c [SECS]              继续 → 等停止(默认25s)；打印停止应答/寄存器/pc+lr 反汇编/栈
  go [SECS]             非阻塞继续，等 SECS 后返回（不打断）
  int                   发送 Ctrl-C 打断当前运行
  regs                  读寄存器
  mem 0xADDR [LEN]      读内存并 hexdump（默认 64）
  dump 0xADDR LEN PATH  读内存写文件
  str 0xADDR            dump C 字符串
  x 0xADDR [N]          反汇编 N 条（默认 12）
  fn 0xADDR             反汇编该地址起 40 条，标记函数序言
  threads               列出线程
  tid <N>               切换线程 H g
  sleep SECS
  quit
"""
import argparse
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rsp_client import GDBClient  # noqa: E402

try:
    from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM
    _MD = Cs(CS_ARCH_ARM, CS_MODE_ARM)
except Exception:  # capstone 可选
    _MD = None

BASE = 0x00100000


def dis(addr, n=12, code=None, base=BASE):
    """用 capstone 反汇编（默认读本仓库解压后的 code.bin）。"""
    if code is None or _MD is None:
        print("    (no capstone/code)")
        return
    off = addr - base
    for insn in _MD.disasm(code[off:off + n * 4], addr):
        print("    %#010x: %-8s %s" % (insn.address, insn.mnemonic, insn.op_str))


def regs_line(regs):
    names = ['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10', 'r11',
             'r12', 'sp', 'lr', 'pc']
    out = []
    for i in range(0, 16, 4):
        out.append("  " + "  ".join("%s=%#010x" % (names[j], regs[names[j]]) for j in range(i, i + 4)))
    out.append("  cpsr=%#010x mode=%s" % (regs.get('cpsr', 0),
                                          'THUMB' if regs.get('cpsr', 0) & 0x20 else 'ARM'))
    return "\n".join(out)


def le(s):
    b = bytes.fromhex(s)
    b += b'\x00' * (-len(b) % 4)
    return int.from_bytes(b[:4], 'little')


class Session:
    def __init__(self, port, code_path=None, connect_tries=60):
        last = None
        for _ in range(connect_tries):
            try:
                self.c = GDBClient(port=port, timeout=30.0)
                break
            except OSError as e:
                last = e
                time.sleep(1.0)
        else:
            raise last
        self.code = open(code_path, 'rb').read() if code_path else None
        self.pending = False  # 已发出 'c' 而停止应答未取

    # --- 基础 ---
    def stop_reply(self):
        return self.c.recv_packet()

    def select_thread(self, rep):
        m = re.search(r'thread:([0-9a-fA-F]+);', rep)
        if m:
            self.c.send('H g' + m.group(1))
            try:
                self.c.recv_packet()
            except Exception:
                pass
            return m.group(1)
        return None

    def show_stop(self, rep, extra=True):
        print("[stop] %r" % rep[:80])
        tid = self.select_thread(rep)
        regs = self.c.read_registers()
        print(regs_line(regs))
        print("  thread=%s" % tid)
        if extra:
            if BASE <= regs['pc'] < BASE + 0x7c0000:
                print("--- pc ---")
                dis(regs['pc'], 8, self.code)
            if BASE <= regs['lr'] < BASE + 0x7c0000:
                print("--- lr (caller) ---")
                dis(regs['lr'] - 8, 6, self.code)
        return regs

    # --- 命令 ---
    def run(self, cmd):
        parts = cmd.split()
        if not parts:
            return True
        op = parts[0].lower()
        a = (lambda i, d=None: int(parts[i], 0) if len(parts) > i else d)

        if op == 'bp':
            print("  Z0 ->", self.c.set_break(a(1)))
        elif op in ('rbp', 'wbp', 'abp'):
            z = {'rbp': 3, 'wbp': 2, 'abp': 4}[op]
            print("  Z%d ->" % z, self.c.cmd('Z%d,%x,4' % (z, a(1))))
        elif op == 'dbp':
            print("  z0 ->", self.c.clear_break(a(1)))
        elif op == 'c':
            secs = a(1, 25)
            self.c.sock.settimeout(secs)
            try:
                rep = self.c.cmd('c')
            except Exception as e:
                print("  (no stop in %ss: %s)" % (secs, e))
                self.pending = True
                return True
            if rep in ('OK', ''):
                print("  (still running)")
                self.pending = True
                return True
            self.pending = False
            self.show_stop(rep)
        elif op == 'go':
            self.c.send('c', wait_ack=False)
            self.pending = True
            print("  (continuing, no wait)")
            if len(parts) > 1:
                time.sleep(a(1))
        elif op == 'poll':
            secs = a(1, 10)
            self.c.sock.settimeout(secs)
            try:
                rep = self.c.recv_packet()
            except Exception as e:
                print("  (no stop in %ss)" % secs)
                return True
            self.pending = False
            self.show_stop(rep)
        elif op == 'int':
            self.c.send('\x03', wait_ack=False)
            time.sleep(0.4)
            try:
                self.c.sock.settimeout(5)
                rep = self.c.recv_packet()
                self.pending = False
                self.show_stop(rep)
            except Exception as e:
                print("  (no stop after int: %s)" % e)
        elif op == 'regs':
            print(regs_line(self.c.read_registers()))
        elif op == 'mem':
            addr, ln = a(1), a(2, 64)
            d = self.c.read_mem(addr, ln)
            for i in range(0, ln, 16):
                row = d[i:i + 16]
                print("    %#010x: %-47s %s" % (addr + i, row.hex(' '),
                                                ''.join(chr(x) if 32 <= x < 127 else '.' for x in row)))
        elif op == 'dump':
            addr, ln, path = a(1), a(2), parts[3]
            d = self.c.read_mem(addr, ln)
            open(path, 'wb').write(d)
            print("    wrote %d bytes -> %s" % (len(d), path))
        elif op == 'str':
            addr = a(1)
            d = self.c.read_mem(addr, 96)
            print("    %r" % d.split(b'\x00')[0])
        elif op == 'x':
            dis(a(1), a(2, 12), self.code)
        elif op == 'fn':
            dis(a(1), a(2, 40), self.code)
        elif op == 'threads':
            self.c.send('qXfer:threads:read::0,4000')
            print("  ", re.findall(r'<thread id="(\d+)"[^>]*name="([^"]*)"', self.c.recv_packet()))
        elif op == 'tid':
            self.c.send('H g' + parts[1])
            try:
                self.c.recv_packet()
            except Exception:
                pass
            print("  switched")
        elif op == 'sleep':
            time.sleep(a(1, 1))
        elif op in ('quit', 'q'):
            return False
        else:
            print("  ? unknown command:", cmd)
        return True

    def close(self):
        self.c.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=24689)
    ap.add_argument('-c', '--commands', default='')
    ap.add_argument('-f', '--file')
    ap.add_argument('--fifo', help='持久会话：从命名管道逐行读命令（推荐，断点不丢）')
    ap.add_argument('--code', default=os.environ.get('NLP_CODE_UNPACKED', ''))
    args = ap.parse_args()

    cmds = []
    if args.file:
        cmds += [l.strip() for l in open(args.file) if l.strip() and not l.strip().startswith('#')]
    if args.commands:
        cmds += [c.strip() for c in args.commands.split(';') if c.strip()]

    s = Session(args.port, args.code or None)
    print("[i] connected; initial stop: %r" % s.c.stop_reply[:60], flush=True)
    try:
        if args.fifo:
            # O_RDWR 持有写端 → readline 永不返回 EOF，可以长期挂着
            fd = os.open(args.fifo, os.O_RDWR | os.O_NONBLOCK)
            os.set_blocking(fd, True)
            f = os.fdopen(fd, 'r')
            open('/tmp/gdb_session.pid', 'w').write(str(os.getpid()))
            print("[i] fifo mode pid=%d: echo 'CMD' > %s" % (os.getpid(), args.fifo), flush=True)
            while True:
                line = f.readline()
                if not line:
                    continue
                line = line.strip()
                if not line:
                    continue
                print("\n>>> %s" % line, flush=True)
                if not s.run(line):
                    break
        else:
            for cmd in cmds:
                print("\n>>> %s" % cmd, flush=True)
                if not s.run(cmd):
                    break
    finally:
        s.close()
    print("\n[OK] session closed")


if __name__ == '__main__':
    main()
