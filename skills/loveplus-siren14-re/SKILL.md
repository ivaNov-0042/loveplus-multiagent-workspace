---
name: LovePlus Siren14 语音解码与 code.bin 逆向
description: LovePlus+ 的 Siren14（G.722.1）语音解码链与 code.bin 静态逆向操作要点：反汇编对象与 VA 换算、r2/r2dec/r2ghidra 可用命令、位流层与定点 IMDCT 变换层的函数地址、Siren14voice.bin/.spp/.dpb 结构、踩坑清单。凡要在 code.bin 里查 Siren14/语音解码/逆向、用 r2 反编译、或移植解码器时加载本 skill。
---

# LovePlus Siren14 语音解码与 code.bin 逆向

## 目标与边界

- 目标：静态定位 `code.bin`（ARM11 可执行）里「Siren14 语音读取 + 解码」链，出源码级理解。
- 只做静态分析；动态调试线已被用户叫停。
- 远端 `tx-new` 只 `pull`，不 `push`。

## 反汇编对象与地址映射（最易错的一步）

| 项 | 值 |
| --- | --- |
| 反汇编对象 | `data/loveplus/nlp_plus/code_text_unpacked.bin`（8,126,464 B = 0x7C0000） |
| `code.bin` | 4,429,644 B，ExeFS LZSS 压缩体，不能按偏移当地址 |
| 地址映射 | VA = 0x00100000 + 文件偏移（两文件头 64 B 相同） |
| 指令集 | ARM 定长 4 B；任意 4 对齐地址可线性反汇编，不怕起点猜错 |

- 压缩判别式：`u32@(len-4) + len == 解压后大小`。
- 旧笔记里的 `0x3f8923`、`0x1a037d` 之类「VA」是压缩体内的字面量偏移，不是地址，勿再引用（`audio_siren14.md` 的「code.bin 静态线索」一节已作废）。

## r2 工具链

```bash
r2 -q -a arm -b 32 -m 0x00100000 -e asm.bits=32 \
   -c 'ahb 32 @ 0x<addr>' -c 'af @ 0x<addr>' -c 's 0x<addr>' -c pdg code_text_unpacked.bin
```

- 反编译质量：`pdc`（内置，会标注字符串，好用）→ `pdd`（r2dec）→ `pdg`（r2ghidra，含跳转表也出干净 C，最准）。
- `pdd`/`pdg` 已装好（`~/.local/share/radare2/plugins/`）；安装踩坑见 `memory/others/diary/2026-10-17_02_static-re.md`，可重跑 `scripts/loveplus/build_r2ghidra.sh`。
- 全量 `aa; aar` 约 2 分钟、识别 6511 函数，但项目存不住 → 只对目标函数 `af @ <起点>`。
- 定位新实现库的手法：拿参考实现的**整数表**当字节模式全仓搜 → 命中数据地址 → `find_code_xref.py` 反查引用它的字面量池 → 池所在函数即实现代码（整数表无四舍五入干扰，比浮点表可靠）。

## 关键函数

引擎侧读取链（详见指针）：

| 地址 | 作用 |
| --- | --- |
| `0x6d6f04` | 音声资源初始化：拼 4 个路径槽（+0x48 `.bin` 索引 / +0x4c `.spp` 码流 / +0x50 `.dpb` 参数 / +0x54 目录） |
| `0x6d854c` | `play_voice(ctx, id)`：从 `Siren14voice.bin` 的 `id*8` 读 8 B (off,size) → 从 `.spp` 读 size 字节 |
| `0x6d7d1c` | 语音库状态机（8 路 switch，含 SoundEx/DLC 分支，16 槽累计 > 0x60000 护栏） |
| `0x6d84ec` / `0x6d87a4` | 发起 base / SoundEx `.dpb`(16 B) 读取 |
| `0x6d99e8` | 语音引擎 tick：建解码器 → 取槽 (buf,size) → 描述符 → 压入 64×0x70 命令环 `0x9d7ae8` |
| `0x106f9c` | 统一资源读取 `(dst, path, size, offset, heap, reqctx)`；`.spp` 687 MB 全靠它分段读 |

解码链（`0x75c000-0x767000` 是本作内置的 G.722.1 实现库）：

| 地址 | 作用 |
| --- | --- |
| `0x142568` | 解码器初始化；按采样率参数分两支：7000 → 14 region/320 样本，14000 → 28 region/640 样本 |
| `0x142454` | 喂一帧 → `0x75e69c` → 结果拷入 `dec+ch*0x500+0xa08`（0x500 B = 640×i16） |
| `0x75e69c` | 帧解码总入口：envelope → rate_control → categorize → decode_vector |
| `0x75e0c0` / `0x75c3dc`(+`0x75c500`) / `0x75e2b8` | envelope / categorize_regions / decode_vector |
| `0x76b67c` | 窗 + 重叠相加（TDAC），内部调 `0x75dd2c` |
| `0x75dd2c` | 定点快速 IMDCT（10×2^k 分解；640 = 10×2⁶） |
| `0x1420dc` | 整帧流水线：在 MLT 系数域混音，32 voice 槽累加后每声道一次 IMDCT/OLA |

- 运行时函数语义锚点（strlen/memcpy/new/free 等）见真源 §5b；逐行语义全链见 §5c/§5d/§5e/§5f，本 skill 不复述。

## 解码链要点（结论与判据）

- `.spp` 流 = 标准 G.722.1 流。判据是**码本等价性**：枚举全部约 1276 条比特路径，游戏堆式码树与 FFmpeg「值即下标 + 幂掩码」给出的分量下标元组 7 类 100% 一致（`siren14_framecheck.py codebook`）→ FFmpeg 派生的表可直接复用，只改参数。
- 本作参数：28 region / 640 样本 / 32 kHz / 5-bit 速率控制（32 种）。FFmpeg `siren.c` 只有 14-region 支，解不了本作流。
- 位读器：16 位字内 MSB-first。
- 变换层是定点（Q12-Q15 + 四舍五入 + 0x7fff 饱和），FFmpeg 为 float；移植用 float IMDCT + FFmpeg 窗/OLA 即可（±1 LSB）。
- 位流只编码前 560 个系数（= 20×28，14 kHz 带宽上限），余 80 个为 0；`0x1420dc` 的 `step = 帧长×14/16 = 560` 独立印证。
- 引擎在系数域混音（线性变换下与时域混音等价，整帧只需一次 IMDCT/声道），音量/淡入也在系数域。

## Siren14 资源结构

| 文件 | 大小 | 结构 |
| --- | --- | --- |
| `audio/Siren14Voice.spp` | 656 MB | 码流本体，无容器 magic、高熵 |
| `audio/Siren14voice.bin` | 724 KB | 185310 个 u32 = 92655 组 (off,size)；`off[i+1]==off[i]+size[i]`，`sum(size)==文件大小`；所有 size 是 46 B 整数倍 |
| `audio/Siren14Voice.dpb` | 16 B | LE u32 `{23,1,1,16}` = {每帧 u16 字数, 带宽选择, 声道, 位深} |

- 帧长由参数算出：`bits/帧 = 码率/50 = 18400/50 = 368 bit = 46 B = 23×u16`（20 ms/帧），与 `dpb[0]=23` 互证。
- 18400 bps 低于 G.722.1C 标准速率（标准 24/32/48 kbps），属本作定制；自定义码率不成问题，FFmpeg 标准路径按包长算可用位数。
- 读 `.dpb` 时按解码参数块理解（4 个 u32 字段，无容器头与帧索引）。
- `.csidbin`(SDNM)/`.bcsar` 属另一条音效链（状态机状态 6/7），与语音无关。

## 踩坑清单（勿重复尝试）

1. 别对 `code.bin`（压缩体）反汇编；别把压缩体内的偏移当 VA。
2. `Ps` 保存项目失败（`Cannot save project`）；`anal.from/to`、`anal.in=range` 对 `aa` 无效（只出入口区 43 个函数）→ 只 `af @ <起点>`。
3. `r2 -L | grep` 查不到 r2dec 注册名，但 `pdd` 实际可用，别以 `-L` 判成败。
4. r2 偶发把 ARM 误判成 Thumb（`af` 出 "unaligned" 垃圾）→ 先 `ahb 32 @ <addr>` 再 `pd`/`pdg`。
5. `pdf` 对某些函数报 `Linear size differs too much from the bbsum` → 改 `pd N @ <地址>`。
6. `pdc`/`pdd` 对含跳转表的函数输出碎片（`// orphan`、`Failed to retrieve block`）→ 换 `pdg`。
7. 字面量池里的字符串指针多数是指针表，不是被代码直接 LDR；找调用方按「池地址 → 谁加载该池」两步走。
8. 大结构偏移（>0xfff）在池里找不到数值：编译器用 `mov rX,#0x1440`、`add rX,rY,#0x34000`（imm12 `0x90D`）/`#0x34c00`（`0xBD3`）造基址 → 按 imm12 反查指令。
9. 序幕扫描只匹配含 lr 的 push，会漏掉不保存 lr 的叶子函数（如 `0x742668`）。
10. VFP 密度高不能当归属证据。判「一段代码属于谁」走 `xrefin` → `ptrtab` → `prologue`；实例 0x76d000-0x76f000 属别的音效内核，与语音链无关。
11. 「一帧解完必须正好用掉 368 bit」是错的判据（编码器不填满帧，帧尾留 0~21 bit）；`bits` 子命令只做「不跑飞/不越界」回归检查。
12. 位读器三处易错：已读位数→字偏移应为 `(bit_index//16)*2`；符号位计数须按码字重置；`mlt_quant` 行距是 16 字（64 B）。
13. 两条旧推断已证伪：`0x006bccd4` 是触笔/输入状态机（非解码器），`0x8a8358` 是按键掩码映射表（非位分配表）；`SDNM` 是 `.csidbin` 头（非 `.spp` 头）。

## 下一步

1. 参数化移植：把 `scripts/loveplus/siren14.py` 由 14-region/320 改成 28/640/32000 Hz/5-bit；表可继续用 `siren_tables.py`（已证等价），或从 code.bin 直读（更权威，带 Q12 定点值）。
2. 移植要补三处：速率控制跳过已达 7 的区域 + 可用位数上限 `cap = 320·(nregions/14)`；多出的系数必须清零（FFmpeg 留上一帧陈旧值，不能照抄）；float IMDCT + 正弦窗 `sin((k+0.5)π/1280)` + 50% 重叠相加。
3. 解码验证：整条 voice 0（54 帧 / 2484 B）解到底，查不越界、不削波、帧边界无跳变。无原始 PCM 参照，报告须写明「未与官方解码器逐样本对齐」。
4. 可延后：0x76d000-0x76f000 属哪个编解码器（只有解 BGM/SE 时才需要）。

## 真源指针

- 细则以 `memory/loveplus/reverse_code_bin.md`（§0 目标、§1 地址映射、§4 工具链、§5 目标函数、§5b 库函数、§5c 读取链、§5d 实现库、§5e 位流层、§5f 变换层、§6 坑、§7 脚本、§8 下一步）与 `memory/loveplus/audio_siren14.md`（资源清单、索引表、`.dpb`、编解码）为准。
- 本 skill 是操作版。发现新结论先回填 memory 真源（`multiagents/agentctl.py memory …`），再更新本文件。
- 脚本用法：`scripts/loveplus/SCRIPTS.md` 的「R2 静态逆向辅助」「Siren14（G.722.1）解码核验与移植」两节。
