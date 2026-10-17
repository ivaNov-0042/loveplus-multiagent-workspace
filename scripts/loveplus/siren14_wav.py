#!/usr/bin/env python3
"""解 NLP+ 的 Siren14 语音（`Siren14Voice.spp`）→ 16 bit WAV。

用法：
    .venv/bin/python scripts/loveplus/siren14_wav.py --voice 0 1 2
    .venv/bin/python scripts/loveplus/siren14_wav.py --voice 0 --probe    # 相位约定诊断
    .venv/bin/python scripts/loveplus/siren14_wav.py --voice 0 --gain 2   # 音量微调

参数档：`--profile siren14`（默认：28 区域 / 640 样本 / 32 kHz / 5 bit 速率控制）
或 `g7221-16k`（FFmpeg 的 14 区域 / 320 样本 / 16 kHz 支）。

产出：`data/loveplus/nlp_plus/decoded/voice_<id>.wav`（16 bit 单声道，可直接播）。
索引：`Siren14voice.bin` 每条 8 B = (off, size)，指向 `Siren14Voice.spp`；
size 均为帧长（46 B）的整数倍，size=0 为空条目。
"""
import argparse
import struct
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_paths import REPO          # noqa: E402
import siren14                          # noqa: E402
import siren_transform as st            # noqa: E402

AUDIO = Path(REPO) / "data/loveplus/nlp_plus/audio"
INDEX_BIN = AUDIO / "Siren14voice.bin"
SPP = AUDIO / "Siren14Voice.spp"
DEFAULT_OUT = Path(REPO) / "data/loveplus/nlp_plus/decoded"
PROFILES = {"siren14": dict(nregions=28), "g7221-16k": dict(nregions=14)}


def frame_bytes(bitrate_bps, frame_ms=20):
    """帧字节数：比特率 × 帧长（本作 18400 bps × 20 ms = 46 B）。"""
    return bitrate_bps * frame_ms // 1000 // 8


def load_index():
    raw = INDEX_BIN.read_bytes()
    return [struct.unpack_from("<II", raw, i * 8) for i in range(len(raw) // 8)]


def decode_voice(fh, off, size, nb, max_frames=0, bit_order="game"):
    """读一条语音 → 系数矩阵 [帧数, FRAME_SIZE]。"""
    siren14.reset_dw()          # dw 状态跨帧持久，每条语音流从头开始
    fh.seek(off)
    raw = fh.read(size)
    nframes = size // nb
    if max_frames > 0:
        nframes = min(nframes, max_frames)
    rows = [siren14.decode_frame(raw[i * nb:(i + 1) * nb], bit_order)[2] for i in range(nframes)]
    return np.array(rows) if rows else np.zeros((0, siren14.FRAME_SIZE))


def pcm16(pcm, gain=1.0):
    """float PCM（≈[-1,1]）→ int16。"""
    return np.clip(np.round(pcm * gain * 32768.0), -32768, 32767).astype("<i2")


def write_wav(path, data16, sr):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(data16.tobytes())


def stats(pcm, n, out_scale=1.0):
    peak = float(np.abs(pcm).max()) if pcm.size else 0.0
    rms = float(np.sqrt((pcm ** 2).mean())) if pcm.size else 0.0
    return dict(peak=peak, rms=rms, crest=peak / max(rms, 1e-12),
                raw_peak=peak / out_scale if out_scale else 0.0,
                disc=st.boundary_continuity(pcm, n))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", type=int, nargs="+", default=[0])
    ap.add_argument("--profile", default="siren14", choices=sorted(PROFILES))
    ap.add_argument("--bitrate", type=int, default=18400, help="bps（决定帧长 46 B）")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--gain", type=float, default=1.0)
    ap.add_argument("--max-frames", type=int, default=0, help="每条语音最多解多少帧（0=全部）")
    ap.add_argument("--probe", action="store_true", help="打印相位/系数统计诊断")
    ap.add_argument("--stats-csv", default="", help="把逐条统计写成 CSV（供报告复核）")
    ap.add_argument("--ref-check", action="store_true", help="与折叠/旋转式合成端（FFmpeg siren.c 排布）逐样本交叉核对")
    ap.add_argument("--no-wav", action="store_true")
    args = ap.parse_args()

    prof = siren14.configure(**PROFILES[args.profile])
    nb = frame_bytes(args.bitrate)
    idx = load_index()
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    print("参数档 %s；帧 %d B；索引 %d 条；输出 → %s" % (prof, nb, len(idx), outdir))
    rows = []

    with open(SPP, "rb") as fh:
        for vid in args.voice:
            if not 0 <= vid < len(idx):
                print("voice %d 越界（索引 %d 条）" % (vid, len(idx)))
                continue
            off, size = idx[vid]
            if size == 0:
                print("voice %d: size=0（空条目）" % vid)
                continue
            coefs = decode_voice(fh, off, size, nb, args.max_frames)
            syn = st.Synthesizer(prof["frame_size"], out_scale=st.out_scale_default(prof["frame_size"]))
            pcm = st.decode_voice(coefs, n=prof["frame_size"], out_scale=syn.out_scale)
            s = stats(pcm, prof["frame_size"], syn.out_scale)
            nz = int(np.median(np.count_nonzero(coefs, axis=1)))
            rows.append(dict(voice=vid, off=off, size=size, frames=coefs.shape[0], samples=len(pcm),
                             seconds=len(pcm) / prof["sample_rate"], peak=s["peak"], rms=s["rms"],
                             crest=s["crest"], disc=s["disc"], nz_median=nz, raw_peak=s["raw_peak"]))
            print("voice %-6d off=%-11d size=%-7d 帧=%-5d 样本=%-7d %.2f s 峰值=%.3f RMS=%.4f "
                  "峰均比=%.1f 边界跳变=%.2f 非零系数/帧(中位)=%d 原始逆变换峰值=%.0f"
                  % (vid, off, size, coefs.shape[0], len(pcm), len(pcm) / prof["sample_rate"],
                     s["peak"], s["rms"], s["crest"], s["disc"], nz, s["raw_peak"]))
            if args.probe:
                flipped = coefs.copy()
                flipped[:, 0::2] *= -1.0
                p2 = st.decode_voice(flipped, n=prof["frame_size"], out_scale=syn.out_scale)
                s2 = stats(p2, prof["frame_size"], syn.out_scale)
                print("        probe 原样: 边界跳变=%.2f RMS=%.4f ｜ 偶下标取负: 边界跳变=%.2f RMS=%.4f"
                      % (s["disc"], s["rms"], s2["disc"], s2["rms"]))
                dr = float(np.abs(pcm).max()) if pcm.size else 0.0
                dr2 = float(np.abs(p2).max()) if p2.size else 0.0
                print("        probe 峰值: 原样=%.3f 偶下标取负=%.3f" % (dr, dr2))
            if args.ref_check:
                n = prof["frame_size"]
                alt = st.synth_folded(coefs, n=n, out_scale=syn.out_scale)
                a, b = pcm[n:], alt[n:]          # 第 0 帧两边都是残留（无前帧），略去
                m = min(len(a), len(b))
                ra = float(np.sqrt((a[:m] ** 2).mean()))
                k = ra / max(float(np.sqrt((b[:m] ** 2).mean())), 1e-300)
                d = a[:m] - k * b[:m]
                print("        ref-check 折叠/旋转式合成端（= FFmpeg siren.c 排布，需 §5f 的无翻转约定）: "
                      "标量比=%.6f 归一相对误差=%.3e"
                      % (k, float(np.sqrt((d ** 2).mean())) / max(ra, 1e-300)))
            if not args.no_wav:
                path = outdir / ("voice_%05d.wav" % vid)
                write_wav(path, pcm16(pcm, args.gain), prof["sample_rate"])
                print("        → %s" % path)
    print("解码诊断 STATS:", siren14.STATS)
    if args.stats_csv and rows:
        cols = list(rows[0])
        with open(args.stats_csv, "w") as fh:
            fh.write(",".join(cols) + "\n")
            for r in rows:
                fh.write(",".join(("%g" % r[c]) if isinstance(r[c], float) else str(r[c]) for c in cols) + "\n")
        print("逐条统计 → %s（%d 行）" % (args.stats_csv, len(rows)))


if __name__ == "__main__":
    main()
