#!/usr/bin/env python3
"""极简 GDB Remote Serial Protocol (RSP) 客户端。

用途：连接 azahar 的 GDB stub，做无 gdb 依赖的自动化调试：
设置断点、单步、读寄存器、读内存、dump 内存。

协议要点：
- 发包: $<payload>#<checksum>
- 每包需收 '+' 确认 (除非 NoAck 模式)
- 'c' 继续运行，直到断点/信号，回 'T05...' / 'S05' / 'W00' 等。
"""
import socket
import struct
import sys
import time


class GDBClient:
    def __init__(self, host='127.0.0.1', port=24689, timeout=30.0):
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.sock.settimeout(timeout)
        self.buf = b''
        # 协商：非扩展模式，然后发送 '?' 选取主进程与线程。
        self.cmd('qSupported:multiprocess+')
        self.stop_reply = self.cmd('?')

    @staticmethod
    def _checksum(payload: bytes) -> int:
        return sum(payload) & 0xFF
    def send(self, payload: str, wait_ack=True):
        p = payload.encode()
        pkt = b'$' + p + b'#' + f'{self._checksum(p):02x}'.encode()
        self.sock.sendall(pkt)
        if wait_ack:
            ack = self._recv_exact(1)
            # '+' 表示已接收；'$' 说明无 ack 模式直接回了响应（本 stub 有 ack）
            if ack == b'$':
                self.buf = b'$'  # 视为响应开头

    def _recv_exact(self, n: int) -> bytes:
        out = b''
        while len(out) < n:
            chunk = self.sock.recv(n - len(out))
            if not chunk:
                raise ConnectionError('connection closed')
            out += chunk
        return out

    def recv_packet(self) -> str:
        # 读取直到收到完整的 $...#xx
        while True:
            if b'$' in self.buf:
                start = self.buf.index(b'$')
                # 找 '#' + 2 校验
                h = self.buf.find(b'#', start)
                if h >= 0 and len(self.buf) >= h + 3:
                    payload = self.buf[start + 1:h]
                    self.buf = self.buf[h + 3:]
                    # 回 ack
                    try:
                        self.sock.sendall(b'+')
                    except OSError:
                        pass
                    return payload.decode('latin1')
                # 不够，继续读
            chunk = self.sock.recv(4096)
            if not chunk:
                raise ConnectionError('connection closed')
            self.buf += chunk

    def cmd(self, payload: str) -> str:
        self.send(payload)
        return self.recv_packet()

    # --- 高层封装 ---
    def read_registers(self):
        """g 包：返回 ARM 寄存器组 (r0-r15, 外加 fp regs 与 fpscr 等)。"""
        hexs = self.cmd('g')
        # 前 16 个 int = r0..pc；ARM 下 r13=sp, r14=lr, r15=pc
        raw = bytes.fromhex(hexs)
        regs = {}
        names = ['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10', 'r11',
                 'r12', 'sp', 'lr', 'pc']
        for i, name in enumerate(names):
            if (i + 1) * 4 <= len(raw):
                regs[name] = struct.unpack('<I', raw[i * 4:i * 4 + 4])[0]
        # CPSR 紧随 16 个通用寄存器之后 (offset 16*4)
        if len(raw) >= 16 * 4 + 4:
            regs['cpsr'] = struct.unpack('<I', raw[16 * 4:16 * 4 + 4])[0]
        return regs

    def is_thumb(self) -> bool:
        """由 CPSR 的 T 位(bit5)判断当前是否 Thumb 模式。"""
        return bool(self.read_registers().get('cpsr', 0) & 0x20)

    def read_mem(self, addr: int, length: int) -> bytes:
        out = b''
        while length > 0:
            n = min(length, 0x400)
            resp = self.cmd(f'm{addr:x},{n:x}')
            if resp.startswith('E'):
                raise RuntimeError(f'read_mem error at {addr:#x}: {resp}')
            out += bytes.fromhex(resp)
            addr += n
            length -= n
        return out

    def write_mem(self, addr: int, data: bytes):
        resp = self.cmd(f'M{addr:x},{len(data):x}:' + data.hex())
        if resp != 'OK':
            raise RuntimeError(f'write_mem failed: {resp}')

    def set_break(self, addr: int) -> str:
        return self.cmd(f'Z0,{addr:x},4')

    def clear_break(self, addr: int) -> str:
        return self.cmd(f'z0,{addr:x},4')

    def continue_(self) -> str:
        return self.cmd('c')

    def step(self) -> str:
        return self.cmd('s')

    def read_pc(self) -> int:
        return self.read_registers()['pc']

    def close(self):
        try:
            self.send('D', wait_ack=False)
        except OSError:
            pass
        self.sock.close()


def demo(port):
    c = GDBClient(port=port)
    # 连接即处于 halt 状态
    regs = c.read_registers()
    print("PC on connect = 0x%08x" % regs['pc'])
    print("r0=0x%08x sp=0x%08x lr=0x%08x" % (regs['r0'], regs['sp'], regs['lr']))
    # 单步 5 次
    for i in range(5):
        r = c.step()
        regs = c.read_registers()
        print("step %d: status=%s pc=0x%08x" % (i, r[:8], regs['pc']))
    c.close()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 24689
    demo(port)
