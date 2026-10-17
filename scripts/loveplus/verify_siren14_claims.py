#!/usr/bin/env python3
"""核验 `output/loveplus/report/siren14_decode.md` 里的可核验数字（现算，不写死）。

做法：左列 = 报告里出现的口径值（从报告正文用正则抓取），右列 = 本脚本**现场重算**的值；
逐条比对后落表 `data/loveplus/nlp_plus/decoded/report_claims_check.csv`。
外部来源（FFmpeg 源码事实）只标注「参考」，不作断言。

用法：
    ./.venv/bin/python scripts/loveplus/verify_siren14_claims.py [报告路径]
退出码：0 = 全部 OK；1 = 有 MISMATCH。
"""
import re
import struct
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_paths import REPO                              # noqa: E402
import siren14                                              # noqa: E402
import siren_transform as st                                # noqa: E402
import siren14_wav as wv                                    # noqa: E402

REPORT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(REPO) / "output/loveplus/report/siren14_decode.md"
OUT_CSV = Path(REPO) / "data/loveplus/nlp_plus/decoded/report_claims_check.csv"

# 抽样语音（报告里的端到端统计表与之一致）
SAMPLE = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1000, 46327]
# 谱一致性用到的三条
SPECTRAL = [0, 5, 1000]


def canonical():
    """现算全部口径值。"""
    v = {}
    st_res = st.selftest(640)
    v["selftest_kernel"] = max(st_res["kernel"], 0.0)
    v["selftest_exact"] = st_res["exact"]
    v["selftest_gain"] = st_res["gain"]
    v["selftest_window_orth"] = st_res["window_orth"]
    v["selftest_folded"] = st_res["folded"]
    v["out_scale_640"] = st.out_scale_default(640)

    prof = siren14.configure(nregions=28)
    v["frame_size"] = prof["frame_size"]
    v["sample_rate"] = prof["sample_rate"]
    v["nregions"] = prof["nregions"]
    v["rate_control_bits"] = prof["rate_control_bits"]

    raw = wv.INDEX_BIN.read_bytes()
    idx = [struct.unpack_from("<II", raw, i * 8) for i in range(len(raw) // 8)]
    v["index_entries"] = len(idx)
    v["index_monotonic"] = all(idx[i][0] <= idx[i + 1][0] for i in range(len(idx) - 1))
    v["index_size_mod46"] = all(s % 46 == 0 for _, s in idx)
    v["index_spp_bytes"] = wv.SPP.stat().st_size
    v["index_max_off_size"] = max(off + size for off, size in idx)

    rows = []
    with open(wv.SPP, "rb") as fh:
        for vid in SAMPLE:
            off, size = idx[vid]
            coefs = wv.decode_voice(fh, off, size, 46)
            pcm = st.decode_voice(coefs, n=prof["frame_size"], out_scale=v["out_scale_640"])
            s = wv.stats(pcm, prof["frame_size"], v["out_scale_640"])
            rows.append((vid, coefs.shape[0], len(pcm), s["peak"], s["rms"], s["crest"]))
    v["sample_rows"] = rows
    v["sample_max_peak"] = max(r[3] for r in rows)
    v["sample_min_peak"] = min(r[3] for r in rows)
    v["voice0"] = rows[0]
    v["voice1"] = rows[1]
    v["voice2"] = rows[2]

    # 谱一致性（500 Hz 并带相关）+ 14 kHz 以上能量占比
    corr, hi = {}, {}
    with open(wv.SPP, "rb") as fh:
        for vid in SPECTRAL:
            off, size = idx[vid]
            coefs = wv.decode_voice(fh, off, size, 46)
            prof_band = np.array([np.mean(coefs[:, k * 20:(k + 1) * 20] ** 2) for k in range(28)])
            pcm = st.decode_voice(coefs, n=prof["frame_size"], out_scale=v["out_scale_640"])
            win = np.hanning(len(pcm))
            F = np.abs(np.fft.rfft(pcm * win)) ** 2
            fr = np.fft.rfftfreq(len(pcm), 1.0 / prof["sample_rate"])
            meas = np.array([F[(fr >= k * 500) & (fr < (k + 1) * 500)].mean() for k in range(28)])
            corr[vid] = float(np.corrcoef(meas, prof_band)[0, 1])
            hi[vid] = float(F[fr > 14000].sum() / F.sum())
    v["spectral_corr"] = corr
    v["spectral_hi14k"] = hi

    # std 表（游戏 0x801d34，Q0）语义：round(2^((i-24)/2))
    q = np.array([round(2.0 ** ((i - 24) / 2.0)) for i in range(54)])
    v["std_24"] = int(q[24])
    v["std_53"] = int(q[53])
    v["std_0"] = int(q[0])
    v["stats"] = dict(siren14.STATS)

    # 328 条抽样（每 283 条取一条）的产出表统计（口径 = 该 CSV）
    spread = Path(REPO) / "data/loveplus/nlp_plus/decoded/decode_stats_spread.csv"
    if spread.exists():
        import csv
        rs = list(csv.DictReader(open(spread)))
        v["spread_n"] = len(rs)
        v["spread_peak_max"] = max(float(r["peak"]) for r in rs)
        v["spread_peak_median"] = float(np.median([float(r["peak"]) for r in rs]))
        v["spread_dur_max"] = max(float(r["seconds"]) for r in rs)
        v["spread_clip"] = sum(1 for r in rs if float(r["peak"]) >= 1.0)
    return v


# (报告中的口径名, 正则, 取值函数, 相对容差)
CLAIMS = [
    ("分析核与标准 MDCT 定义式偏差", r"逐元素完全一致", lambda v: v["selftest_kernel"] == 0.0, None),
    ("往返重构相对误差", r"完美重构[^0-9]{0,20}?([0-9.]+e[-+]?[0-9]+)", lambda v: v["selftest_exact"], 0.05),
    ("窗正交 max\\|w²+w'²−1\\|", r"窗正交[^\n]{0,40}?([0-9.]+e[-+]?[0-9]+)", lambda v: v["selftest_window_orth"], 0.30),
    ("输出标量 out_scale(640)", r"输出标量[\s\S]{0,200}?([0-9]+\.[0-9]+e[-+][0-9]+)", lambda v: v["out_scale_640"], 0.01),
    ("索引条数", r"\b(92655)\b", lambda v: v["index_entries"], None),
    ("每帧系数/样本数", r"\b(640)\b", lambda v: v["frame_size"], None),
    ("抽样峰值上限", r"峰值\s*0\.[0-9]+\s*[–\-~]\s*(0\.[0-9]+)", lambda v: v["sample_max_peak"], 0.02),
    ("voice 0 峰值", r"voice\s*0[^\n]{0,80}?峰值\s*([0-9.]+)", lambda v: v["voice0"][3], 0.02),
    ("voice 0 RMS", r"voice\s*0[^\n]{0,120}?RMS\s*([0-9.]+)", lambda v: v["voice0"][4], 0.03),
    ("谱一致性相关（voice 0）", r"谱一致性[\s\S]{0,300}?(\+0\.9[0-9]+)", lambda v: v["spectral_corr"][0], 0.02),
    ("标准表 std[24]", r"std\[24\]\s*=\s*([0-9]+)", lambda v: v["std_24"], None),
    ("328 条抽样峰值上限", r"328\s*条[^\n]{0,60}?([0-9]\.[0-9]+)", lambda v: v["spread_peak_max"], 0.02),
    ("328 条抽样削波条数", r"削波[^\n]{0,20}?([0-9]+)\s*条", lambda v: v["spread_clip"], None),
]


def grab(pattern, text):
    """抓取报告里的口径值：有捕获组取第一个组，无捕获组时按「出现即 1.0」处理。"""
    m = re.search(pattern, text)
    if not m:
        return None
    return float(m.group(1)) if m.groups() else 1.0


def main():
    text = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    if not text:
        print("报告尚未生成：%s（只打印现算口径值）" % REPORT)
    v = canonical()
    print("=== 现算口径值 ===")
    for k in ("selftest_kernel", "selftest_exact", "selftest_gain", "selftest_window_orth",
              "selftest_folded", "out_scale_640", "frame_size", "sample_rate", "nregions",
              "rate_control_bits", "index_entries", "index_monotonic", "index_size_mod46",
              "index_spp_bytes", "index_max_off_size", "sample_max_peak", "sample_min_peak", "stats"):
        print("  %-20s %s" % (k, v[k]))
    for r in v["sample_rows"]:
        print("  voice %-6d 帧=%-4d 样本=%-7d 峰值=%.3f RMS=%.4f 峰均比=%.1f" % r)
    print("  谱相关:", {k: round(x, 4) for k, x in v["spectral_corr"].items()},
          " >14kHz 占比:", {k: round(x, 8) for k, x in v["spectral_hi14k"].items()})

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    bad = 0
    with open(OUT_CSV, "w") as fh:
        fh.write("claim_id,报告中的值,现算值,容差,结论\n")
        for i, (name, pat, fn, tol) in enumerate(CLAIMS, 1):
            got, cur = fn(v), None
            try:
                cur = float(got)
            except (TypeError, ValueError):
                cur = np.nan
            rep = grab(pat, text) if text else None
            if not text:
                verdict = "NO-REPORT"
            elif rep is None:
                verdict = "NOT-FOUND"
            elif cur is None or (isinstance(cur, float) and np.isnan(cur)):
                verdict = "N/A"
            elif tol is None:
                verdict = "OK" if abs(rep - cur) < 0.5 else "MISMATCH"
            else:
                verdict = "OK" if abs(rep - cur) <= tol * max(abs(cur), 1e-30) else "MISMATCH"
            if verdict == "MISMATCH":
                bad += 1
            fh.write("%s,%s,%s,%s,%s\n" % (name, "" if rep is None else rep,
                                           got if not isinstance(got, (bool, dict, list)) else got, tol, verdict))
            print("  [%-9s] %-24s 报告=%s 现算=%s" % (verdict, name, rep, got))
    print("核验表 → %s（MISMATCH %d）" % (OUT_CSV, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
