#!/usr/bin/env python3
"""G.722.1（Siren14 同族）解码器：位流解析（帧 → MLT 系数）。

移植自 FFmpeg 6.1.1 libavcodec/siren.c（与 ITU-T G.722.1 参考实现同源），
用于解 New Love Plus+ 的 Siren14Voice.spp。合成（逆 MLT + 窗 + 重叠相加）在
`siren_transform.py`；端到端驱动在 `siren14_wav.py`。

参数档：模块默认 = FFmpeg 的 16 kHz 支（14 区域 / 320 样本）；本作用
`siren14.configure()` 切到 32 kHz 支（28 区域 / 640 样本 / 5 bit 速率控制）。

帧格式（NLP+ 实测）：18400 bps、20 ms、46 字节 = 368 bit。
位序：游戏按 16 位小端字读入、从 bit15 向下取（= 16 位字节交换后 MSB-first）。
差异与依据见 memory/loveplus/reverse_code_bin.md §5c/§5d/§5e/§5f。

与 ITU-T G.722.1 官参实现逐系数对照后修正的三处（memory §5e/§5f）：
噪声幅度与编码系数同单位（x SCALE_FACTOR）、dw 状态跨帧持续、噪声符号位按相邻 10 系数分块。
"""
import numpy as np

from siren_tables import (INDEX_TABLE, VECTOR_DIMENSION, NUMBER_OF_VECTORS,
                          EXPECTED_BITS_TABLE, DIFFERENTIAL_DECODER_TREE,
                          DECODER_TREES, DECODER_TABLES_ELEMENTS, MLT_QUANT)

# 解码参数档：模块默认 = FFmpeg 的 G.722.1 16 kHz 支（14 区域 / 320 样本）；
# 本作 Siren14 用 configure(...) 切到 32 kHz 支（28 区域 / 640 样本 / 5 bit 速率控制）。
FRAME_SIZE = 320          # 每帧样本数 = 每帧系数个数（16 kHz / 20 ms）
REGION_SIZE = 20          # 每区域系数个数（各码类均为 20，见 memory §5e）
NUMBER_OF_REGIONS = 14
ESF_ADJUSTMENT = 7
SCALE_FACTOR = 22

# 游戏噪声填充平台值（code.bin 表 0x8bf98c，Q15）：类别 5/6/7 各一个固定系数。
# 游戏里编码系数 = (mlt_quant_Q12 x std) >> 12、噪声 = (tbl_Q15 x std) >> 15，二者同单位；
# 本实现给编码系数乘了 SCALE_FACTOR，噪声必须同乘，否则噪声低 22x（约 -27 dB）。
# 与 ITU-T G.722.1 官参 decoder.c 的 noise_fill_factor[3] = {5793, 8192, 23170} 一致。
GAME_NOISE_TBL = {5: 5793 / 32768.0, 6: 8192 / 32768.0, 7: 23170 / 32768.0}

RATE_CONTROL_BITS = 4     # 14 区域支 4 bit；28 区域支 5 bit
RATE_CONTROL_POSSIBILITIES = 1 << RATE_CONTROL_BITS
CHECKSUM_BITS = 0         # 非 MSN 路径为 0（FFmpeg 语义）
SAMPLE_RATE = 16000       # 输出采样率（本作 32000）

# 本作 code.bin 0x801d34 的 std_dev 表只有 54 项（arp −24..+29），值是 round(std) 的 Q0 整数，
# 与下面这条 FFmpeg 公式逐项相符（最大偏差 0.5）；FFmpeg 表有 64 项（−24..+39）。
GAME_ARP_MAX = 29

# 本作 categorize 前的可用位数上限（FFmpeg 无此步；18400 bps / 368 bit 帧下不触发）。
AVAIL_CAP = True

# 解码诊断计数（driver 打印；越界/异常路径应恒为 0）。
STATS = {'arp_gt_game_max': 0, 'rc_skip7': 0}

# FFmpeg: region_power = 10^((i-24)*0.3010299957)，std = sqrt(region_power)
STANDARD_DEVIATION = [float(np.sqrt(10.0 ** ((i - 24) * 0.3010299957))) for i in range(64)]


def configure(nregions=28, frame_size=None, rate_control_bits=None, sample_rate=None):
    """切换解码参数档：本作 Siren14 = configure()，即 28 区域 / 640 样本 / 32 kHz / 5 bit。

    帧长与区域数的关系沿用本作：FRAME_SIZE = 320·nregions/14（区域只编码 20·nregions
    个系数，其余高频系数为 0，见 memory §5e/§5f）。FFmpeg 只实现 14 区域一支。
    """
    global NUMBER_OF_REGIONS, FRAME_SIZE, RATE_CONTROL_BITS
    global RATE_CONTROL_POSSIBILITIES, SAMPLE_RATE
    NUMBER_OF_REGIONS = int(nregions)
    FRAME_SIZE = int(frame_size) if frame_size else 320 * NUMBER_OF_REGIONS // 14
    RATE_CONTROL_BITS = int(rate_control_bits) if rate_control_bits else (
        4 + int(max(0, round(np.log2(NUMBER_OF_REGIONS / 14.0)))))
    RATE_CONTROL_POSSIBILITIES = 1 << RATE_CONTROL_BITS
    SAMPLE_RATE = int(sample_rate) if sample_rate else 16000 * FRAME_SIZE // 320
    return dict(nregions=NUMBER_OF_REGIONS, frame_size=FRAME_SIZE,
                rate_control_bits=RATE_CONTROL_BITS, rate_control_possibilities=RATE_CONTROL_POSSIBILITIES,
                sample_rate=SAMPLE_RATE)


def swap16(data: bytes) -> bytes:
    """16 位字节交换：把 16-bit 小端字流化成 MSB-first 可读的字节流。"""
    b = bytearray(data)
    b[0::2], b[1::2] = data[1::2], data[0::2]
    return bytes(b)


class BitReader:
    """MSB-first 位读取器（输入需已是正确的字节序）。"""

    def __init__(self, data: bytes, nbits: int = None):
        self.data = data
        self.nbits = len(data) * 8 if nbits is None else nbits
        self.pos = 0

    def bits_left(self):
        return self.nbits - self.pos

    def get_bits(self, n: int) -> int:
        v = 0
        p = self.pos
        for _ in range(n):
            v = (v << 1) | ((self.data[p >> 3] >> (7 - (p & 7))) & 1)
            p += 1
        self.pos = p
        return v

    def get_bits1(self) -> int:
        v = (self.data[self.pos >> 3] >> (7 - (self.pos & 7))) & 1
        self.pos += 1
        return v

    def show_bits1(self) -> int:
        return (self.data[self.pos >> 3] >> (7 - (self.pos & 7))) & 1


def _clip_u3(i):
    return 0 if i < 0 else (7 if i > 7 else i)


def _clip(a, lo, hi):
    return lo if a < lo else (hi if a > hi else a)


def decode_envelope(br, nregions, esf_adjustment=ESF_ADJUSTMENT):
    """返回 (arp, std)。arp 为绝对区域功率指数（-24..39）。"""
    arp = [0] * nregions
    std = [0.0] * nregions
    arp[0] = _clip(br.get_bits(5) - esf_adjustment, -24, 39)
    std[0] = STANDARD_DEVIATION[arp[0] + 24]
    for i in range(1, nregions):
        index = 0
        while True:
            if br.bits_left() < 4 + nregions - i + CHECKSUM_BITS:
                raise ValueError('envelope: out of bits')
            index = DIFFERENTIAL_DECODER_TREE[i - 1][index][br.get_bits1()]
            if not index > 0:
                break
        arp[i] = _clip(arp[i - 1] - index - 12, -24, 39)
        std[i] = STANDARD_DEVIATION[arp[i] + 24]
    for a in arp:
        if a > GAME_ARP_MAX:
            STATS['arp_gt_game_max'] += 1
    return arp, std


def categorize_regions(nregions, available_bits, arp):
    """区域比特分配。返回 (power_categories, category_balance)。"""
    offset = -32
    power_categories = [0] * nregions
    delta = 32
    while nregions > 0 and delta > 0:
        expected = 0
        for region in range(nregions):
            i = _clip_u3((delta + offset - arp[region]) >> 1)
            power_categories[region] = i
            expected += EXPECTED_BITS_TABLE[i]
        if expected >= available_bits - 32:
            offset += delta
        delta //= 2

    expected = 0
    max_rate_categories = [0] * nregions
    for region in range(nregions):
        i = _clip_u3((offset - arp[region]) >> 1)
        max_rate_categories[region] = i
        power_categories[region] = i
        expected += EXPECTED_BITS_TABLE[i]

    min_rate_categories = list(max_rate_categories)
    mn = mx = expected
    temp_category_balances = [0] * 64
    min_ptr = max_ptr = RATE_CONTROL_POSSIBILITIES
    for _ in range(RATE_CONTROL_POSSIBILITIES - 1):
        if mn + mx > available_bits * 2:
            raw_value = -99
            raw_min_idx = 0
            for region in range(nregions - 1, -1, -1):
                if min_rate_categories[region] < 7:
                    temp = offset - arp[region] - 2 * min_rate_categories[region]
                    if temp > raw_value:
                        raw_value = temp
                        raw_min_idx = region
            if raw_value == -99:
                raise ValueError('categorize: no min')
            temp_category_balances[min_ptr] = raw_min_idx
            min_ptr += 1
            mn += (EXPECTED_BITS_TABLE[min_rate_categories[raw_min_idx] + 1]
                   - EXPECTED_BITS_TABLE[min_rate_categories[raw_min_idx]])
            min_rate_categories[raw_min_idx] += 1
        else:
            raw_value = 99
            raw_max_idx = 0
            for region in range(nregions):
                if max_rate_categories[region] > 0:
                    temp = offset - arp[region] - 2 * max_rate_categories[region]
                    if temp < raw_value:
                        raw_value = temp
                        raw_max_idx = region
            if raw_value == 99:
                raise ValueError('categorize: no max')
            max_ptr -= 1
            temp_category_balances[max_ptr] = raw_max_idx
            mx += (EXPECTED_BITS_TABLE[max_rate_categories[raw_max_idx] - 1]
                   - EXPECTED_BITS_TABLE[max_rate_categories[raw_max_idx]])
            max_rate_categories[raw_max_idx] -= 1

    for region in range(nregions):
        power_categories[region] = max_rate_categories[region]
    balance = [temp_category_balances[max_ptr + i] for i in range(RATE_CONTROL_POSSIBILITIES - 1)]
    return power_categories, balance


class _DwGen:
    """FFmpeg get_dw() 等价的伪随机序列（噪声填充用）。"""

    def __init__(self):
        self.dw1 = self.dw2 = self.dw3 = self.dw4 = 1

    def get(self):
        ret = self.dw1 + self.dw4
        if ret & 0x8000:
            ret += 1
        self.dw1, self.dw2, self.dw3, self.dw4 = self.dw2, self.dw3, self.dw4, ret
        return ret


# 游戏把 dw 状态存在解码器对象上（`dec+0x1420+slot*16`），跨帧连续；ITU 参考的 `randobj`
# 同样跨帧（`get_rand` 状态在解码器里延续）。故用模块级状态，一条语音流解完再 reset_dw()。
DW_PERSIST = True
_DW_STATE = None


def reset_dw():
    """每条语音流开始时重置（游戏初始状态 1,1,1,1）。"""
    global _DW_STATE
    _DW_STATE = _DwGen()


def decode_vector(br, nregions, std, power_categories, dw: _DwGen):
    """解出 320 个 MLT 系数（float，未乘 MDCT scale）。"""
    coefs = np.zeros(FRAME_SIZE, dtype=np.float64)
    error = False
    for region in range(nregions):
        category = power_categories[region]
        base = region * REGION_SIZE
        if 0 <= category < 7:
            tree = DECODER_TREES[category]
            nel = DECODER_TABLES_ELEMENTS[category]
            for _ in range(NUMBER_OF_VECTORS[category]):
                index = 0
                while True:
                    if br.bits_left() - CHECKSUM_BITS <= 0:
                        error = True
                        break
                    if index + br.show_bits1() >= nel:
                        error = True
                        break
                    index = tree[index + br.get_bits1()]
                    if index & 1:          # 奇数 = 叶节点，结束
                        break
                index >>= 1
                if error:
                    break
                for _j in range(VECTOR_DIMENSION[category]):
                    dv = MLT_QUANT[category][index & ((1 << INDEX_TABLE[category]) - 1)]
                    index >>= INDEX_TABLE[category]
                    if dv:
                        if br.bits_left() - CHECKSUM_BITS <= 0:
                            error = True
                            break
                        if br.get_bits1():
                            dv *= std[region]
                        else:
                            dv *= -std[region]
                    coefs[base] = dv * SCALE_FACTOR
                    base += 1
            if error:
                for j in range(region + 1, nregions):
                    power_categories[j] = 7
                category = 7
        # 噪声填充：平台值 x SCALE_FACTOR（与编码系数同单位）
        base = region * REGION_SIZE
        noise = std[region] * GAME_NOISE_TBL[category] * SCALE_FACTOR if category in (5, 6, 7) else 0.0
        if category in (5, 6, 7):
            # 参考实现（decoder.c）取两次随机数、各覆盖**相邻** 10 个系数（0-9 / 10-19）；
            # FFmpeg 写成 dw1/dw2 偶奇交错，与编码端位序不符 -> 按参考分块。
            for _half in range(2):
                bits = dw.get()
                for _j in range(10):
                    if category == 7 or coefs[base] == 0:
                        coefs[base] = noise if (bits & 1) else -noise
                    base += 1
                    bits >>= 1
    return coefs


def _apply_avail_cap(avail):
    """本作 categorize 前的可用位数上限：cap = 320·(nregions//14)，超出部分按 5/8 计。

    FFmpeg 无此步（直接用 bits_left）。368 bit 帧下 avail ≈ 250 远小于 cap = 640，不触发。
    """
    if not AVAIL_CAP:
        return avail
    cap = 320 * max(1, NUMBER_OF_REGIONS // 14)
    return cap + (avail - cap) * 5 // 8 if avail > cap else avail


def decode_frame(frame: bytes, bit_order='game', avail_margin=0):
    """解一帧（46 字节 / 368 bit）→ (arp, power_categories, 系数数组[FRAME_SIZE])。

    系数 = mlt_quant × ±std[region] × SCALE_FACTOR（FFmpeg 口径）；合成时用
    `siren_transform.Synthesizer(out_scale=1/(22*32768))` 抵掉这两个因子。区域只覆盖
    前 20·nregions 个系数，其余高频系数保持 0（14 kHz 带宽上限，见 memory §5e/§5f）。
    """
    data = swap16(frame) if bit_order == 'game' else frame   # 'be' = 标准 MSB-first 字节流
    br = BitReader(data, len(frame) * 8)
    arp, std = decode_envelope(br, NUMBER_OF_REGIONS)
    rate_control = br.get_bits(RATE_CONTROL_BITS)
    avail = _apply_avail_cap(br.bits_left() - avail_margin)
    power_categories, balance = categorize_regions(NUMBER_OF_REGIONS, avail, arp)
    for i in range(rate_control):
        idx = balance[i]
        if power_categories[idx] < 7:   # 本作：已达 7 的区域跳过（FFmpeg 不加守卫）
            power_categories[idx] += 1
        else:
            STATS['rc_skip7'] += 1
    global _DW_STATE
    if _DW_STATE is None:
        _DW_STATE = _DwGen()
    dw = _DW_STATE if DW_PERSIST else _DwGen()
    coefs = decode_vector(br, NUMBER_OF_REGIONS, std, power_categories, dw)
    return arp, power_categories, coefs
