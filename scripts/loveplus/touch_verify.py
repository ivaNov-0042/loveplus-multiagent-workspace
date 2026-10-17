#!/usr/bin/env python3
"""验证脚本化触摸是否真的到达 guest：
在模拟器运行中通过 GDB stub 读取 HID 共享内存的 touch 区，检查 pressed/x/y。
"""
import os
import re
import struct
import subprocess
import sys
import time

from common_paths import *
from rsp_client import GDBClient

PORT = 24755


def le_hex(s):
    b = bytes.fromhex(s)
    b += b'\x00' * (-len(b) % 4)
    return int.from_bytes(b[:4], 'little')


def connect(port, tries=60):
    last = None
    for _ in range(tries):
        try:
            return GDBClient(port=port, timeout=20)
        except OSError as e:
            last = e
            time.sleep(0.5)
    raise last


def main():
    script = ('110000:60:0:0.5:0.57')
    log = open('/tmp/touch.log', 'wb')
    proc = subprocess.Popen(
        [H, R, '--gdb', '--port', str(PORT), '--frames', '200000',
         '--input-script', script, '--dump-every', '500', '--dump-prefix', '/tmp/tch'],
        stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
    try:
        time.sleep(12)
        c = connect(PORT)
        c.send('c', wait_ack=False)

        # HID shared memory physical address is fixed: 0x1EC20000. touch data begins at 0x1EC20000+0xA8? 
        # Instead, find it via the HID process mapping is complex; use known layout:
        # HID SharedMem base = 0x1EC20000; touch entries start at offset 0xA8, each entry 8 bytes? 
        # Actually azahar hid.cpp uses SharedMem struct. We'll just scan a range for our coords.
        time.sleep(6)  # let it reach the menu
        # sample repeatedly, dump around 0x1EC200A8
        for _ in range(6):
            c.send('\x03', wait_ack=False)
            time.sleep(0.3)
            try:
                c.sock.settimeout(2)
                c.sock.recv(4096)
            except Exception:
                pass
            try:
                data = c.read_mem(0x1EC20000, 0x100)
                # print touch-ish region 0xA8..0xF0
                print("hid[0x20..0x60]:", data[0x20:0x60].hex())
                print("hid[0xA8..0xE8]:", data[0xA8:0xE8].hex())
            except Exception as e:
                print("mem err", e)
            c.send('c', wait_ack=False)
            time.sleep(2.0)
        c.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        log.close()


if __name__ == '__main__':
    main()
