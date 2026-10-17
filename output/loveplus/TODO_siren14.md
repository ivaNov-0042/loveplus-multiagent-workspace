# TODO：Siren14 语音解码逆向（动态调试 + 静态反汇编）

> 目标：从 `NLP_plus` 本体反出 Siren14 语音解码链，最终能把 `.spp` 解成可听 WAV。
> 约束：与模拟器交互走 MCP；静态用系统 r2 + capstone；动态用 azahar GDB stub（`gdb_session.py` 持单会话）。

## 阶段 A：定位解码器（静态 + 动态互证）
- [x] 确认 `code.bin` 加载基址 `0x00100000`（GDB 读 guest 内存与解压文件逐字节一致）
- [x] 定位三件套字符串/指针数组：`0x8a829c` = {bin, spp, dpb, .csidbin, .bcsar, "rom:/", "rom:/patch/", "LP2_CTR"}
- [x] 定位 RomFS 路径构造函数 `0x6d6f04`（strlen/strcpy/memcpy 拼路径 + malloc）
- [ ] 断点 `0x6d6f04` 命中 → 拿到 Siren14 声音对象、`.bin` 索引缓冲地址
- [ ] 对索引缓冲下读 watchpoint → 命中即"语音查询函数"
- [ ] 顺调用链找到"每帧读 46B → 解码"的函数（预期入口签名 `(state, u8* frame46, s16* pcm_out)`）
- [ ] 确认采样率（16 kHz / 320 样本 或者 32 kHz / 640 样本）与区域数（14）
- [ ] 排除 `0x142280` 区（320/640 定点内核）是否为重采样/混音而非解码
- [x] （2026-10-16）断点 `0x142454`（系数缓冲路径，`this+8`→1280B）在**整段游戏流程中始终未命中**
      → 该函数不是对话语音的播放路径。已读源码确认执行断点**跨核生效**（清全部 4 核指令缓存），
      排除"多核漏检"这一猜测。

## 阶段 B：取真值 PCM（动态）
- [ ] 断在解码器出口 → dump 一帧 PCM（640 或 320 个 s16）
- [ ] 记录 `N` 帧连续 PCM → `/tmp/siren_ref/*.raw` 作为校核基准
- [ ] 同时记录输入帧字节（46B×N），保证「输入-输出」成对
- [x] （2026-10-16）判明"什么时候才会播语音"：游戏开机 0.8s 做 DSP 初始化
      （`LoadComponent size=0xC288, prog_mask=0x00FF`），之后**必须推进到有声画面**才有音频；
      停在开机防盗版警告画面时本来全静音（曾据此**误判**"音频链坏了"，见 memory 踩坑记录）。
- [ ] 确认游戏是否真的下发音频源：`AZAHAR_LOG="*:Error Audio.DSP:Debug"` 下出现
      `source.cpp:360 source_id=... remaining_dirty` 即证明游戏提交了音频源
- [ ] （备选，更稳）在 `DspHle::Tick()` 里 env 门控把混音帧直接写文件取真值（避开 SDL 落盘的
      节流/膨胀问题：无头跑约 21× 实时）
- 阻塞：azahar HLE DSP 的 semaphore 相关 IPC 未实现（`GetSemaphore`/`ClearSemaphore` 为 `nullptr`，
      `DspHle::SetSemaphore` 空实现；`GetSemaphoreEventHandle`/`SetSemaphoreMask` 标 STUBBED）；
      LLE DSP 缺 `dspfirm.cdc` 固件走不通。已留 env 门控补丁 `AZAHAR_DSP_SEMAPHORE_HACK`（未证实）。

## 阶段 C：解码器实现与校核
- [ ] 移植 G.722.1(Siren14) 解码器（Python，numpy）—— 参考 FFmpeg `libavcodec/siren.c`（已取源码 `/tmp/ffsrc`）
- [ ] 用阶段 B 的真值 PCM 逐样本比对（目标：误差 < 1 LSB 或完全一致）
- [ ] 若 16 kHz 假设不成立 → 改 32 kHz/Annex C 路径

## 阶段 D：批量产出
- [ ] `scripts/loveplus/siren14_*.py`：索引解析 → 分帧 → 解码 → WAV（主入口 ≤200 行、模块 ≤300 行）
- [ ] `output/loveplus/report/siren14_decode.md`（交 subagent 撰写，附素材清单）
- [ ] 更新 `memory/loveplus/audio_siren14.md`、`scripts/loveplus/SCRIPTS.md`、工作日志

## 遗留记录
- 2026-10-16 晚：推进到"音频链路排查"后按用户要求暂停。结论与踩坑见
  `memory/loveplus/headless_azahar.md`（新增：动态调试机制 / DSP 音频链路 / 开机阶段两个误判）
  与 `memory/loveplus/diary/2026-10-16_01_emu-gui.md`（晚间小节）。
- 待决三路线：① `Audio.DSP:Debug` 验证游戏是否下发音频源；② `DspHle::Tick()` env 门控落混音帧；
  ③ 离线 libg7221（源码在 `/tmp/g7221src/`）解 `.spp` + 与已抓系数缓冲互证。

## 静态线收尾（2026-10-17，agent `02_static-re`）

用户明确「只做静态分析与反编译，不做动态调试」，本文件阶段 A/B 的动态任务**全部暂停**；
解码链改由静态逆向走通，阶段 C/D 已实质完成：

- 阶段 A 剩余项（断点/watchpoint 取地址）由静态定位替代：帧入口 `0x75e69c`、envelope `0x75e0c0`、
  categorize `0x75c3dc`、decode_vector `0x75e2b8`、IMDCT `0x75dd2c`、窗+OLA `0x76b67c`、
  整帧流水线 `0x1420dc`。
- 阶段 C：
  - [x] 解码器实现：`scripts/loveplus/{siren14.py,siren_tables.py,siren_transform.py,siren14_wav.py}`
    （位流层参数化 + MLT 合成层 + 端到端驱动）
  - [x] 逐样本比对：无官方真值 PCM，改为**内部一致性**验证——分析核与标准 MDCT/MLT 定义式逐元素
    一致（偏差 0）、完美重构（2.4e-07）、两套等价排布逐样本一致（~2e-7）、谱与码流带功率相关
    +0.996；「与官方解码器逐样本对齐」明确列为**未做**（见报告第 7 节）
  - [x] 16 kHz 假设不成立 → 实际 32 kHz / 640 / 28 region / 5 bit 速率控制（`.dpb` + `0x142568` init）
- 阶段 D：
  - [x] 批量产出脚本（索引 → 分帧 → 解码 → WAV），12 条抽样 + 328 条抽样统计落
    `data/loveplus/nlp_plus/decoded/`
  - [x] `output/loveplus/report/siren14_decode.md`（304 行，交 subagent 撰写）
  - [x] 核验脚本 `scripts/loveplus/verify_siren14_claims.py`（13 条全 OK）
  - [x] 更新 `memory/loveplus/audio_siren14.md`、`memory/loveplus/reverse_code_bin.md` §5c-§5g/§8、
    `scripts/loveplus/SCRIPTS.md`、工作日志
- 仍未做（可选，非阻塞）：定点 IMDCT 逐样本仿真（消掉相位约定最后一点残留不确定性）；
  `0x76d000-0x76f000` 那片与语音链无关的 VFP 密集代码归属哪个编解码器/音效内核。
