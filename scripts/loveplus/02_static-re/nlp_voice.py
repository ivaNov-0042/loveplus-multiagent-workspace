#!/usr/bin/env python3
"""
New Love Plus (3DS) — 语音索引 / 映射链解析工具

已坐实的链路:
    conditionvoice_<角色>.lmb   (zlib, 12B 记录: flag / voice_id / 0xFFFFFFFF 分隔)
        -> voice_id  = Siren14voice.bin 的【直接索引】(无二级映射)
        -> Siren14voice.bin[id] = (offset, size) u32 LE x2
        -> Siren14Voice.spp[offset : offset+size] = G.722.1 帧码流

角色 <-> 脚本前缀 (由 .spgdat 实证, 非推测):
    a*  = 宁宁  Nene     (Nene.spgdat)
    k*  = 凛子  Rinko    (Rinko.spgdat)
    t*  = 爱花  Manaka   (Manaka.spgdat)
    p*  = 主角
    t88 = 三方共有 (公共脚本)

结构体:
  PACK 容器 (gdkchan/NLPUnpacker Program.cs):
      @0x00 'PACK'
      @0x04 u32  FileCount = 值>>16
      @0x08 u32  StringPointersOffset  (+BaseOffset)
      @0x0C u32  StringTableOffset     (+BaseOffset)
      @0x10 u32  DataOffset            (+BaseOffset)
      @0x14 u32  DecompressedSectionLength
      @0x18 u32  CompressedSectionLength
      @0x1C u32  Padding
      @0x20 + i*0x20 文件条目 (0x20B/条):
              +0x00 char[4] FileSignature
              +0x04 u32 Unknown0
              +0x08 u32 DecompressedLength
              +0x0C u32 DecompressedOffset (+BaseOffset)
              +0x10 u32 Unknown1
              +0x14 u32 Flags          (bit0 = IsCompressed)
              +0x18 u32 CompressedLength
              +0x1C u32 CompressedOffset (+BaseOffset)
      文件名: *(StringPointersOffset + i*4) -> StringTableOffset + 偏移, NUL 结尾
      注意: 有些文件 Flags bit0=0 但内容其实是 zlib 流 (如 .lmb/.twbdat), 需自行判断

  SERI 文件 (YAML 序列化, 原为 .yaml):
      @0x00 'SERI'
      @0x04 u32  -> ValuesOffset = 值 + 4
      @0x08 u16  ParametersCount
      @0x0A  ParametersCount * { u16 NameOffset, u16 ValueOffset }
      TypesTable @ ValuesOffset - ParametersCount  (每参数 1 字节类型码)
      Values      @ ValuesOffset
      字符串解析在【PACK 的 StringTableOffset】(ROM 缓冲) 里, 不在 SERI 文件内!
      类型码: 's'=字符串 'i'=int32 'f'=float 'b'=bool 'a'=数组 'h'=嵌套数组
      +版扩展: 参数值 == 'TEXI'(0x49584554) 的是纹理描述, 不是文本索引

  .mdc 邮件词典 (UTF-8 明文日文):
      记录 = 0x00 <len u8> <UTF-8 len 字节> 0x00, 记录间用 0xffff + c1/c2/fe 标志簇 + 00 填充
      该标志簇低字节为比特域(一热编码的桶号), 属索引结构的一部分

  conditionvoice_<0|1|2>.lmb  【核心: 条件语音索引表】
      zlib 解压后: @0x00 u32 Count(=记录数), 随后 Count 条 12 字节记录:
          u32 flag        高16位 = 条件组 id (0x0001, 0x0104, 0x0105 ... 严格递增)
                         低16位 = 组内序号 (1,2,3 ... 严格连续)
          u32 voice_id    Siren14voice.bin 直接索引; 同组内严格 +1 递增
          u32 terminator  0xFFFFFFFF 分隔 (或 0)
      实测: 207 条 / 31 组, 组内 voice_id 连号 (如 0x2a16..0x2a1a, 0x2a1b..0x2a1f)
"""
import os, re, sys, json, zlib, struct, argparse, collections

ROM_DEFAULT = 'data/loveplus/roms_patched/NLP_plus_patched.3ds'
AUDIO_DIR   = 'data/loveplus/nlp_plus/audio'

CHARACTERS = {'0': 'Nene(宁宁)', '1': 'Rinko(凛子)', '2': 'Manaka(爱花)'}
PREFIX_CHAR = {'a': 'Nene(宁宁)', 'k': 'Rinko(凛子)', 't': 'Manaka(爱花)', 'p': '主角'}

# ---------------- PACK 容器 ----------------

def extract_package(buf, base):
    """返回 [(name, data), ...] 或 None。所有偏移按 gdkchan/NLPUnpacker 的定义。"""
    if buf[base:base+4] != b'PACK':
        return None
    if base + 0x20 > len(buf):
        return None
    file_count = struct.unpack_from('<I', buf, base+4)[0] >> 16
    if not (0 < file_count <= 100000):
        return None
    spo = struct.unpack_from('<I', buf, base+8)[0] + base
    sto = struct.unpack_from('<I', buf, base+12)[0] + base
    files = []
    try:
        for i in range(file_count):
            e = base + 0x20 + i*0x20
            if e + 0x20 > len(buf):
                break
            declen  = struct.unpack_from('<I', buf, e+8)[0]
            deco    = struct.unpack_from('<I', buf, e+12)[0] + base
            flags   = struct.unpack_from('<I', buf, e+20)[0]
            complen = struct.unpack_from('<I', buf, e+24)[0]
            compo   = struct.unpack_from('<I', buf, e+28)[0] + base
            is_comp = (flags & 1) != 0
            fn_off  = struct.unpack_from('<I', buf, spo + i*4)[0]
            end = buf.find(b'\x00', sto + fn_off)
            name = buf[sto+fn_off:end].decode('ascii', 'replace')
            if is_comp and complen > 0:
                try:
                    data = zlib.decompress(buf[compo:compo+complen], -15)
                except Exception:
                    data = buf[compo:compo+complen]
            else:
                data = buf[deco:deco+declen]
                # 部分文件 Flags bit0=0 但实际是 zlib 流
                if data[:2] == b'\x78\x9c':
                    try:
                        data = zlib.decompress(data)
                    except Exception:
                        pass
            files.append((name, data))
    except Exception:
        pass
    return files


class Rom:
    def __init__(self, path=ROM_DEFAULT):
        self.path = path
        self.buf = open(path, 'rb').read()
        self._index = None

    def iter_packages(self):
        i = self.buf.find(b'PACK')
        while i >= 0:
            files = extract_package(self.buf, i)
            if files:
                yield i, files
            i = self.buf.find(b'PACK', i+1)

    def find(self, name):
        """返回 (data, pack_offset) 或 (None,-1)"""
        for off, files in self.iter_packages():
            for n, d in files:
                if n == name:
                    return d, off
        return None, -1

    def find_all(self, suffix):
        out = collections.OrderedDict()
        for off, files in self.iter_packages():
            for n, d in files:
                if n.lower().endswith(suffix.lower()) and n not in out:
                    out[n] = (off, d)
        return out


# ---------------- conditionvoice_*.lmb ----------------

def parse_lmb(data):
    """12 字节记录: {u32 flag, u32 _mid, u32 voice_id}，另有一对以 0xFFFFFFFF flag 作分隔。
    返回 [(flag, voice_id)]。"""
    if data[:2] == b'\x78\x9c':
        data = zlib.decompress(data)
    if len(data) < 4:
        return []
    recs = []
    off = 4
    while off + 12 <= len(data):
        flag, _mid, voice = struct.unpack_from('<III', data, off)
        recs.append((flag, voice))
        off += 12
    return recs


def build_voice_map(rom):
    """解析三个 conditionvoice_*.lmb，按条件组整理 voice_id。"""
    groups = collections.OrderedDict()
    for idx, name in enumerate(['conditionvoice_0.lmb',
                                'conditionvoice_1.lmb',
                                'conditionvoice_2.lmb']):
        data, pack = rom.find(name)
        if data is None:
            continue
        recs = parse_lmb(data)
        real = [r for r in recs if r[0] != 0xffffffff]
        char = CHARACTERS.get(str(idx), '?')
        for flag, voice in real:
            cond = flag >> 16
            seq  = flag & 0xffff
            groups.setdefault((char, cond), []).append({'seq': seq, 'voice_id': voice})
    return groups


# ---------------- Siren14voice.bin ----------------

# 语音帧长：实测全部 clip 的 size 均能被 46 整除
#   46 B = 45 B 载荷 + 1 B 帧头（16 kHz G.722.1）→ 20 ms/帧 → 2300 B/s
# ⚠️ 勿改回 320 B/帧（理论 16 kHz 帧长）：那会把时长算大约 7 倍。
G7221_FRAME_BYTES = 46
G7221_FRAME_MS    = 20.0

def frames_to_sec(nframes):
    return nframes * G7221_FRAME_MS / 1000.0

def entry_to_sec(size):
    return frames_to_sec(size // G7221_FRAME_BYTES)


class VoiceIndex:
    """Siren14voice.bin: 92655 条 * 8B (offset u32, size u32), offset 单调递增。

    每条 payload = size//46 个 G.722.1 帧，每帧 20 ms。
    """

    def __init__(self, path=None):
        self.path = path or os.path.join(AUDIO_DIR, 'Siren14voice.bin')
        self.data = open(self.path, 'rb').read()
        self.count = len(self.data) // 8
        self.spp_size = os.path.getsize(os.path.join(AUDIO_DIR, 'Siren14Voice.spp'))
        self.spp_path = os.path.join(AUDIO_DIR, 'Siren14Voice.spp')

    def entry(self, voice_id):
        if not (0 <= voice_id < self.count):
            return None
        return struct.unpack_from('<II', self.data, voice_id*8)

    def frames(self, voice_id):
        e = self.entry(voice_id)
        return e[1] // G7221_FRAME_BYTES if e else None

    def duration(self, voice_id):
        """秒。"""
        fr = self.frames(voice_id)
        return frames_to_sec(fr) if fr is not None else None

    def read_frames(self, voice_id):
        e = self.entry(voice_id)
        if not e:
            return None
        off, size = e
        with open(self.spp_path, 'rb') as f:
            f.seek(off)
            return f.read(size)


# ---------------- .mdc 邮件词典 ----------------

def parse_mdc(data):
    """记录 = 0x00 <len u8> <UTF-8 len 字节>。返回去重后的台词列表。"""
    if data[:2] == b'\x78\x9c':
        data = zlib.decompress(data)
    out = []
    i, n = 0, len(data)
    while i < n - 1:
        if data[i] == 0x00:
            L = data[i+1]
            if 1 <= L <= 120:
                seg = data[i+2:i+2+L]
                if len(seg) == L:
                    try:
                        t = seg.decode('utf-8')
                    except Exception:
                        t = None
                    if t and re.search(r'[\u3040-\u30ff\u4e00-\u9fff]', t):
                        t = t.rstrip('\x00').rstrip('\ufffd')
                        if t:
                            out.append(t)
                            i += 2 + L
                            continue
        i += 1
    seen, uniq = set(), []
    for t in out:
        if t not in seen:
            seen.add(t)
            uniq.append(t)
    return uniq


# ---------------- SERI ----------------

def cstr(buf, off):
    end = buf.find(b'\x00', off)
    return buf[off:end].decode('utf-8', 'replace')


def parse_seri(data, rom_buf, string_table_off):
    """SERI -> [(name, type, value)]。字符串在 ROM 缓冲的 string_table_off 处解析。"""
    if data[:4] != b'SERI':
        return []
    vals = struct.unpack_from('<I', data, 4)[0] + 4
    nparams = struct.unpack_from('<H', data, 8)[0]
    types = [chr(data[vals - nparams + k]) for k in range(nparams)]
    out = []
    for p in range(nparams):
        noff = struct.unpack_from('<H', data, 0xa + p*4)[0]
        voff = struct.unpack_from('<H', data, 0xa + p*4 + 2)[0]
        name = cstr(rom_buf, string_table_off + noff)
        t = types[p]
        if t == 'i':
            v = struct.unpack_from('<i', data, vals + voff)[0]
        elif t == 's':
            v = cstr(rom_buf, string_table_off + struct.unpack_from('<H', data, vals+voff)[0])
        else:
            v = '<type %s @%#x>' % (t, vals + voff)
        out.append((name, t, v))
    return out


# ---------------- CLI ----------------

def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    ap.add_argument('--rom', default=ROM_DEFAULT)
    ap.add_argument('--out', default='data/loveplus/nlp_plus/voice_map')
    sub = ap.add_subparsers(dest='cmd', required=True)

    sub.add_parser('voicemap', help='解析 conditionvoice_*.lmb 并导出 voice_id 映射')
    sub.add_parser('verify',  help='验证 voice_id 是否为 Siren14voice.bin 直接索引')
    sub.add_parser('mdc',     help='导出 maildic_*.mdc 台词')
    sub.add_parser('prefix', help='打印角色 <-> 脚本前缀 对应表')
    sub.add_parser('durations', help='按时长(46B/帧,20ms) 统计音库，定位短片段音库(语音引擎候选)')

    a = ap.parse_args()
    rom = Rom(a.rom)
    os.makedirs(a.out, exist_ok=True)

    if a.cmd == 'prefix':
        print('角色 <-> 脚本前缀 (由 .spgdat 实证):')
        for p, c in sorted(PREFIX_CHAR.items()):
            print('  %s* = %s' % (p, c))
        print('  t88 = 三方共有 (公共脚本)')
        return

    if a.cmd == 'durations':
        vi = VoiceIndex()
        ents = [vi.entry(i) for i in range(vi.count)]
        # 完整性: 是否全部能被帧长整除
        bad = [i for i, e in enumerate(ents) if e[1] and e[1] % G7221_FRAME_BYTES]
        print('entries %d ; size %% %d != 0 : %d  (帧长 %d B, %g ms/帧, %g B/s)'
              % (vi.count, G7221_FRAME_BYTES, len(bad),
                 G7221_FRAME_BYTES, G7221_FRAME_MS,
                 G7221_FRAME_BYTES * 1000.0 / G7221_FRAME_MS))
        # 找短片段连续流: size < 3200B(=~1.39s/64帧) 且 连续 >= 250 条
        runs, cur = [], None
        for i, e in enumerate(ents):
            if 0 < e[1] < 3200:
                cur = [i, i] if cur is None else [cur[0], i]
            else:
                if cur and cur[1] - cur[0] >= 250:
                    runs.append(tuple(cur))
                cur = None
        if cur and cur[1] - cur[0] >= 250:
            runs.append(tuple(cur))
        print('\n短片段音库候选 (size<3200B, 连续>=250 条):')
        for lo, hi in runs:
            seg = [ents[i][1] for i in range(lo, hi+1)]
            ds = [entry_to_sec(s) for s in seg]
            gaps = sum(1 for i in range(lo, hi) if ents[i+1][0] != ents[i][0] + ents[i][1])
            print('  %6d-%-6d n=%-5d %.2f-%.2fs (均值 %.2fs) offset间隙=%d %s'
                  % (lo, hi, len(seg), min(ds), max(ds), sum(ds)/len(ds), gaps,
                     '<= 连续流' if gaps == 0 else ''))
        # 对照
        seg = [ents[i][1] for i in range(40000, min(44000, vi.count))]
        ds = [entry_to_sec(s) for s in seg]
        print('\n对照 普通对白 40000-44000: %.2f-%.2fs 均值 %.2fs' % (min(ds), max(ds), sum(ds)/len(ds)))
        return

    if a.cmd == 'mdc':
        idx = {}
        for n, (off, d) in rom.find_all('.mdc').items():
            lines = parse_mdc(d)
            idx[n] = lines
            print('%-18s %4d lines' % (n, len(lines)))
            for t in lines[:5]:
                print('      %s' % t)
        json.dump(idx, open(os.path.join(a.out, 'mdc_lines.json'), 'w'),
                  ensure_ascii=False, indent=1)
        print('saved -> %s' % os.path.join(a.out, 'mdc_lines.json'))
        return

    if a.cmd in ('voicemap', 'verify'):
        groups = build_voice_map(rom)
        vi = VoiceIndex()
        print('Siren14voice.bin: %d entries; spp %d bytes' % (vi.count, vi.spp_size))
        total = 0
        for (char, cond), items in groups.items():
            vids = [x['voice_id'] for x in items]
            valid = [v for v in vids if 0 <= v < vi.count]
            contig = all(vids[k+1] == vids[k]+1 for k in range(len(vids)-1))
            total += len(items)
            print('%-16s cond=%#06x n=%-3d voice %s..%s  contiguous=%-5s  in-range=%d/%d'
                  % (char, cond, len(items), hex(min(vids)), hex(max(vids)),
                     contig, len(valid), len(vids)))
            if a.cmd == 'verify' and valid:
                o, s = vi.entry(valid[0])
                print('        voice_id %d -> spp off=%d size=%d' % (valid[0], o, s))
        print('total records: %d' % total)
        json.dump({'%s|%#06x' % k: v for k, v in groups.items()},
                  open(os.path.join(a.out, 'conditionvoice_map.json'), 'w'),
                  ensure_ascii=False, indent=1)
        print('saved -> %s' % os.path.join(a.out, 'conditionvoice_map.json'))


if __name__ == '__main__':
    main()