<!-- 生成物，勿手改：真源 `multiagents/state/memory/loveplus/audio_siren14.json`；改动走 `python3 multiagents/agentctl.py memory …`，本文件由 `memory export --write` 重渲染。 -->

# Love Plus+ 音频(Siren14)分析笔记

链路：`Siren14voice.bin` 索引 → `Siren14Voice.spp` 取帧 → `siren14.py`（位流 → 640 个 MLT 系数）
→ `siren_transform.py`（逆 MLT + 正弦窗 + 50% 重叠相加）→ 16 bit WAV。

    P="./.venv/bin/python scripts/loveplus/siren14_wav.py"
    $P --voice 0 1 2                       # 出 WAV 到 data/loveplus/nlp_plus/decoded/
    $P --voice 0 --ref-check --probe       # 折叠·旋转排布交叉核对 + 诊断
    $P --voice 0.. --no-wav --stats-csv out.csv   # 批量统计（供报告复核）
    ./.venv/bin/python scripts/loveplus/siren_transform.py   # selftest

参数档 `--profile siren14`（默认，本作：28 区域 / 640 样本 / 32 kHz / 5 bit 速率控制）或
`g7221-16k`（FFmpeg 的 14 区域 / 320 样本 / 16 kHz 支）。

### 验证结论（数字见 `memory/loveplus/reverse_code_bin.md` §5g）

- 分析核与标准 MDCT/MLT 定义式**逐元素完全一致**（相对偏差 0）；(分析, 合成) 补 2/N 后
  完美重构（2.4e-07）；窗正交 4.4e-16。
- 与 FFmpeg siren.c 的「折叠输出 + 旋转式重叠相加」排布**逐样本一致**（真实语音 ~2e-7），
  且**不需要**对系数做 (−1)^k 翻转 ⇒ 合成端采用 MLT 直接转置约定。
- 谱一致性：按 500 Hz 并带的实测谱 vs 码流逐区域系数带功率，相关 +0.97…+0.99；>14 kHz 能量 ≈ 0
  （系数 560..639 恒 0）⇒ 无镜像/混叠，带宽与 14 kHz 上限吻合。
- 输出标量 `sqrt(2/N)/32768`（N = 640 ⇒ 1.706e-06）：12 条抽样峰值 0.405–0.568，无削波；
  该标量与官方解码器的逐样本电平**未对齐**（整体增益，±6 dB 内），需要时 `--gain` 覆盖。
- 索引：92655 条 `(off,size)`，offset 单调、覆盖 `.spp` 100%、size 全为 46 的倍数；
  voice 92654 为空条目（size = 0）。

### 官参 G.722.1 资产归档（2026-10-18，03_audio-dec）

**重要资产，勿丢**：ITU-T G.722.1 官参定点实现（本仓库 Siren14 解码的 ground truth）。

- **归档位置**：`tools/g7221_ref/`（源码 24 个 .c/.h + 已编译 `refdec`/`refsynth`；
  `tools/` 在 .gitignore 内 → 版权第三方代码不入库但随仓库留存）
  + 纯源码快照 `tools/g7221_ref_src_20261018.tar.gz`（77 KB，不含二进制）
- **上游来源（此前未记录，本次补齐）**：GitHub **`Distrotech/h323plus`**（H.323 协议栈，
  内含 ITU-T G.722.1 官参代码），路径 `plugins/audio/G.722.1/G722-1/`。
  单文件取法：
  `https://raw.githubusercontent.com/Distrotech/h323plus/master/plugins/audio/G.722.1/G722-1/dct4_s.h`
  （来源证据：`/tmp/02_static-re/ref/_t` 是当时的 GitHub contents API 响应残片，含 html_url/git_url）
- **版本标识**：ITU-T G.722.1 (2005-05) Fixed point implementation for main body and Annex C，
  Software Release 2.1 (2008-06)，© 2004 Polycom, Inc.
- **编译复现**（`tools/g7221_ref/` 内源码已是改名后的可编译版本，直接即可）：
  `gcc -O2 -w -o refdec main_ref.c decoder.c coef2sam.c dct4_s.c tables.c huff_tab.c count.c common.c basop32.c`
  （首次从上游取时需 `perl -pi -e 's/\bround\s*\(/stl_round(/g' *.c *.h` 避 `round` 与 math.h 冲突；
  `tables.c` 含非 UTF-8 字节，读用 latin-1）
- **自写驱动**（我们的，非上游）：`main_ref.c`（refdec）、`refsynth.c`（refsynth），同目录。
  用法 `refdec <in.spp> <out.pcm> <nregions> <bits> [coef_out from to]`。
- **已验证**：归档内源码可重新编译通过；`refdec` 可执行。

⚠️ `/tmp/02_static-re/ref/` 是临时目录，会被系统清理 —— 权威副本现为 `tools/g7221_ref/`。

## 资源清单（`data/loveplus/nlp_plus/`）

| 文件 | 大小 | 作用 |
| --- | --- | --- |
| `code.bin` | 4.2 MB | ExeFS ARM11 可执行(`.text`，加载基址 0x00100000) |
| `audio/Siren14Voice.spp` | 656 MB | 语音数据本体 |
| `audio/Siren14voice.bin` | 724 KB | 索引表 |
| `audio/Siren14Voice.dpb` | 16 B | 头 |
| `audio/bcsar/*` | 26 MB | 音效库(BFSTM/CWAV 容器) |
| `audio/stream/*.bcstm` | 161 MB | 492 个 BGM 流 |

## 索引表 `Siren14voice.bin`（已确认结构）

- 185310 个 u32 = **92655 组 (offset, size) 对**，小端。
- 各组连续铺满 `.spp`：`off[i+1] == off[i]+size[i]`，且 `sum(size) == 656MB`（精确等于文件大小，ratio=1.0）。
- **所有 size 都是 46 字节的整数倍**（min=46）。即每条语音 = N × 46B 帧。
- 条目 size 中位数 ~6394B(139 帧)，最大 93978B(2043 帧)。

## `.dpb`（16B）

`17 00 00 00 | 01 00 00 00 | 01 00 00 00 | 10 00 00 00`
LE u32 = {0x17=23, 1, 1, 0x10=16}。注意 46 = 2×23。

**四个字段的语义（2026-10-17 静态确认，见 `reverse_code_bin.md` §5c）**：
驱动 `0x68b950` 按 `码率 = dpb[0]×800`、`采样率参数 = 7000<<dpb[1]`、`声道 = dpb[2]`、`位深 = dpb[3]` 存成每声部参数。

| 字段 | 值 | 语义（代码级） |
| --- | --- | --- |
| `dpb[0]` | 23 | **每帧 16 位字数**（= 46 B/帧）；×800 得码率（800 = 16 bit × 50 帧/s） |
| `dpb[1]` | 1 | **带宽选择**：`7000 << dpb[1]` = 14000 Hz（Siren14 那一支） |
| `dpb[2]` | 1 | 声道数 |
| `dpb[3]` | 16 | 位深 |

## 编解码

- **Siren14 = ITU-T G.722.1 Annex C (Polycom Siren14)**，32 kHz 采样，24/32/48 kbps，20ms 帧。
- 开源解码实现：PJMEDIA(pjmedia G722.1)、ITU C 参考实现、PolyTool。
- 每条 46B 帧的字节熵 ≈5.3/5.52（接近随机）→ 确为压缩码流。

### 46 B 帧长与采样率：已由静态代码确认（原「待确认」项）
逆向结论（细节与函数地址见 `reverse_code_bin.md` §5c）：

- 帧长不是常数，而是**从 `.dpb` 参数算出来的**：`bits/帧 = 码率 ÷ 50`（20 ms）→ 18400/50 = **368 bit
  = 46 B = 23 个字**；驱动侧再 `>>1` 得 23，正好等于 `dpb[0]`。三者互证。
- **368 bit（18.4 kbps）非 G.722.1C 标准速率**（标准为 24/32/48 kbps = 480/640/960 bit），
  属本作为语音定制的低速率；故「46 B 是自定义帧长」成立，条目内**没有**更细的组帧。
- 解码器 `0x142568` 只接受两个带宽参数：**7000 → 14 region / 320 样本**（16 kHz 采样那一支）、
  **14000 → 28 region / 640 样本**（32 kHz 采样那一支）；其它值报错。
  `.dpb[1]=1` → 参数 14000 → **本作走 28 region / 640 样本 / 32 kHz**。
- ⚠️ **既有实现与此不符**：`scripts/loveplus/siren14.py` 写的是 `FRAME_SIZE=320` + `NUMBER_OF_REGIONS=14`
  （16 kHz 那一支），`scripts/loveplus/siren_ref.c` 也设 `c->sample_rate = 16000`。
  按静态结论应为 **640 / 28 / 32000**；改这几个常量重跑一次即可用音频判定（任务 1.2/1.3）。

### 参照实现（FFmpeg 6.x `libavcodec/siren.c`）的局限与可复用点（2026-10-17 静态核对）

从 jsdelivr 取的 master 版 `siren.c`（872 行）核对结果：

- **可复用**：整条帧结构与本作逐项对应——`decode_envelope`（`get_bits(gb,5) - esf_adjustment`，
  `esf_adjustment=7`）→ `rate_control = get_bits(gb, 4)` → `categorize_regions(regions, get_bits_left(gb), …)`
  → `for (i<rate_control) power_categories[category_balance[i]]++` → `decode_vector(...)`；
  表名/值与仓内一致（`vector_dimension`、`number_of_vectors`、`expected_bits_table`、`mlt_quant`、
  `noise_category5/6`、`decoder_tables`、`differential_decoder_tree`、`index_table`）。
- **不可复用**：FFmpeg 写死 **14 region**、`#define FRAME_SIZE 320`、`REGION_SIZE 20`、
  `rate_control_possibilities = 16`、`rate_control = get_bits(gb, 4)`。
  本作的 **28-region 支（`dec+0x144c=28`、`dec+0x1464=640`、速率控制 **5 bit/32 种**）FFmpeg 没有**，
  必须按本作代码补（本作实现库 `0x75c000-0x767000`，帧解码入口 `0x75e69c`）。
- **自定义码率不成问题**：标准路径用**包长**算可用位数
  （`init_get_bits8(gb, avpkt->data, avpkt->size)`），`bits_per_frame = sample_rate/50` 只出现在
  Microsoft(MSNSIREN) 变体与 CRC 校验里 → 18400 bps 只要包长对（46 B）就能解。
- 参考源码临时副本：`/tmp/02_static-re/siren.c`（非真源，可重取）。

## code.bin 静态线索（2026-10-18 更正：偏移已作废）

> ⚠️ **2026-10-18 更正：本节原列的偏移是 `code.bin`（ExeFS LZSS 压缩体，4,429,644 B）内的字面量偏移，
> 不是虚拟地址，勿再当地址引用。** 冲突时的判定以 `memory/loveplus/reverse_code_bin.md` §1 为准。
> 正确的反汇编对象是解压后的文本段 `data/loveplus/nlp_plus/code_text_unpacked.bin`（8,126,464 B = 0x7C0000），
> 地址映射 VA = `0x00100000 + 文件偏移`（两文件头 64 B 相同）；压缩判别式 `u32@(len-4) + len == 解压后大小`。

- 加载基址 0x00100000；ARM 指令（非 Thumb）。
- 字符串（名字仍有效，偏移已作废）：`/Plus/`、`LP2_CTR.bcs`、`Voice`、`1A4VoiceEx`、`onVoice`、`SoundOpt`、
  `DSP1`、`AT9`、`dpb`。
- 作废偏移（仅留痕，勿引用）：`0x3f8923`、`0x3f8934`、`0x1a037d`、`0x331183`、`0x3f57ee`、`0x3f8905`、
  `0x3f88ce`。要在文本段里重找这些字符串，按上面的地址映射重算即可。

## 下一步

1. 无头 azahar 构建（关 QT/SDL/Vulkan/GL）。
2. 动态调试定位 `.spp` 读取/解码函数，确认 46B 帧与 G.722.1C 的关系及是否有额外变换。

## 07  移植实现与端到端验证（2026-10-17）

链路：`Siren14voice.bin` 索引 → `Siren14Voice.spp` 取帧 → `siren14.py`（位流 → 640 个 MLT 系数）
→ `siren_transform.py`（逆 MLT + 正弦窗 + 50% 重叠相加）→ 16 bit WAV。

    P="./.venv/bin/python scripts/loveplus/siren14_wav.py"
    $P --voice 0 1 2                       # 出 WAV 到 data/loveplus/nlp_plus/decoded/
    $P --voice 0 --ref-check --probe       # 折叠·旋转排布交叉核对 + 诊断
    $P --voice 0.. --no-wav --stats-csv out.csv   # 批量统计（供报告复核）
    ./.venv/bin/python scripts/loveplus/siren_transform.py   # selftest

参数档 `--profile siren14`（默认，本作：28 区域 / 640 样本 / 32 kHz / 5 bit 速率控制）或
`g7221-16k`（FFmpeg 的 14 区域 / 320 样本 / 16 kHz 支）。

### 验证结论（数字见 `memory/loveplus/reverse_code_bin.md` §5g）

- 分析核与标准 MDCT/MLT 定义式**逐元素完全一致**（相对偏差 0）；(分析, 合成) 补 2/N 后
  完美重构（2.4e-07）；窗正交 4.4e-16。
- 与 FFmpeg siren.c 的「折叠输出 + 旋转式重叠相加」排布**逐样本一致**（真实语音 ~2e-7），
  且**不需要**对系数做 (−1)^k 翻转 ⇒ 合成端采用 MLT 直接转置约定。
- 谱一致性：按 500 Hz 并带的实测谱 vs 码流逐区域系数带功率，相关 +0.97…+0.99；>14 kHz 能量 ≈ 0
  （系数 560..639 恒 0）⇒ 无镜像/混叠，带宽与 14 kHz 上限吻合。
- 输出标量 `sqrt(2/N)/32768`（N = 640 ⇒ 1.706e-06）：12 条抽样峰值 0.405–0.568，无削波；
  该标量与官方解码器的逐样本电平**未对齐**（整体增益，±6 dB 内），需要时 `--gain` 覆盖。
- 索引：92655 条 `(off,size)`，offset 单调、覆盖 `.spp` 100%、size 全为 46 的倍数；
  voice 92654 为空条目（size = 0）。

## 官参 G.722.1 资产归档（2026-10-18）

### 官参 G.722.1 资产归档（2026-10-18，03_audio-dec）

**重要资产，勿丢**：ITU-T G.722.1 官参定点实现（本仓库 Siren14 解码的 ground truth）。

- **归档位置**：`tools/g7221_ref/`（源码 24 个 .c/.h + 已编译 `refdec`/`refsynth`；
  `tools/` 在 .gitignore 内 → 版权第三方代码不入库但随仓库留存）
  + 纯源码快照 `tools/g7221_ref_src_20261018.tar.gz`（77 KB，不含二进制）
- **上游来源（此前未记录，本次补齐）**：GitHub **`Distrotech/h323plus`**（H.323 协议栈，
  内含 ITU-T G.722.1 官参代码），路径 `plugins/audio/G.722.1/G722-1/`。
  单文件取法：
  `https://raw.githubusercontent.com/Distrotech/h323plus/master/plugins/audio/G.722.1/G722-1/dct4_s.h`
  （来源证据：`/tmp/02_static-re/ref/_t` 是当时的 GitHub contents API 响应残片，含 html_url/git_url）
- **版本标识**：ITU-T G.722.1 (2005-05) Fixed point implementation for main body and Annex C，
  Software Release 2.1 (2008-06)，© 2004 Polycom, Inc.
- **编译复现**（`tools/g7221_ref/` 内源码已是改名后的可编译版本，直接即可）：
  `gcc -O2 -w -o refdec main_ref.c decoder.c coef2sam.c dct4_s.c tables.c huff_tab.c count.c common.c basop32.c`
  （首次从上游取时需 `perl -pi -e 's/\bround\s*\(/stl_round(/g' *.c *.h` 避 `round` 与 math.h 冲突；
  `tables.c` 含非 UTF-8 字节，读用 latin-1）
- **自写驱动**（我们的，非上游）：`main_ref.c`（refdec）、`refsynth.c`（refsynth），同目录。
  用法 `refdec <in.spp> <out.pcm> <nregions> <bits> [coef_out from to]`。
- **已验证**：归档内源码可重新编译通过；`refdec` 可执行。

⚠️ `/tmp/02_static-re/ref/` 是临时目录，会被系统清理 —— 权威副本现为 `tools/g7221_ref/`。

## 归档补记（2026-10-18 稍后）

**双份落地**（原先只在 `/tmp/02_static-re/ref/`，会被系统清理）：

| 位置 | 性质 | 内容 |
| --- | --- | --- |
| `archive/loveplus/g7221_ref_upstream_2026-10-18/` | **原始件归档**（`archive/` 不入库） | 上游源码 + README（含来源 URL、版本、编译步骤）+ `github_api_response_dct4_s.h.json`（来源证据）+ 我们的自写驱动 `main_ref.c`/`refsynth.c` |
| `tools/g7221_ref/` | **可执行副本**（`tools/` 不入库） | 同上源码 + 已编译 `refdec`/`refsynth`；另有纯源码快照 `tools/g7221_ref_src_20261018.tar.gz`（77 KB） |

- 已验证：`archive/` 副本可独立重新编译出可用的 `refdec`（编译命令见上节）。
- 注意：归档内上游源码是**已改名版**（`round(` → `stl_round(`），从上游重取需自行再改一次。
- **尚未利用**：官参**自带编码器** `encoder.c` / `encode.c` / `sam2coef.c` —— 可用来做
  「对已知信号编码 → 两边解码」闭环，一次判死波形不对齐的根因；远期还能用于中文配音的
  G.722.1 重编码。
