#!/usr/bin/env python3
"""MLT 合成层：逆 MLT + 正弦窗 + 重叠相加（G.722.1 / Siren14 同族解码的最后一步）。

数学定义（N = 每帧样本数 = 每帧系数个数；窗长 2N；相邻帧重叠一半，hop = N）：

    y[n] = Σ_{k=0}^{N-1} X[k]·cos(π/N·(n + 0.5 + N/2)·(k + 0.5))     n = 0..2N-1
    w[n] = sin((n + 0.5)·π/(2N))
    pcm[m] = w[m]·y_k[m] + w[N+m]·y_{k-1}[N+m]                       m = 0..N-1

窗满足 w[n]² + w[n+N]² = 1，与 MLT 分析端（`forward_mlt`）构成完美重构；`selftest()`
用量级 1e-7（float32 基矩阵）的往返误差验证。N = 640 即本作 Siren14（32 kHz），N = 320 即
FFmpeg 的 G.722.1（16 kHz），窗式与 FFmpeg `window[i] = sinf((i+0.5)*M_PI_2/320)` 相同
（本作窗表拟合式 G·sin((k+0.5)π/1280)，即 Malvar MLT 的 2N = 1280 正弦窗）。

相位约定（2026-10-17 定案）：合成端**不对系数做 (−1)^k 翻转**。判据三条——
①分析核 `imlt_basis().T` 与标准 MDCT/MLT 定义式 `cos((2j+1+N)(2k+1)π/(4N))` 逐元素完全一致
（selftest `kernel` = 0）；②`(分析, 合成)` 完美重构（补 2/N 后相对误差 ~1e-7）；
③`synth_folded()`（FFmpeg siren.c 的「折叠输出 + 旋转式重叠相加」排布）在同一系数上与本
实现逐样本一致（~1e-7），且同样不需要翻转。偶下标取负会得到另一条（互相关 ~0）的信号，
属 FFmpeg 通用逆 MDCT codelet 的输入约定（其 naive 参考实现是 prio MIN 的死代码路径），
不作为证据。

依据（静态逆向，见 memory/loveplus/reverse_code_bin.md §5f）：游戏侧 0x75dd2c（定点 IMDCT，
10×2^k 分解）与 0x76b67c（正弦窗 + 重叠相加、保留上一帧尾）语义与上式一致；窗表
0x802954 / 0x802e54 / 0x803354 逐项拟合 w[j] = G·sin((j+0.5)π/(2N))，最大偏差 ≤ 1 LSB。
"""
import numpy as np


def mlt_window(n):
    """MLT 合成窗（2N 项，含上升、下降两半）。"""
    return np.sin((np.arange(2 * n, dtype=np.float64) + 0.5) * np.pi / (2.0 * n))


def imlt_basis(n):
    """逆 MLT 基矩阵 (2N × N)，float64。"""
    m = np.arange(2 * n, dtype=np.float64)[:, None]
    k = np.arange(n, dtype=np.float64)[None, :]
    return np.cos(np.pi / n * (m + 0.5 + n / 2.0) * (k + 0.5))


def forward_mlt(x, n, w=None):
    """MLT 分析端（只用于 selftest 的往返验证）。"""
    if w is None:
        w = mlt_window(n)
    return imlt_basis(n).T @ (w * np.asarray(x, dtype=np.float64))


def out_scale_default(n):
    """默认输出标量：MLT 正交归一 ÷ Q15。

    取 sqrt(2/N)/32768，即「分析端与合成端各 sqrt(2/N)」的教科书正交归一约定，
    再除以 32768 以沿用 FFmpeg 的 Q15 口径（FFmpeg: 系数 ×22 → 逆变换 → ÷(22·32768)，
    净效果即系数按 Q15 解释后过未归一化逆变换）。

    标准/游戏把 2/N 完全放在合成端、还是两端各 sqrt(2/N)，无法从静态代码唯一确定：
    两者相差 sqrt(2/N)（N=640 时 25 dB），属可整体缩放的标量。实测约束：本作素材最响帧的
    未归一化逆变换输出峰值 = 252300，整体标量只要大于约 1/7.7 就必然削波，故取 sqrt(2/N)
    （对应峰值 0.43、RMS 0.10，无削波）。需要对齐游戏混音电平时用 `--gain` 整体缩放。
    """
    return float(np.sqrt(2.0 / n) / 32768.0)


class Synthesizer:
    """逐帧逆 MLT + 重叠相加；内部保存上一帧尾部 w[N:]·y_{k-1}[N:]。

    out_scale 默认取 `out_scale_default(n)`（见该函数对整体标量的说明）；显式传入
    2/N 可得到与 `forward_mlt`（未归一化分析端）的完美重构。
    """

    def __init__(self, n=640, out_scale=None, dtype=np.float32):
        self.n = int(n)
        self.w = mlt_window(self.n)
        self.basis = imlt_basis(self.n).astype(dtype)
        self.out_scale = out_scale_default(self.n) if out_scale is None else float(out_scale)
        self.tail = np.zeros(self.n, dtype=dtype)

    def reset(self):
        self.tail.fill(0)

    def frame(self, coefs):
        """一帧系数（长度 N）→ N 个 PCM 样本（float64）。"""
        y = self.basis @ np.asarray(coefs, dtype=self.basis.dtype)
        out = (self.w[:self.n] * y[:self.n] + self.tail) * self.out_scale
        self.tail = self.w[self.n:] * y[self.n:]
        return out.astype(np.float64)

    def flush(self):
        """收尾：只输出上一帧尾的贡献（对齐帧数用）。"""
        out = self.tail * self.out_scale
        self.tail = np.zeros(self.n, dtype=self.tail.dtype)
        return out.astype(np.float64)


def decode_voice(coefs_frames, n=640, out_scale=None, dtype=np.float32):
    """[帧数, N] 系数矩阵 → 一维 PCM（帧数 × N 个样本）。"""
    syn = Synthesizer(n, out_scale, dtype)
    return np.concatenate([syn.frame(c) for c in np.asarray(coefs_frames)])


def synth_folded(coefs_frames, n=640, out_scale=None):
    """折叠/旋转式合成：与 `Synthesizer` 逐样本等价的第二种排布（交叉验证用）。

    同样 hop = n、每帧输出 n 个样本，但不做整长（2n）重叠相加，而是只用基矩阵的两块：
    当前帧 KX 的行 0..n/2-1（记 cur）与上一帧 KX 的行 n..3n/2-1（记 prev），
    按 θ_a = (a+0.5)π/(2n) 旋转合并：
      out[a]     = prev[a]·cos θ_a + cur[a]·sin θ_a
      out[n-1-a] = prev[a]·sin θ_a - cur[a]·cos θ_a
    这正是 FFmpeg `libavcodec/siren.c` 的「逆 MDCT 折叠输出 + `vector_fmul_window_c`
    （libavutil/float_dsp.c）旋转式重叠相加」的排布：窗 sin/cos 由同一条
    win[k] = sin((k+0.5)π/(2n)) 取 w[a] 与 w[n-1-a] 得到，本作 0x76b67c 的
    (sin,cos) 对同构。实测（selftest 与 --ref-check）它与 `Synthesizer`
    在同一系数上逐样本一致（相对误差 ~1e-7，float 精度），且同样不需要对系数做
    任何 (−1)^k 翻转——FFmpeg 解码器里对偶数下标的取负属于其通用逆 MDCT 的输入约定，
    与本作/标准 MLT 的合成算子无关。
    """
    n = int(n)
    half = n // 2
    basis = imlt_basis(n)
    w = mlt_window(n)
    sins, coss = w[:half], w[n - half:n][::-1]     # sin θ_a, cos θ_a (a = 0..half-1)
    scale = out_scale_default(n) if out_scale is None else float(out_scale)
    prev = None
    out = []
    for x in np.asarray(coefs_frames, dtype=np.float64):
        kx = basis @ x
        cur = kx[:half]
        fr = np.zeros(n)
        if prev is not None:
            fr[:half] = prev * coss + cur * sins
            fr[n - half:][::-1] = prev * sins - cur * coss
        out.append(fr)
        prev = kx[n:n + half]
    return np.concatenate(out) * scale if out else np.zeros(0)


def boundary_continuity(pcm, n):
    """帧边界跳变诊断：边界处 |Δ| 均值 ÷ 全体 |Δ| 均值。

    重叠相加正确时两端贡献连续，比值 ≈ 1；相位或窗约定错误会让每个帧边界出现跳变（比值 ≫ 1）。
    """
    d = np.abs(np.diff(pcm))
    if d.size == 0:
        return float("nan")
    idx = np.arange(n, len(pcm), n)
    idx = idx[idx < d.size]
    if idx.size == 0:
        return float("nan")
    return float(d[idx].mean() / max(d.mean(), 1e-12))


def selftest(n=640, nframes=6, seed=1):
    """自检，返回 dict：

    - `gain`：无归一化 MLT 对（`forward_mlt` + `Synthesizer(out_scale=1)`）的固有增益，应为 N/2；
    - `exact`：补 2/N 后的相对重构误差（应 ~1e-15）；
    - `kernel`：`forward_mlt` 与标准 MDCT 定义式
      `X[k] = Σ_j w[j]x[j]·cos((2j+1+N)(2k+1)π/(4N))` 的相对最大偏差（应 ~1e-16）；
    - `folded`：折叠/旋转式 `synth_folded` 与 `Synthesizer` 在同一系数上的相对最大差（应 ~1e-7）。
    """
    rng = np.random.default_rng(seed)
    hop = n
    nsig = (nframes + 2) * hop
    t = np.arange(nsig) / 32000.0
    x = (0.4 * np.sin(2 * np.pi * 440 * t) + 0.2 * np.sin(2 * np.pi * 1310 * t)
         + 0.05 * rng.standard_normal(nsig))
    w = mlt_window(n)
    coefs = np.array([forward_mlt(x[s:s + 2 * n], n, w) for s in range(0, nsig - 2 * n + 1, hop)])
    ref = np.concatenate([x[k * hop:(k + 1) * hop] for k in range(1, len(coefs))])
    rms = float(np.sqrt((ref ** 2).mean()))

    def interior(pcm):
        return np.concatenate([pcm[k * hop:(k + 1) * hop] for k in range(1, len(coefs))])

    raw = decode_voice(coefs, n, out_scale=1.0, dtype=np.float64)
    exact = interior(decode_voice(coefs, n, out_scale=2.0 / n))
    a2 = (2.0 * np.arange(2 * n) + 1.0 + n)
    kern = np.cos(np.outer(a2 * (np.pi / (4.0 * n)), 2.0 * np.arange(n) + 1.0))
    kerr = float(np.abs(kern.T @ (w * x[:2 * n]) - coefs[0]).max() / np.abs(coefs[0]).max())
    return dict(
        n=n,
        gain=float(np.sqrt((interior(raw) ** 2).mean()) / rms),
        exact=float(np.sqrt(((ref - exact) ** 2).mean()) / rms),
        kernel=kerr,
        window_orth=float(np.abs(mlt_window(n)[:n] ** 2 + mlt_window(n)[n:] ** 2 - 1).max()),
        folded=float(np.sqrt(((interior(raw) - interior(synth_folded(coefs, n, out_scale=1.0))) ** 2).mean()) / rms),
    )


if __name__ == '__main__':
    import sys
    keys = ['%s=%.3e' % (k, v) for k, v in selftest(640).items() if k != 'n']
    print('selftest N=640: ' + '  '.join(keys))
    print('       默认输出标量 sqrt(2/N)/32768 = %.6e（peak_raw·scale = 可听电平）' % out_scale_default(640))
