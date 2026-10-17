<!-- 生成物，勿手改：真源 `multiagents/state/memory/loveplus/reverse_code_bin.json`；改动走 `python3 multiagents/agentctl.py memory …`，本文件由 `memory export --write` 重渲染。 -->

# code.bin 静态逆向（Siren14 读取/解码）笔记

> 本文件专记 **静态反汇编/反编译** 这条线的进展、地址表、工具与踩坑。
> 动态调试线在 `memory/loveplus/diary/2026-10-16_01_emu-gui.md`（用户已叫停）；资源结构结论在 `audio_siren14.md`。
> 最后更新：2026-10-17

本节给出**位流 → 频谱系数**这一层的完整还原结果：表清单（地址级）、帧级算法、以及把
「游戏表 vs FFmpeg 表」的等价性判定为**同一标准 G.722.1 码本**的实证。

### 定点/整数表全清单（游戏内以 i32 存储）

| 表 | 地址 | 形态 | 内容 / 语义 | FFmpeg 对应 |
| --- | --- | --- | --- | --- |
| 标准偏差 | **0x801d34** | i32 ×54（Q12） | `sqrt(10^((i-24)·0.30103))`；末尾 6 值 4096/5793/8192/11585/16384/23170 | `standard_deviation[64]`（float） |
| `vector_dimension` | 0x801e34 | i32[8] | 2,2,2,4,4,5,5,1 | 同名 |
| mlt 行长−1 | **0x801e54** | i32[8] | 13,9,6,4,3,2,1,1 → 行长 `d` = 14,10,7,5,4,3,2,2 | 无（FFmpeg 用幂掩码） |
| 行长倒数 | **0x801e74** | i32[8] | `2^15/d` = 2341,3277,4682,6554,8193,10923,16385,16385 | 无（编译器生成整除用） |
| `number_of_vectors` | 0x801e94 | i32[8] | 10,10,10,5,5,4,4,20 | 同名 |
| 差分码树 | **0x8bbb38** | i32[28][23][2] | **行 0 全零占位**；行 i = FFmpeg `differential_decoder_tree[i-1]` 的前 46 值（逐值吻合） | `differential_decoder_tree[27][24][2]` |
| `mlt_quant` | **0x8bcf58** | i32[7][16]（Q12，行距 16 字） | ÷4096 后与 FFmpeg 的 float 表偏差 ≤ 0.0006 | `mlt_quant[7][14]`（float） |
| `expected_bits_table` | 0x8bd118 | i32[8] | 52,47,43,37,29,22,16,0 | 同名 |
| 码树（7 棵） | 指针表 **0x8bf8e0** → 0x8bd138 / 0x8bd6d8 / 0x8bd9c0 / 0x8bdb38 / 0x8beb70 / 0x8bf1f0 / 0x8bf7e8 | i32，**堆式布局** | 结点 n 的子节点 = `tree[2n]`、`tree[2n+1]`；值 ≤0 为叶，码 = −值 | `decoder_tree0..6`（值即下标、奇数为叶） |
| 噪声常数 | **0x8bf98c** | i32[3]（Q15） | 5793 / 8192 / 23170 = 0.17678 / 0.25 / 0.70711（类别 5/6/7） | `noise_category5/6` 的**平台值**；FFmpeg 是 21 元表、按「区域非零系数个数」取行，本作只取单值（见下「差异」） |

相邻地址：0x801e64 是 0x801e54 与 0x801e74 之间的空档（未使用）。

### 帧级算法（`0x75e69c`）

```
frame_decode(bitreader br, coefs_out, nregions=28):
    rc_bits, n_rc = (4, 16) if nregions == 14 else (5, 32)      # 5 bit / 32 种（本作）
    decode_envelope(br, nregions, std_dev[], power[])           # 0x75e0c0
    rate_control = br.read(rc_bits)                             # MSB-first
    categorize_regions(nregions, br.bits_left, n_rc, power, cats, balance)   # 0x75c3dc → 0x75c500
    for i in 0..rate_control-1:                                 # 0x75e69c 内联
        r = balance[i]; if cats[r] < 7: cats[r]++
    decode_vector(br, coefs_out, nregions, std_dev, cats)       # 0x75e2b8
```

`decode_envelope`（0x75e0c0）：`ESF = read(5) - 7`；区域 1..27 各走一次差分码树
（叶值 ≤0 → 增量 `= -叶值`，`power[i] = power[i-1] + 增量 - 12`，与 FFmpeg 的
`power[i-1] - index - 12` 等价）；最后 `std_dev[i] = table_0x801d34[clamp(power[i]+24, ≤53)]`。

`categorize_regions`（0x75c3dc + 0x75c500）与 FFmpeg 同构：`offset=-32, delta=32→1`
二分，`cat = clamp((offset+delta-power)>>1, 0, 7)`，`Σ expected_bits_table[cat] >= available-32`
则 `offset += delta`；再跑 min/max 调整循环（`n_rc-1` 次）产出 `balance[]`，最终
`cats = max_rate_categories`。**两处与 FFmpeg 不同**：

1. `n_rc` 是参数（16/32），FFmpeg 里硬编码 16；`balance` 长度 `n_rc-1`（31）。
2. 速率控制施加时**跳过已为 7 的区域**、且最多走 `len(balance)` 步（FFmpeg 不判断直接 `++`）。

另有游戏自己的**可用位数上限**（FFmpeg 完全没有）：`K = nregions/14`（编译器用魔数 0x92492493
生成，实测 14→1、28→2），`cap = 320·K`（14 region→320 bit、28 region→640 bit）；
`available > cap` 时 `available = cap + (available-cap)·5/8`。本作 46 B 帧 → available ≈ 230 bit
< 640 → **该规则不触发**，但移植到其它码率时需要。

`decode_vector`（0x75e2b8）：逐区域，`cat < 7` 时重复 `number_of_vectors[cat]` 次
「走码树得码字 → 拆成 `vector_dimension[cat]` 个量化下标 → 每个非零下标读 1 个符号位」；
系数 = `(mlt_quant[cat][digit] · std_dev · 22? + 0x800) >> 12`（Q12 乘加四舍五入），输出 **i16**。
出错时把后续区域类别置 7。`cat ≥ 5` 时叠 dither：`noise = (noise_table[cat-5]·std_dev + 0x4000) >> 15`，
每 10 个系数取一次 4 字 LFSR（`state[3]+state[0]`）的 16 位字，逐位决定 ±noise 写入为 0 的系数
（cat 7 全部重写）。**与 FFmpeg 的 dither 结构一致**（每 10 系数一次 `get_dw`）。

### 码本等价性证明（决定性结论）

游戏的码树是**堆式布局**、码字拆解用**按行长整除**（`digit = code % d; code //= d`，且
digit0 落在输出数组**末位**），与 FFmpeg 的「值即下标、奇数为叶」+「2 的幂掩码」表面完全不同。
判据：枚举**所有比特路径**（≈1276 条），比较两套码本给出的**分量下标元组**。

```
scripts/loveplus/siren14_framecheck.py codebook
  cat0: 路径 181/181，元组一致 181/181      cat4: 209/209，一致 209/209
  cat1:  94/94            94/94            cat5: 192/192，一致 192/192
  cat2:  48/48            48/48            cat6:  32/32，一致  32/32
  cat3: 520/520          520/520
```

结论：**两套码本语义等价**——游戏的树只是同一标准码本的另一种存储。故
**本作 `.spp` 流 = 标准 G.722.1 流**，既有 FFmpeg 派生的 `siren14.py` / `siren_tables.py`
**可以直接用来解**，只需改参数（28 region / 640 样本 / 32 kHz / 5-bit 速率控制）。

### 判据勘误：「位消耗必须精确等于帧长」不成立

最初设计的判据是「一帧解完必须正好用掉 368 bit」。实测**不成立**：编码器不填满帧，
`bits` 子命令在 voice 0 前 40 帧上给出帧尾剩余 0~21 bit（8 帧恰好填满，其余留零或随机尾）。
所以「闭合」不能当判据；**决定性判据是上面的码本等价性**。`bits` 子命令保留用于
「解码是否跑飞/越界」的回归检查（两套约定在 40/40 帧上都能解完、不越界）。

### 与 FFmpeg 的真实差异（写报告时必须写明）

1. FFmpeg 的 `siren.c` **没有** 28-region 分支（只有 14 region / 320 样本 / 16 种速率控制）。
   本作走 28 region / 640 / 32 种，是 FFmpeg 未覆盖的一支。
2. 噪声幅度：本作按类别取单一平台值；FFmpeg 按区域非零系数个数索引 21 元表。低非零数区域
   的舒适噪声幅度会不同（波形层面可见，听感影响小）。
3. 可用位数上限（320K + 5/8 压缩）：本作有、FFmpeg 无（本作 18400 bps 下不触发）。

本节补上「频谱系数 → PCM」这一层（任务 1.3 的最后一块），并更正上一轮的一个误判。

### 结论：本作变换层是**定点**，不是浮点

| 函数 | 地址 | 大小 | 职责 |
| --- | --- | --- | --- |
| 窗 + 重叠相加 | **0x76b67c** | 300 B | 调 IMDCT → 加正弦窗 → 与上一帧尾相加 → 写 PCM；唯一调用者 `0x1423bc`（语音链） |
| 快速 IMDCT | **0x75dd2c** | 896 B | 定点逆 MLT（N=640 或 320）；只被 0x76b67c 调用 |

定点证据：i16 乘 + `>>0xd/0xe/0xf`、`+0x1000/0x2000/0x4000` 四舍五入、负向饱和到 `0x8000`
（`^0x7fff ^ >>31` 惯用法，池常数 `*0x76b7b0 = 0x7fff`）。

### `0x75dd2c` = 定点快速 IMDCT（10×2ᵏ 分解）

640 = 10×2⁶、320 = 10×2⁵（`param_3 == 0x140` 选 320 分支，log2 级数 6 vs 7）。四段结构：

1. **前置蝶形**：按 `(a+b+1)>>1`、`(a−b+1)>>1` 处理 N 个输入，符号/取反决策取自一张
   **位模式表**（每个 u32 供 16 次迭代，每迭代 2 bit）：`0x8bf8fc`（320 用，10 字）、
   `0x8bf924`（640 用，20 字；表区间 0x8bf924-0x8bf974 恰好 80 B = 20 字 ✓）。
2. **log2 级基 2 蝶形**（双缓冲乒乓，栈上两个 640×i16 缓冲）。
3. **10 点逆 DCT-IV 核**：表 **0x801eb4**，i16 Q15，`tab[j] = round(32768·cos((2j+1)π/40))`
   （前 10 项逐值吻合）；按 **5 元素步长阶梯**索引：第 n 个输出取 `tab[5n .. 5n+9]` 与同一组
   10 个输入做点积，`(Σ + 0x4000) >> 15`。每块 10 输出，共 64 块 → 640 ✓。
4. **旋转级**：表 **0x8bf974**，i16 (cos,sin) 对，Q14（`>> 0xe`），复数式旋转
   `out = (c·a − s·b)>>14`、`(c·b + s·a)>>14`；最后 memmove 到输出。

### 窗表（3 张，验证到 ≤1 LSB）

三张表都是 **i16 交替 (sin φ, cos φ) 对**，幅度 `G = 18317`（≈0.5590·2¹⁵）：

| 表 | 地址 | 长度 | 用途 | φ |
| --- | --- | --- | --- | --- |
| A | **0x802954** | 640 i16 = 320 对 | N=320 帧 | `φ_j = (j+0.5)·π/640` |
| B | **0x802e54** | 640 i16 | N=640 帧前半 | `φ_j = (j+0.5)·π/1280` |
| C | **0x803354** | 640 i16 | N=640 帧后半 | `φ_{j+320}` |

拟合结果：三张表对 `G·(sin φ_j, cos φ_j)` 的**最大偏差 ≤ 0.99 LSB**（A/B/C 均最佳 G=18317）。
即窗函数 `w[k] = G·sin((k+0.5)·π/1280)`（k=0..639，2N = 1280），与 FFmpeg 的
`window[i] = sinf((i+0.5) * M_PI_2 / 320)` **同形**（FFmpeg 的 320 ↔ 本作的 640）。
对子 `(s,c) = (w[j], w[639−j])` 满足 `s² + c² = G²`（单位对），这正是 TDAC/`ff_vector_fmul_window`
所依赖的旋转形式。代码选表：`N/2 == 320`（即本作 N=640）→ (B, C)；否则 (A, A+0x280) ✓。

### `0x76b67c` 语义（窗 + 重叠相加）

```
fcn_76b67c(coefs /*r0*/, prev_tail /*r1*/, pcm_out /*r2*/, N)
    imdct(coefs → buf[N])                       # 0x75dd2c
    for j in 0..N/2-1:
        out[J1] = sat((c_j·prev_tail[j] + s_j·buf[N-1-j] + 0x1000) >> 13)   # 重叠相加
        out[J2] = sat((s'_j·buf[N/2+j] − c'_j·…)       + 0x1000) >> 13)      # 新尾
    memmove(prev_tail ← buf[N/2..N])            # 保存新尾给下一帧
```
与 FFmpeg 的 `vector_fmul_window`（TDAC 旋转 + 重叠相加）**同构**；50% 重叠、hop = N/2 = 320，
每帧输出 N=640 样本（20 ms @32 kHz ✓），上一帧尾缓冲每声道 0x280 B = 320 i16 ✓。

### 整帧流水线 `0x1420dc`（848 B）：**频域混音**

```
fcn_1420dc(obj, nch, pcm_dst[])
    memset(obj + ch*0x500, 0x500)  for ch in 0..max(nch,1)-1     # 清系数缓冲（640 i16/声道）
    for i in 0..31:                                              # 32 个 voice 槽（obj+0xf00）
        v = obj[0xf00 + i*4];  if v == NULL or 槽被掩码禁用(obj+0xf84 的 bit i): continue
        n = v.vtbl[0](v)                                         # 本帧样本数
        0x142454(v, 0, n, v+2)                                   # 位流→系数（→ 0x75e69c）
        ...（单/双声道分支、可选声道平均降混 (a+b+1)>>1）...
        step = frame_len*14/16                                   # 640→560（= 20×nregions）
        gain = v[·]*0x14243c>>15（仅 frame_len==320 时）
        for ch, k in (nch, step):
            obj[ch*0x500 + k] += sat((v_ch[k]·vol·gain + 0x2000) >> 14)   # 系数域累加！
    for ch in 0..nch-1:
        0x76b67c(obj + ch*0x500, obj + ch*0x280 + 0xa00, pcm_dst[ch], obj[0xf88])
    obj[0xf90] = (有 voice 解码成功)
```
关键点：
1. **混音在 MLT 系数域完成**（线性变换 ⇒ 与时域混音等价，但整帧只需一次 IMDCT/声道）——多达 32 路
   语音共享同一帧格式（28 region / 640）。
2. 累加只覆盖 **前 560 个系数**（`step = 640×14/16 = 560`）⇒ 与 §5e 的 28×20=560 完全吻合，
   **印证「位流只编码 560 个系数，其余 80 个为 0（14 kHz 带宽上限）」**。
3. 字段：`obj+0xf88` = 帧长（640）、`obj+0xf90` = 上一帧是否有声（无则输出静音）、
   `obj+0xf80` = 降混标志、`*0x14242c` = 0x7fff、系数缓冲 `obj + ch*0x500`、
   上一帧尾 `obj + ch*0x280 + 0xa00`、输出 PCM 由调用者按声道传入。
4. `0x142454`（逐帧封装）= 填好解码器字段（+0x1448 bits/帧、+0x144c region 数）后调
   **0x75e69c**，再把结果（0x500 B/声道）拷到 `v + ch*0x500`。

### 勘误：0x76d000-0x76f000（VFP 密度 34-36%）**不是**语音链的变换层

上一轮把该区当作变换层候选，**错**。证据：
1. 该区**没有** `push {…, lr}` 型序幕（`prologue --range 0x76b000-0x770000` 只找到 7 个，全在 0x76b000-0x76c000），
   全仓**无任何 `bl` 落入 0x76d000-0x76f000**；
2. 它只被函数指针表 **0x76bc34**（位于 0x76bb14 内，41 项 → 0x76d22c/0x76d318/…/0x76ee0c，
   其中 0x76e724/0x76e968/0x76ebb4/0x76ee0c 各重复 8 次）间接调用；
3. 0x76bb14 的 4 个调用者全在 **0x765xxx**，而 0x765xxx 只被 0x64xxxx-0x66axxx
   （SE/BGM 引擎）调用；
4. 语音链（0x14xxxx）对 0x75c000-0x772000 的全部调用只有：0x75c3b8、0x75c7d8、0x75e69c、
   0x76b67c（另 0x145xxx 调 0x76b460/0x76b634）。

⇒ 该区属于**另一个编解码器/音效内核**（VFP 密集），与 Siren14 语音解码无关。未做，见 §8。

### 与 FFmpeg 的差异（补充，写报告时并入）

1. FFmpeg `number_of_valid_coefs = REGION_SIZE·nregions = 280 < FRAME_SIZE=320`，
   多出的 40 个槽位**不清零**（保留上一帧陈旧值，`imdct_in` 是持久缓冲）；本作显式 memset
   整个 640 系数缓冲，且只累加前 560 ⇒ 高 80 个系数为 0。**移植时应按本作清零**。
2. 本作变换为定点（Q13/Q14/Q15 + 饱和），FFmpeg 为 float。移植用 float IMDCT + FFmpeg 窗/OLA 即可，
   差异在 ±1 LSB 量级（听感无关）。窗/重叠约定（正弦窗 `sin((k+0.5)π/2N)`、50% 重叠、
   每帧 N 样本）两者一致 ⇒ **本作流可用「FFmpeg 表 + 28-region/640/5-bit 参数 + 清零尾部系数」解**。
3. 本作把「音量 × 多路混音」放在系数域（引擎架构，非标准内容）。

§5f 给出变换层的静态还原；本节记录**移植实现 + 数值验证 + 两个悬而未决项的定案**。

### 实现（`scripts/loveplus/`）

| 模块 | 职责 |
| --- | --- |
| `siren_transform.py` | MLT 合成层：`mlt_window` / `imlt_basis` / `forward_mlt`（仅自检用）/ `Synthesizer`（逐帧逆 MLT + 窗 + OLA）/ `synth_folded`（折叠·旋转式等价排布）/ `out_scale_default` / `selftest` |
| `siren14.py` | 位流 → 系数（G.722.1 家族；`configure(nregions=…)` 切档，本作 = 28 区域 / 640 / 32 kHz / 5 bit 速率控制） |
| `siren14_wav.py` | 驱动：`Siren14voice.bin` 索引 → `.spp` → 系数 → WAV；`--ref-check` / `--stats-csv` / `--probe` |

正/逆变换（N = 每帧系数数 = 每帧样本数，窗长 2N，hop = N）：

    y[m] = Σ_k X[k]·cos(π/N·(m + 0.5 + N/2)·(k + 0.5))    m = 0..2N-1
    w[m] = sin((m + 0.5)·π/(2N))
    pcm[i] = w[i]·y_k[i] + w[N+i]·y_{k-1}[N+i]            i = 0..N-1

### 数值验证（`selftest`，N = 640）

| 量 | 值 | 含义 |
| --- | --- | --- |
| `gain` | 3.200e+02 = N/2 | 未归一化 MLT 对的固有增益 |
| `kernel` | **0.000e+00** | 分析核与标准 MDCT 定义式 `cos((2j+1+N)(2k+1)π/(4N))` 逐元素完全一致 |
| `exact` | 2.4e-07 | 补 2/N 后往返（完美）重构相对误差 |
| `window_orth` | 4.4e-16 | max\|w[i]² + w[i+N]² − 1\|（TDAC 条件） |
| `folded` | 6.5e-12 | `synth_folded` 与 `Synthesizer` 在同一系数上的相对 RMS 差 |

`--ref-check`（真实语音 voice 0/1/2）再验一次：折叠·旋转排布 vs 整长 OLA，标量比 = 1.000000、
归一相对误差 ≈ 2.0e-07。

### 相位约定定案：合成端不做 (−1)^k 翻转

1. 分析核 `imlt_basis().T` 与标准 MDCT/MLT 定义式逐元素一致（`kernel` = 0；与 FFmpeg
   `ff_tx_mdct_naive_fwd` 的公式也一致）。本作窗表拟合式 `G·sin((k+0.5)π/1280)` 正是 Malvar
   MLT 的 2N = 1280 正弦窗，基函数含 (N+1)/2 偏移 ⇒ 即 MLT 定义式。
2. (分析, 合成) 完美重构（补 2/N 后 2.4e-07）。
3. FFmpeg siren.c 的「折叠输出 + 旋转式重叠相加」排布，在**不翻转**系数时与本实现逐样本一致
   （真实语音 ~2e-7）。

偶下标取负得到另一条信号（与本实现互相关 ≈ 0.005，与 x 的相关 ≈ −0.01），**不采用**。FFmpeg
源码里的 `imdct_in[i] *= -1, i += 2` 属其通用逆 MDCT（AV_TX）的输入约定；逐字抄录其 naive
参考实现（`ff_tx_mdct_naive_inv`，prio MIN 的死代码路径）无法复现，故不作判据。
残留不确定性：本作定点 IMDCT（0x75dd2c）的**旋转级符号**未逐样本对照（只核了窗表与结构），
若要绝对对齐，按 §5f 的四段结构 + 三张表做定点仿真再逐样本比。

### std 表语义（推翻「系数过大 = 解码 bug」的怀疑）

游戏 0x801d34 = 54 项 i32 **Q0**：`std[i] = round(2^((i-24)/2))`（等价 `10^((i-24)·0.3010299957)`），
按 `arp + 24` 索引，arp ∈ [−24, +29]（本作 `GAME_ARP_MAX = 29`）。故回放增益最大 2^14.5，
响帧（arp 18-20）系数合法可达 1e5 量级：实测最响帧 max|coef| = 136613，而 `q·std` 的比值
仍 ≤ 4.724（码本上限内）⇒ **系数幅度正常**，不是解码错误。

### 输出标量（绝对增益）

未归一化逆变换最响帧峰值 252250，整体标量 > 1/7.7 必削波。取
`out_scale = sqrt(2/N)/32768`（教科书正交归一 ÷ Q15 口径；N = 640 时 1.706e-06）：
voice 0 峰值 0.430 / RMS 0.0969（约 −20 dBFS）。备选 `2/N`（Q15 口径下峰值仅 0.024，过轻）、
`1/32768`（FFmpeg 净效果，会削波）。**该标量与游戏/FFmpeg 的逐样本电平未对齐，属整体增益**
（±6 dB 内），需要时用 `--gain` 覆盖。

### 谱一致性（按 500 Hz 并带）

按 500 Hz 归并的实测谱 vs 码流逐区域系数带功率：voice 0/5/1000 的相关系数
+0.988 / +0.967 / +0.976（把系数带功率镜像后相关转负）；>8 kHz 能量占比
5.3% / 3.6% / 0.9%；>14 kHz 能量 ≈ 0（系数 560..639 恒为 0，与 §5f 的 `step = 560` 吻合）
⇒ 无频域镜像、无混叠，带宽与 14 kHz 上限一致。

### 端到端统计（12 条抽样 + 全量索引勘验）

- `Siren14voice.bin` = 92655 条 × 8 B `(off,size)`：offset 单调、覆盖 `.spp` 100%、
  size 全为 46 的倍数（voice 92654 为空条目 size = 0）。
- 12 条抽样（含 off 最大的 46327）：帧 43–213、时长 0.86–4.26 s、峰值 0.405–0.568
  （**无削波**）、RMS 0.060–0.107、峰均比 4.4–6.8、边界跳变 0.63–1.33、
  非零系数/帧中位 504–518。
- 解码诊断 STATS：`arp_gt_game_max = 0`、`rc_skip7 = 0`（18400 bps 下速率控制守卫未触发）。

起因：用户提问「dpb 是不是所有音频解码都要用？有没有可能特定语音用高保真/低保真参数？」
——静态核了一遍代码与两个 ROM，结论如下。

### 结论 1：dpb 只服务 Siren14 语音链，不是全音频系统通用

- dpb 的 16 字节只被两处读：`0x6d84ec`（base `Siren14Voice.dpb`）、`0x6d87a4`（追加データ
  `SoundEx/Siren14VoiceEx.dpb`）。
- dpb 字段的唯一消费者是 `0x68b950`（把 4 个字段写进引擎对象）→ `0x68b174`（配置解码器）→
  `0x142568`（Siren14 解码器 init）。而 `0x142568` **全仓只有一个调用者** `0x68b1d8`，
  `0x68b950`/`0x68b174` 也各只有一个调用者（`0x71ef1c`/`0x71ef2c`，建声部跳板内）。
- BGM（`STRM_BGM*.bcstm` = CSTM）与音效（`LP2_CTR*.bcsar` = CSAR + `.csidbin`/SDNM）各有自己的
  容器头（采样率/编码类型在其中），不经过 dpb。

### 结论 2：粒度是「音库级」，且架构上确实支持分档

- 引擎一次初始化里读 dpb 并建解码器（`0x6d99e8` 的 `[eng+0x58b]`/`[eng+0x58c]` 一次性标志），
  之后同一音库的 92655 条语音共用这套参数 —— 索引表里只有 `(off,size)`，没有任何逐条参数通道。
- `0x142568` 反汇编（本次实读）：
  - `bits/帧 = bitrate / 50`（魔数 `0x51eb851f`），写入 `dec+0x1448` 与 `dec+0x1468`；
    即 `字节/帧 = 2 × dpb[0]`（23 → 46 B）。
  - `rate_param = 7000 << dpb[1]` 只认两个值：`7000` → `dec+0x144c = 14` region、`dec+0x1464 = 0x140`
    (320 样本)；`14000` → `0x1c` (28 region)、`0x280` (640 样本)；**其它值 `bl 0x124730` 报错**。
  - 对位率码 `dpb[0]` **不做范围校验** → 原理上帧长可换。
- 也就是说：`dpb[1]` 是「7 kHz 带宽（16 kHz 采样 / 320 样本 / 14 region）」与「14 kHz 带宽
  （32 kHz / 640 / 28）」两档的开关，`dpb[0]` 决定帧长 —— 分档能力确实存在，只是本作只用了一档。

### 结论 3：本作（以及前作）都只有一个音库、一种配置

- base dpb = `{23, 1, 1, 16}` → 18400 bps、14 kHz 带宽、单声道、16 bit，即**高档**。
- 全库单一配置的判据：92655 条 `size` **全是 46 的倍数**，且 `.spp` 被 46 B 帧整除
  （687534906 = 46 × 14946411）。若存在别的帧长/配置，size 不会一致地对齐 46。
- 卡带 RomFS 名表（UTF-16，~4.60 MB 处）实测只有一套：`Siren14voice.bin` / `Siren14Voice.spp` /
  `Siren14Voice.dpb`；**没有 `Siren14VoiceEx.*`** → 追加データ（SoundEx）那套 dpb 不在卡带里，
  代码里为它预留的读取路径（状态 5 / `0x6d87a4`）在本作卡带内容上不会触发。
- 跨作品核对：`New Love Plus (Japan)` 与 `New Love Plus+ (Japan)` 两个 ROM 里，按 dpb 形状
  （`{1..64, 0..3, 1..2, 8/16/24/32}` 小端 u32）扫全盘，**形状成立且唯一的 dpb 都是 `{23,1,1,16}`**
  （+ 版 @ROM 偏移 747015024，非 plus 版 @965856128）→ 两作用同一档。

### 结论 4：逐帧的「保真度」变化来自 5 bit 速率控制，而不是逐条配置

- 每帧 5 bit 的 rate control（32 档）+ 7 类码本决定这一帧 28 个 region 里哪些分到多少 bit。
- 实测（最长的三条：2043 / 1720 / 1249 帧）：每帧**有码 region 数 24–28，中位 28**（分布
  28:1406 / 27:527 / 26:96 / 25:13 / 24:1）。说明 18400 bps 对 28 region 这档预算够用，
  本库里几乎不存在「被降到低带宽」的帧；帧间差异主要在量化精度与包络上。

### 操作含义（将来遇到别的音库）

- 若某音库的 `dpb[1] = 0`（7 kHz 档）：`siren14_wav.py --profile g7221-16k` + `N = 320` 合成。
- 若 `dpb[0] ≠ 23`：`--bitrate = dpb[0] × 800`（帧长 = `2 × dpb[0]` 字节；驱动已按 bps 推算帧长）。
- 找 ROM 里的 dpb 的两步法（本次用过，可复用）：① 搜 UTF-16 名表（3DS RomFS 名是 UTF-16LE，
  ASCII 搜不到）拿到 `*.dpb` 条目的 `(dataOffset, size=16)`；② 按 dpb 形状扫全盘、再用配套
  `.bin` 索引结构（`off[i+1] = off[i]+size[i]`、`size` 为偶数）反解 RomFS 数据区基址做自校验。

ITU-T G.722.1 **官参定点实现**已落地并作为本仓库 Siren14 解码器的 ground truth。

### 来源与编译（可复现）

- 源码：*ITU-T G.722.1 (2005-05) — Fixed point implementation for main body and Annex C*，
  Software Release 2.1 (2008-06)，© 2004 Polycom, Inc.（即标准配套的官参代码；未入库，
  仅作对照用，见 `repos/` 规则）。本会话放在 `/tmp/02_static-re/ref/`。
- 编译（`round` 与 `math.h` 冲突需改名；`tables.c` 含非 UTF-8 字节，读时用 `latin-1`）：
  `perl -pi -e 's/\bround\s*\(/stl_round(/g' *.c *.h` 之后
  `gcc -O2 -w -o refdec main_ref.c decoder.c coef2sam.c dct4_s.c tables.c huff_tab.c count.c common.c basop32.c`
- 自带驱动（本次新写，在 ref 目录内）：`refdec <in.spp> <out.pcm> <nregions> <bits> [coef_out from to]`
  （真实比特流解码；28 区域 / 368 bit → `frame_size=640`、`nvalid=560`）、
  `refsynth <coef.bin> <out.pcm> [dct_length] [mag_shift]`（只做合成）。
  输入 `.spp` 片是**原始字节**（不必 `swap16`；官参按 16 位小端字读、bit15 起取）。
- 官参参数档与本作一致：`NUM_CATEGORIZATION_CONTROL_BITS 4`/`POSSIBILITIES 16`、
  `MAX_… 5`/`32`、`NUMBER_OF_REGIONS 14`/`MAX 28`、`REGION_SIZE 20`、`MAX_DCT_LENGTH 640`、
  `ESF_ADJUSTMENT_TO_RMS_INDEX 7`、`MAX_BITS_PER_FRAME 960`、`bit_rate/50` fps。

### 逐系数对照（决定性判据）

`/tmp/02_static-re/cmp_coef_detail.py <voice> <模块> <帧数>`：分「编码位（cat≤4）」与
「噪声位（cat≤7 中 cat==7 的区）」比我们的系数与官参 `refdec` 导出的系数。

- **符号一致率恒为 100%**（编码位与噪声位都是）。
- 比值 = `22 × 2^mag_shift`：相邻帧若 `mag_shift` 差 1，比值就 22 ↔ 44 翻倍
  （官参 `mag_shift` 是纯定点动态范围技巧，`rmlt_coefs_to_samples` 在 OLA 前把 DCT 输出
  整体 `shr 2^mag_shift`，且 `old_samples` 存的是**移位后**的值，帧间不产生尺度跳变；
  本作是固定 Q13 窗、无逐帧定标 → **不需要移植**，只在对照时换算）。
- 噪声位比值恰好 `5793/256 = 22.6289`（cat 7）→ 游戏表 0x8bf98c 的 `23170/32768`
  精确到 <0.01%。

### 由此坐实、已落 `scripts/loveplus/siren14.py` 的三处修正（2026-10-17）

1. **噪声幅度与编码系数同单位**：游戏里 `系数 = (mlt_quant_Q12 × std) >> 12`、
   `噪声 = (tbl_Q15 × std) >> 15`，两者同单位；本实现给系数乘了 `SCALE_FACTOR=22`，
   噪声必须同乘，否则噪声低 22×（≈ −27 dB）。表 0x8bf98c 是**单一类别平台值**
   （cat5=5793/32768、cat6=8192/32768、cat7=23170/32768），**不是** FFmpeg 的按非零计数查表；
   已由官参 `decoder.c` 的 `noise_fill_factor[3] = {5793, 8192, 23170}` 独立证实。
2. **`dw` 伪随机状态跨帧持久**：游戏把状态存在解码器对象上（`dec+0x1420+slot*16`），
   官参的 `randobj`（`get_rand`）同样跨帧。模块级 `_DW_STATE` + `siren14.reset_dw()`
   （每条语音流起头调用；`siren14_wav.py` 的 `decode_voice` 已加）。
3. **噪声符号位按相邻 10 系数分块**：官参取两次 `get_rand`、各覆盖**相邻** 10 个系数
   （0–9 / 10–19）；FFmpeg 写成 `dw1/dw2` 偶奇交错。照抄 FFmpeg 时长音频符号位与官参
   不一致，改分块后 100% 一致。

### 「平均 / 平滑」裁定：**没有跨帧平滑**

用户问「源码里有没有做平均/平滑」。逐条查完（官参全源 + 游戏 code.bin）：

- 官参里所有 `shr(...,1)` 都不是平滑：`common.c:359/443` 是类别量化步长
  `j = (offset − rms_index) >> 1`；`decoder.c:335` 是 `mag_shift` 搜索里把标准差之和
  逐次减半；`coef2sam.c:91` 是 `half_dct_size = shr(dct_length,1)`；`dct4_s.c:189/193`
  与 `dct4_a.c:228/315/320` 是蝶形归一化。
- **唯一的真「平均」**：合成 DCT 输入蝶形 `(x ± y + dither) >> 1`
  （官参 `dct4_s.c:187-193`，注释自述用于消除截断偏置；dither 是 0/1 固定位模式，
  表 `dither[320]` / `max_dither[640]`，定义在 `dct4_s.h:90/124`）。
  **游戏 code.bin 同构**：`0x75dd8c`–`0x75ddb4` 同一蝶形，dither 位取自
  `0x8bf8fc`（320 档）/ `0x8bf924`（640 档）的 **32 位打包位表**（取位循环 31→1、
  每用完 4 字节表指针 +4）。→ 这是**块内**蝶形缩放（整体增益意义），不是帧间平滑。
- OLA 本身本身就是相邻两帧的**加权交叉淡化**（游戏 `0x76b67c`：两次 `smulbb` 相加 +
  `+0x1000` 舍入 + `asr #13`；官参 `L_mac` 累加 + `stl_round(L_shl(sum,2))`）。
- **没有**：跨帧系数平滑 / EMA / 低通、后置滤波器、谐波噪声整形、自适应增益平滑。

### 仍未决：波形与官参不相关（谱一致）

- 逐帧 28 带（0–14 kHz）幅度谱：全部 **±0.6 dB** 内，逐帧谱形相关中位 0.974、
  逐帧总能量相关 0.885（见 `/tmp/02_static-re/cmp_spec.py`）。
- 样本级：lag 0 相关 ≈ 0；lag 640（一帧）处稳定为 **−0.3** 左右（15 条长音频全部如此）。
- 已排除：逐块反转、逐块反转+取负、整体取负、半块循环移、奇偶帧取负（逐帧相关符号
  **不交替**）、单系数探针变体、系数域顺序/偶数取负变体。
- 结论方向：两边「系数→样本」的**折叠/相位排布约定**不等价（官参是标准文本定义的
  「反序 MLT」：样本反序 + MLT + 偶数下标取负；FFmpeg 系是另一种等价排布）。
  但**谱一致**说明量值正确，差异在相位/排布层。
- **旁证**：两边解码时长逐条完全一致（同一 640 样本/20 ms → 32 kHz），样本级边界跳变
  指标（`boundary_continuity`）都在 0.88–1.07 的健康区间 → 「语速不对」不是解码器
  造成的（要怀疑的是播放端/游戏侧的采样率处理）。
- 关键判据（尚未做）：用官参**自带编码器**（`encoder.c`/`encode.c`/`sam2coef.c` 都在 ref 目录）
  对已知信号编码 → 两边解码对照，一次判死谁对；或做 640×640 算子矩阵比对。

### 6a. patched 卡带布局（NLP_plus_patched.3ds，2 GB）

- NCSD 头在文件偏移 **0x100**（不在 0）；主程序 NCCH 在表项 `0x2E40400*0x200` 处但**已加密**。
- 全文件仅一个 IVFC 头 @**0x45E000**（RomFS 明文区），其 level1/2/3 描述与标准 3DS 不符
  （实测 level1 hash 区 @0x45E3A0 size 0x19680、level2/3 与官方布局对不上）——放弃标准解析。
- **文件项表**（明文，0x4776xx 附近起，扫 0x45E000–0x800000 共 2382 项）：
  `[u32 0xffffffff, u32 nameBytes, UTF16 名, u32 id, u32 flags, u32 offset, 0, u32 size, 0]`。
- 表里 offset 是虚拟地址；**明文内容 = offset + 0x496F80**（脚本/Siren14 系列实测一致；
  个别文件头另有 0x10–0x50 hash 块 → ±0x10 档）。
- 明文锚点：`Siren14voice.bin` 内容 @0x2C7B3BF0（唯一内容匹配）、dpb `{23,1,1,16}` @0x2C868B70
  （dpb 之后 64 B hash 即 spp 开头，与我们手里 `audio/Siren14Voice.spp` 前 64 B 一致）。
- 非 SBN2 的大文件（bcsar/bcstm/csidbin/spp/dpb/PAK 字体）都还在表里可提；
  `TextResource`（off=0x69E4, size=0x25D58）实为 **PAK/FNTB 字体块**，不是对话文本。

### 6b. SBN2/DBN2 脚本容器（解密）

- 依据 gdkchan/NLPTextTool（`repos/NLPTextTool/`，tarball master 8f19eb3）。
- **3 层 XOr 流，每层独立 Key**：`out[i] = data[i] ^ (KeyBytes[i%3] + Seed*(i//3))`，
  其中 `Key = LE u32 @magic+4`，`KeyBytes = Key 低 3 字节`，`Seed = Key 第 4 字节`；
  i 是**本层缓冲区内**位置（不是全文件偏移——初版因此解错）。
- SBN2 头：`SBN2`(4) + Key(4)；@8 BE u32 条目数；@0x10 每项 16 B：
  BE `hash0, hash1, off, len`（前两个 u32 疑为校验，NLPTextTool 的 DBN2 分支语义 `u0,u1,off,len` 同构）。
- 内层块再各自解一层：`SOB2`(4)+Key(4)+数据。**本作 535 个脚本的内层全部是 SOB2**（无 SDL2）。
- SOB2 = **Dream VM 字节码**（code.bin 里有 `Dream::ScriptProcess` 字符串 @0x27E9B7 VA；
  `SOB2`/`SDL2` 字面量池 @VA 0x1DD5BC 邻接 Shift-JIS 人名表指针 0x77914/0x779D0）。
  指令形态如 `32 01 00 XX`（push imm）、`87 02 …`、`83 01 00 XX`；块头 @0x0C=0x48（数据起点）、
  @0x24 起 28 B 疑 hash。**文本不在 SOB2 里**（UTF-8/Shift-JIS 日文均 0 命中）。

### 6c. 未决（下轮）

- 文本的真实存放处：候选 ① SOB2 引用的**外部字符串表**（TextResource 已排除=字体）；
  ② ExeFS/另一文件（`rom:/script/bin/script` 主脚本 @VA 0x6EEA35 字符串、`NLP_01/NLP_02`
  语言分支、`%s%s%s` 拼接 @0x6EEA50 邻域——加载器函数在 0x6EE830/0x6EE900/0x6EE9B0，
  无直接 ARM bl 调用者，可能经 vtable/内联）；③ kiwiz/nlpp-fmt 的 xml 是从**原版未打补丁**
  卡带 dump 的，或 SOB2 里 `32 01 00 XX` 的 XX 就是字符串 id（0x271f=10015 超出块长 → 指向池外）。
- 语音 id（如 55655=0xD947）在 t*.dbin2 中无 u32/u16 明文命中 → id 也在字符串/常量池间接引用，
  或由**台词序号**推导（NLPTextTool 的 SDL2.Dialogs 顺序 ↔ 语音序号）。
- 远期目标（TODO 5.2）：中文配音替换链 = 文本/语音对应关系 → TTS 音色克隆 → G.722.1 重编码
  → `.spp` 重打包 → 卡带回写（文件表 offset+0x496F80 定位、size 变更需重排或空洞填充）。

### 7. 脚本→语音映射（2026-10-17，02_static-re）：静态穷举结论 = 数据侧无解，走动态

目标：打通「脚本（SOB2 字节码）→ 语音 id（Siren14voice.bin 索引）」，产出 voice id → 场景/角色/前后台词 小批次表。

**静态穷举结果（全部已验证，均是否定）：**

1. **语音 id 不在 SOB2 明文**。用**正确解密**（`xor_stream(blk,key,0)[8:]`，magic+key 前 8B 是明文、XOR keystream 按绝对位置）解全部 535 文件后：
   - 13 个已知长语音 id（27480–27520、55653–55672）在全语料仅各出现 **8–16 次**（噪声级）；
   - `[10000,70000]` 区间共 1486487 次命中、50231 个不同值——均匀分布噪声；
   - 高频值 12800/13568/18432… 实为**操作码字节**（`32 01`=PUSH、`35 00`、`48 00`）被对齐 u16 误读。
2. **全部 38123 个内层块都是 SOB2**，0 个 SDL2 → NLPTextTool（只解 SDL2）对本作脚本无用。
3. **SOB2 体里无 UTF-16LE 日文对白**（最长 CJK 连续 run 仅 2–6 码元，纯巧合）；对白/文本不在脚本明文。
4. **`.sbin2` 是 PAK 归档**（a000.sbin2 含 2364 个 `PAK ` 子文件），非对白/语音表；dbin2/sbin2 是同名数据+PAK 配对，与语音映射无关。
5. **ROM 文件表 2381 项**无独立「voice map / msg table」；只有 dbin2、sbin2(PAK)、bcsar/bcstm（含 `STRM_VX_*_NN.bcstm` 按角色分库语音）、spp/dpb、FNTB 字体、TextResource(=字体)。

**SOB2 解密布局（实测，纠正旧笔记）：**
- 块 = `magic(4)+key(4)` **明文** + 密文。解密：`xor_stream(blk,key,0)[8:]`。
- 解密头 = `00000001 00000048`（count=1, code_off=0x48），`0x18=0x48`，`0x3C=0`，`0x40=0x48` 数据起点，之后 28B hash，代码 @0x48。
- 指令（已粗解）：`32 01 00 v`=PUSH(v 小整数)、`87 02 00 00`=CALL(2)、`01 00`/`00 XX` 其它操作。`83 01 00 NN`=CALL 子程 NN。

**SOB2 VM 解析链（code.bin，已定位）：**
- `0x1dd2d4` = SOB2/SDL2 块 loader：调 `0x1e0f2c` 读头、读 +9 处 type 字节、按 5 个角色类走各段加载（`0x6ee804`/`0x6ec684`）。
- `0x6ee890` = UTF-16LE→UTF-8 解码器（确认对白以 UTF-16LE 存于 SOB2 某段，但本作用密文/间接方式，未直接落盘明文）。
- `play_voice(ctx, id)` @`0x6d854c`，id 是槽号 0–15；真实大 id 在 16 槽 `slot[i].id`（`ctx+i*0x14+0x7c`）。`0x6d8280`/`0x6d870c` 是两个薄封装，无 `bl` 调用者、无字面量引用 → 经 vtable/函数指针**间接**触发（即脚本命令分发入口）。

**结论 / 下一步（动态）：**
- 数据侧已穷举无解：语音 id 由 SOB2 VM **运行时**解析。只能走 **headless azahar + GDB stub**：
  启动 `scripts/loveplus/run_emu.sh`（无 `--frames`=无限运行）或 MCP `start_emulator(gdb=true)`，
  用 `gdb-multiarch` 连 `127.0.0.1:24689`（target remote，halt on connect），
  在 `play_voice`（`0x6d854c`）或槽写入点 `0x742aec`（读 `slot[i].id`）下断，
  捕获每次播放的 (脚本文件, VM pc) → (slot, big_id)，回溯 SOB2 操作码如何压入 id。
- 模拟器已验证可启动运行（手动 `--frames 200` exit 0；之前 MCP 给 600 帧跑完即退，导致 live 端口 refused）。需注意 `--frames 0` 会立即退出。

# 语音索引链打通：conditionvoice_*.lmb → Siren14voice.bin → .spp

语音索引链打通：conditionvoice_*.lmb → Siren14voice.bin → .spp


¶ 结论一句话

**voice_id 就是 `Siren14voice.bin` 的直接索引，无二级映射。** 中文配音链路的最后一环已闭合。

¶ 核心发现：conditionvoice_<0|1|2>.lmb 是语音索引表

卡带 PACK 归档里有 33 个 `.lmb`，其中 `conditionvoice_{0,1,2}.lmb` 是**条件语音索引表**。

- 这些文件是 **zlib 压缩流**（`78 9c` 开头）。注意：PACK 条目的 `Flags bit0` **没有**标记为压缩，必须自行判断 → 这是 PACK 提取器的一个坑。
- 解压后：`@0x00` u32 = 记录数（207），随后 **12 字节定长记录**：

```
struct LMBRecord {   // 12 B
    u32 flag;        // 高16位 = 条件组 id (0x0001, 0x0104, 0x0105 ... 严格递增)
                      // 低16位 = 组内序号    (1,2,3 ... 严格连续, 31/31 组全部验证通过)
    u32 _mid;        // 恒为 0
    u32 voice_id;    // Siren14voice.bin 直接索引; 同组内严格 +1 递增
};
// 相邻两条之间以 flag==0xFFFFFFFF 的记录作分隔
```

⚠️ 字段顺序踩坑：`voice_id` 是**第三个** u32，不是第二个。最初按 `(flag, voice_id)` 解出全 0，浪费了几轮。

### 「一段对话里多个音频索引是连续的」——已量化验证

用户提出的假设成立。实测 `conditionvoice_0.lmb`：

| 条件组 | 条数 | voice_id 区间 | 连续 |
|---|---|---|---|
| `0x0104` | 5 | `0x2a16–0x2a1a` | ✅ |
| `0x0105` | 5 | `0x2a1b–0x2a1f` | ✅ |
| `0x0106` | 3 | `0x2a20–0x2a22` | ✅ |
| `0x0107` | 3 | `0x2a23–0x2a25` | ✅ |
| `0x0108` | 3 | `0x2a26–0x2a28` | ✅ |
| `0x0109` | 3 | `0x685a–0x685c` | ✅ |

**同一条件下的一组语音，其 voice_id 是连号排列的** → 对中文配音极有利：替换一整段对话 = 替换一段连续 id 区间。

三个文件结构完全同构（均 207 条 / 31 组），仅 voice_id 基址不同：
- `_0` `0x2a16` 起 / `_1` `0x9821` 起 / `_2` `0x1069e` 起

¶ Siren14voice.bin 索引表验证

```
741240 B = 92655 条 × 8 B (offset u32, size u32)
offset 100% 单调递增 (92654/92654)
off+size 全部落在 .spp (687534906 B = 655.7 MiB) 内, 0 越界
size==0 仅 1 条 (尾哨兵)
```
实测 `conditionvoice` 的所有 voice_id **全部 in-range**（e.g. `0x2a16`→off=56661098 size=11454）。

¶ 角色 ↔ 脚本前缀（由 .spgdat 实证，非推测）

| spgdat | 脚本前缀 | 角色 |
|---|---|---|
| `Nene.spgdat` | `a00/a01/a50/a77/a99` | **宁宁 Nene** |
| `Rinko.spgdat` | `k00/k01/k50/k77/k99` | **凛子 Rinko** |
| `Manaka.spgdat` | `t00/t01/t50/t77/t99` | **爱花 Manaka** |
| — | `p*` | 主角 |
| 三方共有 | `t88` | 公共脚本 |

用户明确纠正：**Manaka = 爱花**（我此前臆造为"真奈加"，是错的）。三位角色只有这三个，不要编造第四个。

`.spgdat` 本身是精灵图区间表（`0→256→512→768` 步长 256），**与语音无关**，别再当语音索引。

¶ 文本数据：.mdc 邮件词典（含明文 UTF-8 日文）

- 全 ROM 扩展名统计（5683 PACK / 46521 文件）：`texi` 19681、`yaml` 3305、`mdl/smes/smat/bone` 各 2971、`arc` 2883、**`cdb` 1939**、**`rvbin` 25**（ReVoice 语音合成词典：`dtb`/`mdc`/`hmm`/`phn`）、**`lmb` 33**、**`twbdat` 12**（`EventTable_Stage*`）。
- `.mdc` 结构：`0x00 <len u8> <UTF-8 len 字节> 0x00`，记录间用 `0xffff` + `c1/c2/c4/c8/d0/e0/f0` 标志簇 + `00` 填充。该标志簇低字节为**一热编码的桶号**（`c1→c2→c4→c8→d0→e0`，单 bit 上移），第 4 字节 `ff/fe` 为配对奇偶位，尾部 `01/02` 为段号 → 印证多级连续索引结构。
- 解出真实台词量：`maildic_n` 598 / `maildic_m` 571 / `maildic_r` 552 条，`worddic_*` 各 31 条。

¶ 重要纠正：.texi 不是文本索引，是纹理描述

之前推断「`.texi` = 文本索引，文件名对应脚本」**是错的**。SERI 解开后参数名为
`w/h/mipmap/format/tex/type/ow/oh`，且 `type` 值 = `0x49584554` = ASCII **"TEXI"** → 纹理类型枚举。
`.texi` 是**纹理描述文件**，与文本无关。

（gdkchan 的 NLPUnpacker 原本不支持 `'TEXI'` 这个 +版扩展类型，所以解不出。）

¶ SERI 格式精确布局（gdkchan/NLPUnpacker Program.cs 权威）

```
@0x00 'SERI'
@0x04 u32  -> ValuesOffset = 该值 + 4     ← 注意：不加 BaseOffset
@0x08 u16  ParametersCount               ← 是 @0x08，不是 @0x0a（易错）
@0x0A  ParametersCount * { u16 NameOffset, u16 ValueOffset }
TypesTable @ ValuesOffset - ParametersCount   (每参数 1 字节类型码)
Values      @ ValuesOffset
类型码: 's'=str 'i'=int32 'f'=float 'b'=bool 'a'=array 'h'=nested-array
```
⚠️ **两个必踩的坑**：
1. 字符串（参数名和 's' 值）解析在 **PACK 容器的 StringTableOffset（ROM 缓冲）**里，不在 SERI 文件内。我最初拿文件自身缓冲去索引 → 参数名全空。
2. `ValuesOffset` 若再 `+4` 会算成 50 而非正确的 46+4=50… 实际要严格用 `@0x04 + 4`。

¶ PACK 容器布局（复刻自 gdkchan/NLPUnpacker）

```
@0x00 'PACK'
@0x04 u32 FileCount = 值>>16
@0x08 u32 StringPointersOffset (+Base)
@0x0C u32 StringTableOffset    (+Base)
@0x10 u32 DataOffset           (+Base)
@0x14 u32 DecompressedSectionLength
@0x18 u32 CompressedSectionLength
@0x1C u32 Padding
@0x20 + i*0x20 条目(0x20B): sig[4], unk0, DecompressedLength,
        DecompressedOffset(+Base), unk1, Flags(bit0=IsCompressed),
        CompressedLength, CompressedOffset(+Base)
文件名 = *(StringPointersOffset + i*4) → StringTableOffset + 偏移, NUL 结尾
```

¶ 工具与产物

- **`scripts/loveplus/02_static-re/nlp_voice.py`** —— 正式工具（已落盘），含上述全部结构体注释。
  子命令：`prefix` / `voicemap` / `verify` / `mdc`
- 产物落盘 `data/loveplus/nlp_plus/voice_map/`：
  - `conditionvoice_map.json` (30.3K) —— 条件组 → voice_id 映射
  - `mdc_lines.json` (98.5K) —— 各 `.mdc` 台词全文

¶ 尚未解决

1. **剧情对白主索引表尚未定位**。`conditionvoice_*` 是「条件语音」（满足游戏内条件才播的搭话/反馈），不等于剧情对白主线。`EventTable_Stage*.twbdat`（zlib，已解但未解析）是最可能的候选。
2. **脚本 SOB2 → voice_id 的引用方式未知**。已确认 SOB2 payload 是**带 tag 的对象序列化**而非裸 u32 数组（a000.dbin2 的 4 个 SOB2 块共 14600 字节，u32 值 ≤2000 的仅 5 个），所以静态按 u32 穷举语音 id 行不通——这是之前"静态穷举失败"的根本原因。
3. `keyword_*` 系列 lmb（2655 条）无 12B 定长结构，格式待解；`cdb`(1939)、`rvbin`(25) 未深入。

## 0. 目标与边界

- 目标：在 `code.bin`（ARM11 可执行）里定位**读取 Siren14 语音**的相关函数（文件路径拼接、索引表读取、帧解码），
  用 r2 反汇编 / 反编译出源码级理解。
- 用户明确要求：**只做静态分析，不做动态调试**。

## 1. 反汇编对象与地址映射（务必先看）

| 文件 | 大小 | 说明 |
| --- | --- | --- |
| `data/loveplus/nlp_plus/code.bin` | 4,429,644 B | ExeFS **LZSS 压缩体**，**不能**直接按其偏移当地址 |
| `data/loveplus/nlp_plus/code_text_unpacked.bin` | 8,126,464 B (0x7C0000) | **反汇编就对这个** |

- 压缩判别式：`u32@(len-4) + len == 解压后大小`（实测 8126464）——旧笔记里 `0x3f8923`、`0x1a037d` 一类「VA」
  是**压缩体内的字面量偏移，不是地址**，勿再引用。
- 地址映射：**VA = 0x00100000 + 文件偏移**（两文件头 64 字节相同）。
- r2 加载命令（本项目固定写法）：

```bash
r2 -q -a arm -b 32 -m 0x00100000 -e scr.color=0 code_text_unpacked.bin
```

- 指令集：**ARM 模式**（定长 4 字节，任意 4 对齐地址可直接线性反汇编，不怕起点猜错）。
  `anal.armthumb` 选项在 r2 6.0.7 不存在，报错可忽略。

## 2. Siren14 相关字符串（精确 VA，已实测）

`rom:/Plus/Sound/` 区块集中，VA ≈ 0x844c36 起：

| 字符串 | VA |
| --- | --- |
| `Siren14Voice.dpb` | 0x00844c88 |
| `Siren14voice.bin` | 0x00844cc8 |
| `Siren14Voice.spp` | 0x00844cfd |
| `SoundEx/Siren14VoiceEx.dpb` | 0x00844c99 |
| `SoundEx/Siren14VoiceEx.bin` | 0x00844cd9 |
| `SoundEx/Siren14VoiceEx.spp` | 0x00844d0e |
| `.csidbin` | 0x00844cf4 |
| `.bcsar` | 0x00844d53 |
| `rom:/` | 0x00844c54 |
| `rom:/Plus/Sound/` | 0x00844d3b |
| `LP2_CTR` | 0x00844c80 |
| `LP2_CTR.bcsar` | 0x00844d4c |

同区还有 `.csidbin`、`LP2_CTR_DLC_SE_001`、`LP2_CTR_MG1_PUZZLE`、`LP2_CTR_MG2_Twinbee`、
`LP2_CTR_MG3_YieAr`、`lipsync_jpn.lip`、`textresource_config.trb` 等。

## 3. 关键数据表（.rodata，VA 0x8a82xx 起）

### 3.1 字符串指针数组 `0x008a829c`（Siren 三件套）

```
0x8a829c -> 0x844cc8  "Siren14voice.bin"
0x8a82a0 -> 0x844cfd  "Siren14Voice.spp"
0x8a82a4 -> 0x844c88  "Siren14Voice.dpb"
0x8a82a8 -> 0x844cf4  ".csidbin"
0x8a82ac -> 0x844d53  ".bcsar"
0x8a82b0 -> 0x844c54  "rom:/"
0x8a82b8 -> 0x844c80  "LP2_CTR"
```

引用它的**字面量池**（= 用它的函数）：`0x006d73dc`、`0x006d7814`、`0x006d8294`、`0x0074f4c4`。

### 3.1b SoundEx（追加データ）三件套指针数组 `0x007e38e4`

```
0x7e38e4 -> 0x844cd9  "SoundEx/Siren14VoiceEx.bin"
0x7e38e8 -> 0x844d0e  "SoundEx/Siren14VoiceEx.spp"
0x7e38ec -> 0x844c99  "SoundEx/Siren14VoiceEx.dpb"
```

布局与 §3.1 的前三项一致（bin/spp/dpb 顺序相同）。
**指向该数组的指针** `0x7e38e4` 被存于：`0x006d8290`（池，属 `0x6d7d1c`）、`0x006d87a0`、`0x006d8808`。
其前面还有 3 个代码指针 `0x676900 / 0x6768f0 / 0x6764e4`（0x7e38d8..0x7e38e0），像一张「(函数指针 ×3) + (路径 ×3)」的结构体。
`0x7e38d8` 被存于 `0x006768d8`、`0x00676980`（另一处引用）。

### 3.2 DLC/追加数据表（步长 0x14 = {const char* name; u32 id; pad…}）

```
0x8a82cc "LP2_CTR_MG1_PUZZLE"  id=0x10000000
0x8a82e0 "LP2_CTR_MG2_Twinbee" id=0x20000000
0x8a82f4 "LP2_CTR_MG3_YieAr"   id=0x30000000
0x8a8308 "LP2_CTR_DLC_SE_001"  id=0x40000000
```

### 3.3 音效库配置 `0x008a8330`

```
0x8a8330 -> 0x844d3b "rom:/Plus/Sound/"
0x8a8334 -> 0x844d4c "LP2_CTR.bcsar"
0x8a8338 = 0x3e800000 (0.25f)      <-- 音量系数
```

引用它的池：`0x006d8e78`、`0x006d9648`（后者见 §5 的 `0x6d959c`）。

### 3.4 掩码/映射表区 `0x008a8358` 起 —— **与编解码无关（已证伪）**

```
0x8a8358: 0x10 0x40 0x20 0x80 0x40 0x20 0x80 0x10   (8 值，和 = 480 bit = 60 B)
0x8a8378 起: 0x10000000 0x40000000 0x20000000 0x80000000 …（掩码形态）
0x8a83e0 起: 另一组同类表
```

被池 `0x006bd2f8`、`0x006bd300` 引用 → 都在函数 **0x006bccd4** 内。
2026-10-17 复核：**`0x006bccd4` 不是编解码器，而是触笔/输入状态机**（见 §5）。
0x8a8358 那组数是「按键掩码 → 位序号」的映射表；488 bit 的巧合**不构成**码率证据，
`0x8a8358 → 编解码` 的推断作废。

## 4. 工具链（r2 反编译）

| 命令 | 来源 | 状态 |
| --- | --- | --- |
| `pd` / `pdf` | r2 内置 | ✅ 反汇编 |
| `pdc` | r2 内置 | ✅ 类 C（会把 `ldr r0,[pc,#imm]` 解析成 `sb = [0x6d6f30] // (pstr …) "Siren14voice.bin"`，很好用） |
| `pdd` | r2dec 插件 | ✅ 已装（`~/.local/share/radare2/plugins/libcore_pdd.so`） |
| `pdg` | r2ghidra 插件 | ✅ 已装（`core_ghidra.so`，tag 6.0.7 源码编译，2026-10-17）。**质量最优**，含跳转表的函数也能出干净 C |

装插件踩的坑（master 与 r2 6.0.7 不兼容、release 的 deb 是 ABI 14、subprojects 依赖会卡死、
依赖补丁不能丢）全部记在 **`memory/others/diary/2026-10-17_02_static-re.md`**；可重跑脚本 `scripts/loveplus/build_r2ghidra.sh`。

安装与踩坑：

- `r2pm` 首次必须 `r2pm -U`（clone `radare2-pm` 数据库到 `~/.local/share/radare2/r2pm/git/radare2-pm`）。
  2026-10-17 14:36 曾因 github 瞬时不通失败（`Failed to connect … port 443 after 135223 ms`），
  14:52 复测直连正常（`git ls-remote` rc=0），**无需代理**。
- r2dec 依赖 `meson` + `ninja`：本机 `python3` 无 pip、`sudo` 不可用 →
  用 **uv 装进项目 venv**：`uv pip install meson ninja`，再
  `PATH=<repo>/.venv/bin:$PATH r2pm -ci r2dec`。
- **坑：`env PATH=…:$PATH cmd` 不加引号会因 PATH 里有 `/mnt/c/Program Files/...` 含空格而炸**
  （报 `env: 'Files': Permission denied`）。必须写 `PATH="…:$PATH"`。
- 长任务（r2ghidra 编译）用 `setsid nohup … </dev/null &`，日志落 `/tmp`，用 `ps -eo pid,ppid,sid` 确认 `ppid=/init`。

## 5. 已定位的目标函数

r2 全量 `aa; aar` 约 2 分钟、识别 6511 个函数，但**并存不住项目**（见 §6 坑）。
起点用 `arm_func_boundary.py` 由池地址反推（已修「函数可带连续多池字」的 bug）。

| 函数起点 | 长度 | 引用的池/表 | 作用（现状） |
| --- | --- | --- | --- |
| `0x006d6f04` | 0x4d8 | 0x8a829c、0x8a82b8、0x8a8330 | **音声资源初始化**（`pdg` 已确认）：① 入参 `param_3` 是目录前缀（`"rom:/Plus/Sound/"`）；对 3 个 Siren 文件名各 `strlen`，`new(总长, 堆3, 对齐0x10)` 出一块缓冲，切成 **4 个槽**：`[ctx+0x48]`=前缀+`Siren14voice.bin`、`[+0x4c]`=前缀+`Siren14Voice.spp`、`[+0x50]`=前缀+`Siren14Voice.dpb`、`[+0x54]`=只前缀；② `[ctx+0x1bc]=0`（状态）、`[+0x1bd/+0x1be]=0xff`；③ 初始化 `ctx+0x7c` 起 **16 条 × 0x14 步长**的条目（`[entry+0]=-1`、其余清 0）；④ 循环 bcsar 表拼 `"rom:/"+name+".bcsar"` |
| `0x006d7d1c` | 0x574 | 0x8a829c **和** 0x7e38e4 | **Siren 语音库加载器/状态机**：读 `[ctx+0x1bc]` 状态（0..7）走 8 路 switch（跳转表 `0x6d7fa8`）；用 `0x11611c`/`0x116288`（疑锁/引用计数）、`0x2fcd88`=free、`0x121ca0`=new、`0x300e60`=strlen、`0x1317dc`=memcpy、`0x129ed4`、`0x106f9c`；据状态选 base 或 SoundEx 路径 |
| `0x006d8298` | 0x24c | — | 被 `0x6d6f04` 首行调用；读 `[ctx+0x1bc]`、`[r5+0x708]`，调 `0x66e114`；分支按状态 1/3/6/7 |
| `0x006d8bb0` | 0x2b4 | 0x8a8330 | 音效库（`rom:/Plus/Sound/` + `LP2_CTR.bcsar` + 0.25f）读取/流相关 |
| `0x006d959c` | 0xa4 | 0x8a8330 | 读 `0x8a8330+8` 的 0.25f，把 `s16`（0x230 个样本）取绝对值求峰值 → `vcvt/vmul` 归一 → 与 `1.0f` 比较钳位 |
| `0x006bccd4` | 0x624 | 0x8a8358、0x8a83e0 | **触笔/输入状态机**（原「编解码」推断作废）：取输入单例（`0x6a2844(1)`）、`[+0x54]` 键位掩码、`0x741404/0x74141c` 取触笔 (x,y)、60 点轨迹环形缓冲、状态 0→4 与平方距离阈值 0x40/0x100 |
| `0x006d84ec` | 0xb8 | — | **加载 `.dpb`（base）**：状态置 4；`0x106f9c(dst=ctx+0x1c4, path=*(ctx+0x50), 0x10, off=0, heap=ctx+0x44, req=ctx+0x1ec)` |
| `0x006d87a4` | 0xc0 | 0x7e38e4 | **加载 `.dpb`（SoundEx/DLC）**：状态置 5；path=`*(SoundEx_trio+8)`、dst=`ctx+0x1d4` |
| `0x006d854c` | 0x2ac | — | **语音请求 API `play_voice(ctx, id)`**（详见 §5d） |
| `0x006d99e8` | 0x6ec | — | **语音引擎 tick/调度器**（详见 §5d） |
| `0x142568` | 0x168 | 0x1426b8/0x1426bc/0x1426c0/0x1426c4 | **解码器初始化**：`(dec, 采样率参数, 码率, 声道)`；对象 0x1470 B（池 0x1426b8） |
| `0x142440` | 8 | — | `*(dec+0x1448) >> 3` = **字节/帧**（368>>3 = 46） |
| `0x68b174` | 0xd4 | — | 驱动侧「按声部配置解码器」：取 `*(obj+voice*4+0x34c18)` = 解码器指针，调 `0x142568(dec, p[0x3409c], p[0x34098], p[0x340a0]>1)` |
| `0x68b950` | 0x54 | 0x68b9a8 | 驱动侧「存解码参数」：`p[0x34098]=dpb[0]*800`（码率）、`p[0x3409c]=0x1b58<<dpb[1]`（采样率参数）、`p[0x340a0]=dpb[2]`、`p[0x340a4]=(float)dpb[3]` |
| `0x00742234`→`0x71eed4` | — | 0x8bb610、0x9df4a0 | `0x722034` 是跳板（`b 0x71eed4`）；真身按 `handle*0x20` 索引表 `0x9df4a0` 建播放声部，调 `0x68b8e8/0x68b950/0x68b174/0x68c81c/0x68c3f4` |
| `0x00742638` | 0x18 | — | 访问器：`ctx[0x1bf]!=0` 时返回 dpb 指针 `ctx+0x1c4` 与长度 0x10 |
| `0x00742668` | 0x78 | — | 访问器：按 id 在 16 槽里找「已加载」条目 → 返回 `(buf=slot+0x80, size=slot+0x84)` |
| `0x007427a8` | 0x78 | — | 访问器：在 `*(ctx+0x60)` 数组（计数 `ctx+0x64`）里按 `[+0x12]==id` 找 `[+8]` 指针 |
| `0x117200` | 0x864 | 0x117a14=0x176d、0x117a18=0x02222222；池 0x117a1c=`0x8abxxx` 大表 | **候选：码表/解码核心类初始化**。只调 memset/memcpy（`0x2fddd8`/`0x30004c`/`0x302b20`），操作 `obj+0x1400/0x1700/0x1000` 字段块并索引一张只读大表 → 待确认（见 §8） |
| `0x0074f3f4` | 0xd0 | 0x8a829c | 用 Siren 文件名表（用法待读） |

另外 `0x6d7814` 与 `0x007e38e4` 两处**未能反推起点**（池前无返回指令 / 函数以尾调用结束），需要人工读。

辅助事实：`0x006d8e54` 处 `bl 0x6d6f04`（0x6d8e64 所在函数调用它）。

## 5b. 已识别的库/运行时函数（读代码时的语义锚点）

| 地址 | 身份 | 依据 |
| --- | --- | --- |
| `0x00300e60` | **strlen** | `0x01010101` + `uqsub8` 的经典优化实现 |
| `0x001316bc` | **strlcpy(dst, src, size)** | 带 size 截断的字符串拷贝，返回 src 长度 |
| `0x001317dc` | **memcpy(dst, src, n)** | 经典优化拷贝，含 `0x01010101` 零字节检测 |
| `0x002fcd88` | **free(p)** | `bl 0x120534` 取堆号 → `0x9a3d00 + idx*20` 取堆描述 → 尾调 `0x115304` |
| `0x00121ca0` | **new(size, heap_idx)** | `0x9a3d00 + heap_idx*20` 取堆描述 → 尾调 `0x10de04` |
| `0x009a3d00` | 堆描述表 | 每项 20 字节，`0x2fcd88`/`0x121ca0` 都从这里取 |

已见调用例：`0x121ca0(size, 3, 0x10)` = 从 3 号堆按 0x10 对齐分配。

## 5c. Siren14 语音的读取链（2026-10-17 全链贯通）

```
0x106f9c  (统一资源/区间读取)  签名（由调用点反推）：
        func_0x106f9c(dst, path, size, offset, heap_or_flags, reqctx)
   ├─ 全局表 0x9a5200[字节@0x9a2ddc+0x98] 取 loader；非 0 →
   │     tail 调 0x10d6f8(...)          ; 0x10d6f8: 0x121ca0(0x1c,0,0x10) + 拷 0x1c B
   └─ 为 0 → 0x122908(...)
   注：0x106f9c 既能整读（off=0）也能**带 offset 的区间读**——.spp 687MB 全靠它分段读。

fcn_006d6f04  (音声资源初始化；入参 (ctx, ?, "rom:/Plus/Sound/", 0))
   ├─ 4 个路径槽：ctx+0x48 = P+"Siren14voice.bin"（**索引表**）
   │              ctx+0x4c = P+"Siren14Voice.spp"（**码流**）
   │              ctx+0x50 = P+"Siren14Voice.dpb"（**解码参数**）
   │              ctx+0x54 = P（纯目录）
   ├─ ctx+0x1bc=0（状态）、+0x1bd/+0x1be=0xff（槽号哨兵）
   ├─ 16 条 × 0x14 槽（ctx+0x7c 起）：{+0 id, +4 buf, +8 size, +0xc handle, +0x12/+0x13 flags}
   └─ 循环 5 条 bcsar 表（0x8a82b8，步长 0x14，id 0x0/0x10000000/0x20000000/0x30000000/0x40000000）

fcn_006d854c  (★语音请求 API  play_voice(ctx, id))
   ├─ id > 15 → ctx+0x1bc = 8（越界）
   ├─ ctx+0x1be = ctx+0x1bd = id
   ├─ id = slot[id].id（ctx + id*0x14 + 0x7c）
   ├─ 命中「内存缓存」两条路（不解码、直接 memcpy）
   │   A) ctx+0x914 置位：0x121ccc(&ctx+0x1e4, ctx+0x91c + id*8) → (off,size)；
   │      buf = new(size,3,0x10)；0x302b20(buf, ctx+0x918+off, size)（memcpy）
   │   B) ctx+0x68 表 + base=ctx+0x70、count=ctx+0x74：
   │      0x121ccc(&ctx+0x1e4, *(ctx+0x68) + (id-base)*8)；buf = new(...)；
   │      memcpy(buf, *(ctx+0x6c) + off, size)      ; ctx+0x6c 是常驻码流缓冲
   │   两条路都：slot[id].buf=+0x80、size=+0x84、ready=+0x8e、ctx+0x1bd=0xff、状态=0
   └─ C) 未命中 → 异步：0x106f9c(&ctx+0x1e4, *(ctx+0x48) /*.bin*/, 8, id*8, heap, ctx+0x1ec)
          ; 读的是**索引项 8 字节**（stride 8 = (off,size) 对，id*8 铁证）
          ; 句柄存 ctx+0x78，状态 ← 1（等状态机推进）

fcn_006d7d1c  (语音库状态机；状态 ctx+0x1bc，8 路表 0x6d7fa8)
   状态 1: 等 ctx+0x78 句柄完成 → ctx+0x78=0，落入 2
   状态 2: size=ctx+0x1e8、off=ctx+0x1e4；新分配后
           if (id 高位判 DLC) path = SoundEx.spp else path = *(ctx+0x4c) /*.spp*/
           0x106f9c(dst, path, size, off, heap, ctx+0x1ec) → 状态 3
           护栏：16 槽累计 size > 0x60000 就拒绝（回到状态 2）
   状态 3: 轮询句柄完成 → 数据就位
   状态 4: 置 ctx+0x1bf=1（**base .dpb 已就绪**）
   状态 5: 置 ctx+0x1c0=1（SoundEx .dpb 已就绪）
   状态 6: 解析 SDNM 头（**属于 .csidbin/bcsar 音效链，不是 .spp**）：BE u32@8、BE u16@0xc，
           拼 name+".bcsar" 继续加载 → 状态 7
   状态 7: 等 .bcsar 读完
   状态 8: 请求越界/id 无效

fcn_006d84ec / fcn_006d87a4  (两个兄弟：发起 .dpb 读取)
   0x6d84ec: 0x106f9c(ctx+0x1c4, *(ctx+0x50) /*base dpb*/, 0x10, 0, ..., ctx+0x1ec) → 状态 4
   0x6d87a4: 0x106f9c(ctx+0x1d4, *(0x7e38e4+8) /*SoundEx dpb*/, 0x10, 0, ..., ctx+0x1ec) → 状态 5

fcn_006d99e8  (★语音引擎 tick / 调度器；入参 ctx，引擎对象在 ctx+0x44)
   ├─ 三个一次性初始化（各用一个标志位守住）：
   │    [eng+0x58b]==0 → 0x6d84ec(ctx) 发起 base .dpb 读；
   │                      0x742638(ctx,&dpb,&len) 取到 → 
   │                      eng[0x5a8] = 0x722034(dpb,0,1)   ← **建解码器/声部**
   │    [eng+0x58c]==0 → 0x6d7920(ctx) 发起 SoundEx .dpb 读 → 0x7428b0(ctx) 确认 → eng[0x58c]=1
   │    [eng+0x58d]!=0 且 0x7428bc(ctx, id) → 播放待播语音：
   │                      0x7427a8(ctx, id) 取数据指针 → 描述符 → 0x6779d4/0x6779ac 提交
   ├─ 16 声道循环（eng+8，步长 0x1c）：0x71ffa8 找空闲声道；
   │    声道结束 → 回调 (**(...))(..) → 0x6d7ac4(ctx, id) 释放语音 → 0x7240fc(...)
   └─ 选待播请求 → 0x742668(ctx, id, &buf, &size) →
        描述符 {[0]=buf, [1]=size, [2]=解码器句柄} →
        0x72314c(desc, 0) →（跳板）0x71efe0(拷 desc) / 0x71e164(压入 64×0x70 命令环 0x9d7ae8)
        → 音量：0x723ad8(vol/127.0f, handle)（VFP 只在这一层用）

fcn_00722034 → b 0x71eed4  (跳板；真身 obj=[0x8bb610])
   ├─ *(u8)0x8bb610 != 2 → 直接返回
   ├─ handle = 0x68b8e8(obj[3])          ; 分配/取一个声部句柄
   ├─ 0x68b950(obj, handle, dpb)         ; **存解码参数**（见下）
   ├─ 0x68b174(obj, handle, 1)           ; **按参数配置解码器**
   ├─ 0x68c81c(obj, handle, 0x7f, 0)     ; 音量 0..127
   ├─ 0x68c3f4(obj, handle, 0x40)        ; 声像（中心 64）
   └─ 表 0x9df4a0 + handle*0x20 索引（声部状态块）

fcn_0068b950  (存参数；对象 obj，声部 voice)
   p = obj + voice*0x14 + 0x34000
   p[0x98] = dpb[0] * 800                ; ★ 码率：23*800 = 18400 bps
   p[0x9c] = 0x1b58(7000) << dpb[1]      ; ★ 采样率参数：7000<<1 = 14000
   p[0xa0] = dpb[2]                      ; 声道 = 1
   p[0xa4] = (float)dpb[3]               ; 16.0f（位深）
   p[0xa8] = dpb[2] >> 8

fcn_0068b174  (配置解码器)
   if (obj[0x356ac] & (1<<voice)) {          ; 每声部使能位
       p = obj + voice*0x14
       dec = *(obj + voice*4 + 0x34c18)      ; ★ 解码器对象指针
       0x142568(dec, p[0x3409c] /*14000*/, p[0x34098] /*18400*/, p[0x340a0] > 1)
       0x1424fc(dec, x); q[0x34320] = 0x142440(dec) >> 1   ; 字节/帧/2 = 23
       q[0x34358] = dec
   }

fcn_00142568  (★解码器初始化；对象大小 0x1470 = 池 0x1426b8)
   (dec, rate_param, bitrate, channels)
   dec+0x1440 = bitrate (18400)
   dec+0x1448 = bitrate / 50（魔数 0x51eb851f）  = **bits/帧** 368
   dec+0x1444 = rate_param (14000)
   dec+0x1450 = channels (1)
   if (rate_param == 7000)  { dec+0x144c = 14; dec+0x1464 = 320 }   ; 7 kHz 带宽 → 16 kHz/320 样本
   if (rate_param == 14000) { dec+0x144c = 28; dec+0x1464 = 640 }   ; 14 kHz 带宽 → 32 kHz/640 样本
   else 报错 0x124730
   另有：dec+0xf00 起 32 个「声道槽」（0x14250c 分配）、dec+0xf84 标志、dec+0x1454 停止标志、dec+0x146c 位置
   解码器库同族：0x1420a0=free、0x142440=字节/帧、0x1424fc=set pos、0x142754=按帧拷出 PCM、
                 0x1428a4=stop/reset、0x1426d0=另一类(0xf94)、0x1420dc=声道缓冲初始化
```

要点：

1. **索引与码流分离**：`Siren14voice.bin`（741240 B）是 **92655 组 (off,size) u32 对**，
   `off[i+1] == off[i]+size[i]` 连续；`id*8` 处的 8 字节经 `0x121ccc` 拷成 (off,size)，
   再去 `Siren14Voice.spp` 读 `size` 字节 @ `off`。**每次播放只读一条语音**，故 687MB 无需整载。
2. **`.dpb` 是解码参数块**（不是容器头）：`{23, 1, 1, 16}` =
   `{码率码, 带宽选择, 声道数, 位深}`；码率 = `23 × 800 = 18400 bps`，带宽选择 1 →
   `7000 << 1 = 14000` → **Siren14（14 kHz 带宽）= 32 kHz 采样、28 region、640 样本/帧**。
3. **帧长**：`bits/帧 = bitrate/50 = 368 bit = 46 B = 23 × u16`，与 `.dpb[0]=23`、
   与既有脚本实测的「46 B/帧」三者互证。
4. **`.spp` 无容器 magic、高熵**与「G.722.1 码流近似随机」自洽；同目录 `.bcsar`(CSAR)、
   `.bcstm`(CSTM)、`.csidbin`(SDNM) 头都正常 → 提取未加密。
5. **`.csidbin`/`.bcsar` 是另一条链**（音效/音库，状态 6/7），与 Siren14 语音无关；
   它的消费者是 `ctx+0x60` 数组（`0x7427a8` 读 `[+0x12]`/`[+8]`），与语音槽 `ctx+0x7c` 不是同一个数组。
6. **解码器对象**（0x1470 B）由 `0x142568` 配置、`0x68b174` 取用；驱动对象很大
   （`obj+0x34000` 起每声部 0x14 B 参数块、`obj+0x34c18` 每声部 4 B 解码器指针、
   `obj+0x356ac` 使能位掩码、`obj+0x356a8` 全局标志）。

## 6. 踩坑（勿重复尝试）

- `r2 -c 'Ps /tmp/r2nlp/nlpcode'` / `Ps <name>` **保存项目失败**（`ERROR: Cannot save project`），
  所以每次查询要么重跑 `aa`（~2 分钟），要么**只针对目标函数局部 `af @ <起点>`**。
- `-e anal.from/-e anal.to` 与 `-e anal.in=range` 对 `aa` **无效**：无论怎么设，`afl` 都只给出入口区那 43 个函数。
- `r2 -L | grep` 查不到 `r2dec` 的注册名，但 `pdd` **实际可用**（用 `pdd` 冒烟测过），别以 `-L` 为准。
- 字面量池里的「字符串指针」多数**不是**被代码直接 LDR 的，而是**指针表**；找调用方要按
  「池地址 → 谁加载这个池」两步走（`find_code_xref.py --pool`）。
- **r2 偶发把 ARM 误判成 Thumb**（例：`0x106f9c` 明明是 `3040 2de9` = ARM `push {r4,r5,lr}`，
  `af` 却按 Thumb 解出「unaligned」垃圾，`-e asm.bits=32` 也压不住）。
  解法：`ahb 32 @ <地址>` 手动写 bits 提示，再 `pd`。
- `pdf` 对某些函数报 `ERROR: Linear size differs too much from the bbsum, please use pdr instead`；
  改用 `pd N @ <地址>` 线性反汇编即可。
- `pdc`/`pdd` 对含**跳转表**的函数会输出碎片（`// orphan` 块，甚至
  `ERROR: Failed to retrieve block at 0x…`）——这种函数等 `pdg`（Ghidra）更靠谱。

## 7. 脚本（详见 `scripts/loveplus/SCRIPTS.md`）

- `scripts/loveplus/find_code_xref.py`：目标 VA → 找文件里存该 VA 的 4 字节位置（池）→ 反查取该池的 `ldr [pc,#imm]`；
  `--pool` 模式反过来（给定池地址找加载它的指令）。
- `scripts/loveplus/arm_func_boundary.py`：给字面量池地址，向前找函数序言/返回，推断**拥有该池函数的起点**
  （用于 `af @ <起点>` 再 `pdf/pdc/pdd/pdg`）。注意：对以 `b`/尾调用结束的函数会失败（需人工核对）。
- `scripts/loveplus/scan_arm_patterns.py`（2026-10-17 新增，直接读 `code_text_unpacked.bin`，不依赖 r2）：
  - `prologue [--range]`：扫 `push {…,lr}` 序幕 → 函数起点地图（**注意**：不保存 lr 的叶子函数会漏掉，
    如 `0x742668`；漏掉时用「调用点落在此函数体内」反证）。
  - `bl --range --external-only` / `findbl --target`：聚合/反查 `bl` 目标（跳板函数会让调用点与真身分离）。
  - `immoffs --vals 0x1bc,0x1bd,… [--range]`：按 imm12 找 `ldr/str rX,[rY,#imm]`（定位「谁读某结构体字段」）。
  - `vfp [--window]`：VFP(cp10/cp11) 指令密度直方图（找浮点重的 DSP/编解码模块；**语音模块与 0x71f000-0x726000 密度为 0**）。
  - `shift3 --shift N`：找 `…, lsl #N` 的索引寻址（定 stride）。
  - 大偏移（>0xfff）的正确扫法：先看编译器怎么造基址——本例用 `mov rX, #0x1440` 或 `add rX, rY, #0x34000`
    （imm12 = `0x90D`）/`#0x34c00`（imm12 = `0xBD3`），**按 imm12 反查比按数值反查可靠**。

## 8. 下一步

**位流层（§5e）、变换层（§5f）与移植实现（§5g）都已收尾**：`siren14.py` 已参数化、
`siren_transform.py` 提供合成层、`siren14_wav.py` 端到端出 WAV。

已完成：

1. **参数化移植（任务 1.3）**：28 区域 / 640 样本 / 32 kHz / 5 bit 速率控制（FFmpeg 只覆盖
   14 区域支，见 §5e 差异清单）；本作特有行为（速率控制跳过已达 7 的区域、可用位数上限
   `cap = 320·(nregions/14)`、超出部分 ×5/8）按游戏实现，18400 bps 下不触发。
2. **变换层**：float 逆 MLT + 正弦窗 + 50% 重叠相加；与 FFmpeg siren.c 的折叠·旋转排布
   逐样本一致；相位约定定案（§5g）；尾部 80 个系数清零（本作行为，FFmpeg 不清）。
3. **解码验证（任务 1.4）**：12 条抽样 + 全量索引勘验，无削波、无跑飞，谱与码流带功率一致（§5g）。

剩余：

1. **报告（任务 1.5）**：`output/loveplus/report/siren14_decode.md`。必须写明：
   ① FFmpeg 参照只覆盖 14-region 支；② 噪声幅度取值方式差异；③ 尾部系数清零差异；
   ④ 本作在系数域混音（引擎架构）；⑤ 定点 vs 浮点；⑥ **绝对增益未与官方解码器逐样本对齐**；
   ⑦ 相位约定的三条判据；⑧ 定点 IMDCT 旋转级符号未逐样本对照。
2. 可选：按 §5f 的四段结构做定点 IMDCT 仿真，与本实现逐样本对照（消掉 ⑧ 的残留不确定性）。
3. 可选：0x76d000-0x76f000 那片 VFP 密集代码属于哪个编解码器/音效内核（经函数指针表
   0x76bc34 调用，调用者 0x765xxx ← 0x64xxxx-0x66axxx SE/BGM 引擎）；仅当要解 BGM/SE 时才需要。
4. 可选：`reverse_code_bin.json` 的 `sections` 顺序（§5c–§5g 现排在 §6–§8 之后），需要时重排。

## 5d. 解码链：G.722.1 实现库（0x75c000-0x767000）

### 定位手段（可复用）

按「常量表反查」比按「代码形态」找快得多：把参考实现的**整数表**逐个当字节模式全仓搜，命中即得
数据地址；再用 `find_code_xref.py` 找引用它的字面量池 → 池所在函数就是实现代码。
（浮点表的匹配会被四舍五入误差干扰，整数表没有这个问题。）

本作三张表全部命中（i32 存储，与 FFmpeg 的 i16 表**同值**）：

| 表 | 值 | 游戏内地址 | 引用它的池 |
| --- | --- | --- | --- |
| `vector_dimension[8]` | 2,2,2,4,4,5,5,1 | **0x801e34** | 0x75e68c、0x76639c |
| `number_of_vectors[8]` | 10,10,10,5,5,4,4,20 | **0x801e94** | 0x75e688 |
| `expected_bits_table[8]` | 52,47,43,37,29,22,16,0 | **0x8bd118** | 0x75c4fc、0x75c7d4 |

同区还有两张 8 元表 `0x801e54 = [13,9,6,4,3,2,1,1]`、`0x801e64 = [2341,3277,4682,6554,8193,10923,16385,16385]`，
疑为定点化的标度/标准差表，**未确认**。`mlt_quant` / `noise_category5/6` 的**浮点**版本在仓内**搜不到**
→ 本作把量化表也做成了定点/整型（FFmpeg 是 float）。

### 解码入口链

```
0x142454(ctx, ch, frame_ptr, coef_out)          ← 流封装层的「喂一帧」
  ├─ 位读器状态：*(st+0x1408)=0（位计数）、*(st+0x140a)=*frame（首个 u16）、*(st+0x1410)=…
  ├─ 0x75e69c(st, per_ch_cfg, number_of_regions, coef_out)      ← ★帧解码（56 行 C）
  └─ 结果拷进 dec + ch*0x500 + 0xa08（0x500 B = 1280 B = 640×u16   ★PCM 缓冲）

0x75e69c(bit_state, unused, regions, param4)     ← 帧解码总入口
  ├─ regions==0xe(14) → 4 bit、uVar7=0x10(16)；否则 5 bit、uVar7=0x20(32)   ← 速率控制字段位宽
  ├─ 0x75e0c0(st, regions, stack_a8, stack_118)   ← 相当于 FFmpeg 的 decode_envelope：
  │      先读 5 bit 再 **−7**（= `get_bits(gb,5) - esf_adjustment`，本作 esf_adjustment=7 ✓），
  │      其后按 region 循环读差分索引
  ├─ 读 iVar6 bit → rate_control 索引
  ├─ 0x75c3dc(regions, ?, uVar7, …)               ← 相当于 categorize_regions（用 expected_bits_table）
  └─ 0x75e2b8(st, ?, regions, stack_a8, stack_208, param4)      ← 相当于 decode_vector
        └─ `*(*0x75e688 + cat*4)` = number_of_vectors[cat]
           `*(*0x75e68c + cat*4)` = vector_dimension[cat]
           `*(*0x75e690 + cat*4)` = ?（第 3 张未标定的 8 元表）
```

变换（MDCT/IMDCT + 窗）在 **0x76b67c**（唯一调用者 0x1420dc）及其下游：**0x76d000-0x76f000** 是全区
VFP 密度最高的一带（34-36%）→ **变换层是浮点，位流/量化层是定点**。
大函数 0x762354(7128 B)、0x763f2c(4620 B) 的调用者全在 0x64xxxx/0x66xxxx（驱动侧），不属语音链。

### 与标准 G.722.1 的关系（结论）

- 结构、表、常量（`esf_adjustment=7`）与 FFmpeg `libavcodec/siren.c` **逐项对上** → 本作实现的是
  **标准 G.722.1 家族**，不是私有编解码、也没有第三方中间件。
- FFmpeg 只实现 **14 region / `FRAME_SIZE 320`** 一支（`s->number_of_regions = 14` 写死，
  `REGION_SIZE 20`，14×20=280 有效系数凑 320 点变换）；本作**两支都实现**：
  `dec+0x144c` = 14 或 28（region 数）、`dec+0x1464` = 320 或 640（变换长度）。
  28-region 支的速率控制字段是 **5 bit（32 种可能）**，14-region 支是 4 bit（16 种）。
  → **既有 Python 移植（FFmpeg 派生）只有 14-region 那套，解不了本作的流。**
- 自定义码率无碍：FFmpeg 的标准路径用**包长**算可用位数
  （`init_get_bits8(gb, avpkt->data, avpkt->size)`；`sample_rate/50` 只出现在 Microsoft 变体与校验里），
  位分配由流内 rate_control 索引 + 剩余位数决定 → 18400 bps 这种非标准速率照样能解。
- 因此「46 B 帧 / 18400 bps」不需要新算法，只需要把移植版按 **28 region / 640 / 32 kHz / 5 bit 速率控制**
  重新参数化。

## 5e. 位流→系数：G.722.1 位流层全还原与码本等价性证明

本节给出**位流 → 频谱系数**这一层的完整还原结果：表清单（地址级）、帧级算法、以及把
「游戏表 vs FFmpeg 表」的等价性判定为**同一标准 G.722.1 码本**的实证。

### 定点/整数表全清单（游戏内以 i32 存储）

| 表 | 地址 | 形态 | 内容 / 语义 | FFmpeg 对应 |
| --- | --- | --- | --- | --- |
| 标准偏差 | **0x801d34** | i32 ×54（Q12） | `sqrt(10^((i-24)·0.30103))`；末尾 6 值 4096/5793/8192/11585/16384/23170 | `standard_deviation[64]`（float） |
| `vector_dimension` | 0x801e34 | i32[8] | 2,2,2,4,4,5,5,1 | 同名 |
| mlt 行长−1 | **0x801e54** | i32[8] | 13,9,6,4,3,2,1,1 → 行长 `d` = 14,10,7,5,4,3,2,2 | 无（FFmpeg 用幂掩码） |
| 行长倒数 | **0x801e74** | i32[8] | `2^15/d` = 2341,3277,4682,6554,8193,10923,16385,16385 | 无（编译器生成整除用） |
| `number_of_vectors` | 0x801e94 | i32[8] | 10,10,10,5,5,4,4,20 | 同名 |
| 差分码树 | **0x8bbb38** | i32[28][23][2] | **行 0 全零占位**；行 i = FFmpeg `differential_decoder_tree[i-1]` 的前 46 值（逐值吻合） | `differential_decoder_tree[27][24][2]` |
| `mlt_quant` | **0x8bcf58** | i32[7][16]（Q12，行距 16 字） | ÷4096 后与 FFmpeg 的 float 表偏差 ≤ 0.0006 | `mlt_quant[7][14]`（float） |
| `expected_bits_table` | 0x8bd118 | i32[8] | 52,47,43,37,29,22,16,0 | 同名 |
| 码树（7 棵） | 指针表 **0x8bf8e0** → 0x8bd138 / 0x8bd6d8 / 0x8bd9c0 / 0x8bdb38 / 0x8beb70 / 0x8bf1f0 / 0x8bf7e8 | i32，**堆式布局** | 结点 n 的子节点 = `tree[2n]`、`tree[2n+1]`；值 ≤0 为叶，码 = −值 | `decoder_tree0..6`（值即下标、奇数为叶） |
| 噪声常数 | **0x8bf98c** | i32[3]（Q15） | 5793 / 8192 / 23170 = 0.17678 / 0.25 / 0.70711（类别 5/6/7） | `noise_category5/6` 的**平台值**；FFmpeg 是 21 元表、按「区域非零系数个数」取行，本作只取单值（见下「差异」） |

相邻地址：0x801e64 是 0x801e54 与 0x801e74 之间的空档（未使用）。

### 帧级算法（`0x75e69c`）

```
frame_decode(bitreader br, coefs_out, nregions=28):
    rc_bits, n_rc = (4, 16) if nregions == 14 else (5, 32)      # 5 bit / 32 种（本作）
    decode_envelope(br, nregions, std_dev[], power[])           # 0x75e0c0
    rate_control = br.read(rc_bits)                             # MSB-first
    categorize_regions(nregions, br.bits_left, n_rc, power, cats, balance)   # 0x75c3dc → 0x75c500
    for i in 0..rate_control-1:                                 # 0x75e69c 内联
        r = balance[i]; if cats[r] < 7: cats[r]++
    decode_vector(br, coefs_out, nregions, std_dev, cats)       # 0x75e2b8
```

`decode_envelope`（0x75e0c0）：`ESF = read(5) - 7`；区域 1..27 各走一次差分码树
（叶值 ≤0 → 增量 `= -叶值`，`power[i] = power[i-1] + 增量 - 12`，与 FFmpeg 的
`power[i-1] - index - 12` 等价）；最后 `std_dev[i] = table_0x801d34[clamp(power[i]+24, ≤53)]`。

`categorize_regions`（0x75c3dc + 0x75c500）与 FFmpeg 同构：`offset=-32, delta=32→1`
二分，`cat = clamp((offset+delta-power)>>1, 0, 7)`，`Σ expected_bits_table[cat] >= available-32`
则 `offset += delta`；再跑 min/max 调整循环（`n_rc-1` 次）产出 `balance[]`，最终
`cats = max_rate_categories`。**两处与 FFmpeg 不同**：

1. `n_rc` 是参数（16/32），FFmpeg 里硬编码 16；`balance` 长度 `n_rc-1`（31）。
2. 速率控制施加时**跳过已为 7 的区域**、且最多走 `len(balance)` 步（FFmpeg 不判断直接 `++`）。

另有游戏自己的**可用位数上限**（FFmpeg 完全没有）：`K = nregions/14`（编译器用魔数 0x92492493
生成，实测 14→1、28→2），`cap = 320·K`（14 region→320 bit、28 region→640 bit）；
`available > cap` 时 `available = cap + (available-cap)·5/8`。本作 46 B 帧 → available ≈ 230 bit
< 640 → **该规则不触发**，但移植到其它码率时需要。

`decode_vector`（0x75e2b8）：逐区域，`cat < 7` 时重复 `number_of_vectors[cat]` 次
「走码树得码字 → 拆成 `vector_dimension[cat]` 个量化下标 → 每个非零下标读 1 个符号位」；
系数 = `(mlt_quant[cat][digit] · std_dev · 22? + 0x800) >> 12`（Q12 乘加四舍五入），输出 **i16**。
出错时把后续区域类别置 7。`cat ≥ 5` 时叠 dither：`noise = (noise_table[cat-5]·std_dev + 0x4000) >> 15`，
每 10 个系数取一次 4 字 LFSR（`state[3]+state[0]`）的 16 位字，逐位决定 ±noise 写入为 0 的系数
（cat 7 全部重写）。**与 FFmpeg 的 dither 结构一致**（每 10 系数一次 `get_dw`）。

### 码本等价性证明（决定性结论）

游戏的码树是**堆式布局**、码字拆解用**按行长整除**（`digit = code % d; code //= d`，且
digit0 落在输出数组**末位**），与 FFmpeg 的「值即下标、奇数为叶」+「2 的幂掩码」表面完全不同。
判据：枚举**所有比特路径**（≈1276 条），比较两套码本给出的**分量下标元组**。

```
scripts/loveplus/siren14_framecheck.py codebook
  cat0: 路径 181/181，元组一致 181/181      cat4: 209/209，一致 209/209
  cat1:  94/94            94/94            cat5: 192/192，一致 192/192
  cat2:  48/48            48/48            cat6:  32/32，一致  32/32
  cat3: 520/520          520/520
```

结论：**两套码本语义等价**——游戏的树只是同一标准码本的另一种存储。故
**本作 `.spp` 流 = 标准 G.722.1 流**，既有 FFmpeg 派生的 `siren14.py` / `siren_tables.py`
**可以直接用来解**，只需改参数（28 region / 640 样本 / 32 kHz / 5-bit 速率控制）。

### 判据勘误：「位消耗必须精确等于帧长」不成立

最初设计的判据是「一帧解完必须正好用掉 368 bit」。实测**不成立**：编码器不填满帧，
`bits` 子命令在 voice 0 前 40 帧上给出帧尾剩余 0~21 bit（8 帧恰好填满，其余留零或随机尾）。
所以「闭合」不能当判据；**决定性判据是上面的码本等价性**。`bits` 子命令保留用于
「解码是否跑飞/越界」的回归检查（两套约定在 40/40 帧上都能解完、不越界）。

### 与 FFmpeg 的真实差异（写报告时必须写明）

1. FFmpeg 的 `siren.c` **没有** 28-region 分支（只有 14 region / 320 样本 / 16 种速率控制）。
   本作走 28 region / 640 / 32 种，是 FFmpeg 未覆盖的一支。
2. 噪声幅度：本作按类别取单一平台值；FFmpeg 按区域非零系数个数索引 21 元表。低非零数区域
   的舒适噪声幅度会不同（波形层面可见，听感影响小）。
3. 可用位数上限（320K + 5/8 压缩）：本作有、FFmpeg 无（本作 18400 bps 下不触发）。

## 5f. 变换层（系数→PCM）：定点 IMDCT 0x75dd2c + 窗/重叠相加 0x76b67c，以及整帧频域混音 0x1420dc

本节补上「频谱系数 → PCM」这一层（任务 1.3 的最后一块），并更正上一轮的一个误判。

### 结论：本作变换层是**定点**，不是浮点

| 函数 | 地址 | 大小 | 职责 |
| --- | --- | --- | --- |
| 窗 + 重叠相加 | **0x76b67c** | 300 B | 调 IMDCT → 加正弦窗 → 与上一帧尾相加 → 写 PCM；唯一调用者 `0x1423bc`（语音链） |
| 快速 IMDCT | **0x75dd2c** | 896 B | 定点逆 MLT（N=640 或 320）；只被 0x76b67c 调用 |

定点证据：i16 乘 + `>>0xd/0xe/0xf`、`+0x1000/0x2000/0x4000` 四舍五入、负向饱和到 `0x8000`
（`^0x7fff ^ >>31` 惯用法，池常数 `*0x76b7b0 = 0x7fff`）。

### `0x75dd2c` = 定点快速 IMDCT（10×2ᵏ 分解）

640 = 10×2⁶、320 = 10×2⁵（`param_3 == 0x140` 选 320 分支，log2 级数 6 vs 7）。四段结构：

1. **前置蝶形**：按 `(a+b+1)>>1`、`(a−b+1)>>1` 处理 N 个输入，符号/取反决策取自一张
   **位模式表**（每个 u32 供 16 次迭代，每迭代 2 bit）：`0x8bf8fc`（320 用，10 字）、
   `0x8bf924`（640 用，20 字；表区间 0x8bf924-0x8bf974 恰好 80 B = 20 字 ✓）。
2. **log2 级基 2 蝶形**（双缓冲乒乓，栈上两个 640×i16 缓冲）。
3. **10 点逆 DCT-IV 核**：表 **0x801eb4**，i16 Q15，`tab[j] = round(32768·cos((2j+1)π/40))`
   （前 10 项逐值吻合）；按 **5 元素步长阶梯**索引：第 n 个输出取 `tab[5n .. 5n+9]` 与同一组
   10 个输入做点积，`(Σ + 0x4000) >> 15`。每块 10 输出，共 64 块 → 640 ✓。
4. **旋转级**：表 **0x8bf974**，i16 (cos,sin) 对，Q14（`>> 0xe`），复数式旋转
   `out = (c·a − s·b)>>14`、`(c·b + s·a)>>14`；最后 memmove 到输出。

### 窗表（3 张，验证到 ≤1 LSB）

三张表都是 **i16 交替 (sin φ, cos φ) 对**，幅度 `G = 18317`（≈0.5590·2¹⁵）：

| 表 | 地址 | 长度 | 用途 | φ |
| --- | --- | --- | --- | --- |
| A | **0x802954** | 640 i16 = 320 对 | N=320 帧 | `φ_j = (j+0.5)·π/640` |
| B | **0x802e54** | 640 i16 | N=640 帧前半 | `φ_j = (j+0.5)·π/1280` |
| C | **0x803354** | 640 i16 | N=640 帧后半 | `φ_{j+320}` |

拟合结果：三张表对 `G·(sin φ_j, cos φ_j)` 的**最大偏差 ≤ 0.99 LSB**（A/B/C 均最佳 G=18317）。
即窗函数 `w[k] = G·sin((k+0.5)·π/1280)`（k=0..639，2N = 1280），与 FFmpeg 的
`window[i] = sinf((i+0.5) * M_PI_2 / 320)` **同形**（FFmpeg 的 320 ↔ 本作的 640）。
对子 `(s,c) = (w[j], w[639−j])` 满足 `s² + c² = G²`（单位对），这正是 TDAC/`ff_vector_fmul_window`
所依赖的旋转形式。代码选表：`N/2 == 320`（即本作 N=640）→ (B, C)；否则 (A, A+0x280) ✓。

### `0x76b67c` 语义（窗 + 重叠相加）

```
fcn_76b67c(coefs /*r0*/, prev_tail /*r1*/, pcm_out /*r2*/, N)
    imdct(coefs → buf[N])                       # 0x75dd2c
    for j in 0..N/2-1:
        out[J1] = sat((c_j·prev_tail[j] + s_j·buf[N-1-j] + 0x1000) >> 13)   # 重叠相加
        out[J2] = sat((s'_j·buf[N/2+j] − c'_j·…)       + 0x1000) >> 13)      # 新尾
    memmove(prev_tail ← buf[N/2..N])            # 保存新尾给下一帧
```
与 FFmpeg 的 `vector_fmul_window`（TDAC 旋转 + 重叠相加）**同构**；50% 重叠、hop = N/2 = 320，
每帧输出 N=640 样本（20 ms @32 kHz ✓），上一帧尾缓冲每声道 0x280 B = 320 i16 ✓。

### 整帧流水线 `0x1420dc`（848 B）：**频域混音**

```
fcn_1420dc(obj, nch, pcm_dst[])
    memset(obj + ch*0x500, 0x500)  for ch in 0..max(nch,1)-1     # 清系数缓冲（640 i16/声道）
    for i in 0..31:                                              # 32 个 voice 槽（obj+0xf00）
        v = obj[0xf00 + i*4];  if v == NULL or 槽被掩码禁用(obj+0xf84 的 bit i): continue
        n = v.vtbl[0](v)                                         # 本帧样本数
        0x142454(v, 0, n, v+2)                                   # 位流→系数（→ 0x75e69c）
        ...（单/双声道分支、可选声道平均降混 (a+b+1)>>1）...
        step = frame_len*14/16                                   # 640→560（= 20×nregions）
        gain = v[·]*0x14243c>>15（仅 frame_len==320 时）
        for ch, k in (nch, step):
            obj[ch*0x500 + k] += sat((v_ch[k]·vol·gain + 0x2000) >> 14)   # 系数域累加！
    for ch in 0..nch-1:
        0x76b67c(obj + ch*0x500, obj + ch*0x280 + 0xa00, pcm_dst[ch], obj[0xf88])
    obj[0xf90] = (有 voice 解码成功)
```
关键点：
1. **混音在 MLT 系数域完成**（线性变换 ⇒ 与时域混音等价，但整帧只需一次 IMDCT/声道）——多达 32 路
   语音共享同一帧格式（28 region / 640）。
2. 累加只覆盖 **前 560 个系数**（`step = 640×14/16 = 560`）⇒ 与 §5e 的 28×20=560 完全吻合，
   **印证「位流只编码 560 个系数，其余 80 个为 0（14 kHz 带宽上限）」**。
3. 字段：`obj+0xf88` = 帧长（640）、`obj+0xf90` = 上一帧是否有声（无则输出静音）、
   `obj+0xf80` = 降混标志、`*0x14242c` = 0x7fff、系数缓冲 `obj + ch*0x500`、
   上一帧尾 `obj + ch*0x280 + 0xa00`、输出 PCM 由调用者按声道传入。
4. `0x142454`（逐帧封装）= 填好解码器字段（+0x1448 bits/帧、+0x144c region 数）后调
   **0x75e69c**，再把结果（0x500 B/声道）拷到 `v + ch*0x500`。

### 勘误：0x76d000-0x76f000（VFP 密度 34-36%）**不是**语音链的变换层

上一轮把该区当作变换层候选，**错**。证据：
1. 该区**没有** `push {…, lr}` 型序幕（`prologue --range 0x76b000-0x770000` 只找到 7 个，全在 0x76b000-0x76c000），
   全仓**无任何 `bl` 落入 0x76d000-0x76f000**；
2. 它只被函数指针表 **0x76bc34**（位于 0x76bb14 内，41 项 → 0x76d22c/0x76d318/…/0x76ee0c，
   其中 0x76e724/0x76e968/0x76ebb4/0x76ee0c 各重复 8 次）间接调用；
3. 0x76bb14 的 4 个调用者全在 **0x765xxx**，而 0x765xxx 只被 0x64xxxx-0x66axxx
   （SE/BGM 引擎）调用；
4. 语音链（0x14xxxx）对 0x75c000-0x772000 的全部调用只有：0x75c3b8、0x75c7d8、0x75e69c、
   0x76b67c（另 0x145xxx 调 0x76b460/0x76b634）。

⇒ 该区属于**另一个编解码器/音效内核**（VFP 密集），与 Siren14 语音解码无关。未做，见 §8。

### 与 FFmpeg 的差异（补充，写报告时并入）

1. FFmpeg `number_of_valid_coefs = REGION_SIZE·nregions = 280 < FRAME_SIZE=320`，
   多出的 40 个槽位**不清零**（保留上一帧陈旧值，`imdct_in` 是持久缓冲）；本作显式 memset
   整个 640 系数缓冲，且只累加前 560 ⇒ 高 80 个系数为 0。**移植时应按本作清零**。
2. 本作变换为定点（Q13/Q14/Q15 + 饱和），FFmpeg 为 float。移植用 float IMDCT + FFmpeg 窗/OLA 即可，
   差异在 ±1 LSB 量级（听感无关）。窗/重叠约定（正弦窗 `sin((k+0.5)π/2N)`、50% 重叠、
   每帧 N 样本）两者一致 ⇒ **本作流可用「FFmpeg 表 + 28-region/640/5-bit 参数 + 清零尾部系数」解**。
3. 本作把「音量 × 多路混音」放在系数域（引擎架构，非标准内容）。

## 5g. 变换层验证与可复现实现（2026-10-17）

§5f 给出变换层的静态还原；本节记录**移植实现 + 数值验证 + 两个悬而未决项的定案**。

### 实现（`scripts/loveplus/`）

| 模块 | 职责 |
| --- | --- |
| `siren_transform.py` | MLT 合成层：`mlt_window` / `imlt_basis` / `forward_mlt`（仅自检用）/ `Synthesizer`（逐帧逆 MLT + 窗 + OLA）/ `synth_folded`（折叠·旋转式等价排布）/ `out_scale_default` / `selftest` |
| `siren14.py` | 位流 → 系数（G.722.1 家族；`configure(nregions=…)` 切档，本作 = 28 区域 / 640 / 32 kHz / 5 bit 速率控制） |
| `siren14_wav.py` | 驱动：`Siren14voice.bin` 索引 → `.spp` → 系数 → WAV；`--ref-check` / `--stats-csv` / `--probe` |

正/逆变换（N = 每帧系数数 = 每帧样本数，窗长 2N，hop = N）：

    y[m] = Σ_k X[k]·cos(π/N·(m + 0.5 + N/2)·(k + 0.5))    m = 0..2N-1
    w[m] = sin((m + 0.5)·π/(2N))
    pcm[i] = w[i]·y_k[i] + w[N+i]·y_{k-1}[N+i]            i = 0..N-1

### 数值验证（`selftest`，N = 640）

| 量 | 值 | 含义 |
| --- | --- | --- |
| `gain` | 3.200e+02 = N/2 | 未归一化 MLT 对的固有增益 |
| `kernel` | **0.000e+00** | 分析核与标准 MDCT 定义式 `cos((2j+1+N)(2k+1)π/(4N))` 逐元素完全一致 |
| `exact` | 2.4e-07 | 补 2/N 后往返（完美）重构相对误差 |
| `window_orth` | 4.4e-16 | max\|w[i]² + w[i+N]² − 1\|（TDAC 条件） |
| `folded` | 6.5e-12 | `synth_folded` 与 `Synthesizer` 在同一系数上的相对 RMS 差 |

`--ref-check`（真实语音 voice 0/1/2）再验一次：折叠·旋转排布 vs 整长 OLA，标量比 = 1.000000、
归一相对误差 ≈ 2.0e-07。

### 相位约定定案：合成端不做 (−1)^k 翻转

1. 分析核 `imlt_basis().T` 与标准 MDCT/MLT 定义式逐元素一致（`kernel` = 0；与 FFmpeg
   `ff_tx_mdct_naive_fwd` 的公式也一致）。本作窗表拟合式 `G·sin((k+0.5)π/1280)` 正是 Malvar
   MLT 的 2N = 1280 正弦窗，基函数含 (N+1)/2 偏移 ⇒ 即 MLT 定义式。
2. (分析, 合成) 完美重构（补 2/N 后 2.4e-07）。
3. FFmpeg siren.c 的「折叠输出 + 旋转式重叠相加」排布，在**不翻转**系数时与本实现逐样本一致
   （真实语音 ~2e-7）。

偶下标取负得到另一条信号（与本实现互相关 ≈ 0.005，与 x 的相关 ≈ −0.01），**不采用**。FFmpeg
源码里的 `imdct_in[i] *= -1, i += 2` 属其通用逆 MDCT（AV_TX）的输入约定；逐字抄录其 naive
参考实现（`ff_tx_mdct_naive_inv`，prio MIN 的死代码路径）无法复现，故不作判据。
残留不确定性：本作定点 IMDCT（0x75dd2c）的**旋转级符号**未逐样本对照（只核了窗表与结构），
若要绝对对齐，按 §5f 的四段结构 + 三张表做定点仿真再逐样本比。

### std 表语义（推翻「系数过大 = 解码 bug」的怀疑）

游戏 0x801d34 = 54 项 i32 **Q0**：`std[i] = round(2^((i-24)/2))`（等价 `10^((i-24)·0.3010299957)`），
按 `arp + 24` 索引，arp ∈ [−24, +29]（本作 `GAME_ARP_MAX = 29`）。故回放增益最大 2^14.5，
响帧（arp 18-20）系数合法可达 1e5 量级：实测最响帧 max|coef| = 136613，而 `q·std` 的比值
仍 ≤ 4.724（码本上限内）⇒ **系数幅度正常**，不是解码错误。

### 输出标量（绝对增益）

未归一化逆变换最响帧峰值 252250，整体标量 > 1/7.7 必削波。取
`out_scale = sqrt(2/N)/32768`（教科书正交归一 ÷ Q15 口径；N = 640 时 1.706e-06）：
voice 0 峰值 0.430 / RMS 0.0969（约 −20 dBFS）。备选 `2/N`（Q15 口径下峰值仅 0.024，过轻）、
`1/32768`（FFmpeg 净效果，会削波）。**该标量与游戏/FFmpeg 的逐样本电平未对齐，属整体增益**
（±6 dB 内），需要时用 `--gain` 覆盖。

### 谱一致性（按 500 Hz 并带，28 带 = 0–14 kHz）

按 500 Hz 归并的实测谱 vs 码流逐区域系数带功率（口径唯一：28 个 500 Hz 带，即 560 个系数
= 28×20 覆盖的 0–14 kHz）：相关系数 voice 0 = **+0.996**、voice 5 = +0.986、voice 1000 = +0.956；
>14 kHz 能量占比 = 2.7e-07 / 8.1e-06 / 0（voice 0/5/1000）。把系数带功率镜像后再算相关转负
⇒ 频谱方向正确、无镜像与混叠；>14 kHz ≈ 0 与「系数 560..639 恒为 0」一致。
（注：早先一次用 32 带（0–16 kHz）算得 +0.988/+0.967/+0.976 与 >8 kHz 占比 5.3%/3.6%/0.9%，
属更旧的一组口径，已统一为上面的 28 带口径。）

### 端到端统计（12 条抽样 + 328 条全量抽样 + 索引勘验）

- `Siren14voice.bin` = 92655 条 × 8 B `(off,size)`：offset 单调、覆盖 `.spp` 100%
  （`max(off+size) = 687534906` = 文件大小）、size 全为 46 的倍数（voice 92654 为空条目 size = 0）。
- 12 条抽样（voice 0-9 + 1000 + offset 最大的 46327；表见
  `data/loveplus/nlp_plus/decoded/decode_stats_sample.csv`）：帧 43–213、时长 0.86–4.26 s、
  峰值 **0.405–0.568**（无削波）、RMS 0.060–0.107、峰均比 4.4–6.8、边界跳变 0.63–1.33、
  非零系数/帧中位 504–518、原始逆变换峰值 237474–332834。
- 328 条全量抽样（每 283 条取一条，`decode_stats_spread.csv`）：峰值 0.000–**0.801**（中位 0.606）、
  RMS 中位 0.1203、时长 0.04–20.28 s、帧数 2–1014、峰均比中位 4.9、边界跳变中位 0.97、
  **削波 0 条**。
- 解码诊断 STATS：`arp_gt_game_max = 0`、`rc_skip7 = 0`（18400 bps 下速率控制守卫未触发）。

## 5h. `.dpb` 的作用域与保真分档（2026-10-17）

起因：用户提问「dpb 是不是所有音频解码都要用？有没有可能特定语音用高保真/低保真参数？」
——静态核了一遍代码与两个 ROM，结论如下。

### 结论 1：dpb 只服务 Siren14 语音链，不是全音频系统通用

- dpb 的 16 字节只被两处读：`0x6d84ec`（base `Siren14Voice.dpb`）、`0x6d87a4`（追加データ
  `SoundEx/Siren14VoiceEx.dpb`）。
- dpb 字段的唯一消费者是 `0x68b950`（把 4 个字段写进引擎对象）→ `0x68b174`（配置解码器）→
  `0x142568`（Siren14 解码器 init）。而 `0x142568` **全仓只有一个调用者** `0x68b1d8`，
  `0x68b950`/`0x68b174` 也各只有一个调用者（`0x71ef1c`/`0x71ef2c`，建声部跳板内）。
- BGM（`STRM_BGM*.bcstm` = CSTM）与音效（`LP2_CTR*.bcsar` = CSAR + `.csidbin`/SDNM）各有自己的
  容器头（采样率/编码类型在其中），不经过 dpb。

### 结论 2：粒度是「音库级」，且架构上确实支持分档

- 引擎一次初始化里读 dpb 并建解码器（`0x6d99e8` 的 `[eng+0x58b]`/`[eng+0x58c]` 一次性标志），
  之后同一音库的 92655 条语音共用这套参数 —— 索引表里只有 `(off,size)`，没有任何逐条参数通道。
- `0x142568` 反汇编（本次实读）：
  - `bits/帧 = bitrate / 50`（魔数 `0x51eb851f`），写入 `dec+0x1448` 与 `dec+0x1468`；
    即 `字节/帧 = 2 × dpb[0]`（23 → 46 B）。
  - `rate_param = 7000 << dpb[1]` 只认两个值：`7000` → `dec+0x144c = 14` region、`dec+0x1464 = 0x140`
    (320 样本)；`14000` → `0x1c` (28 region)、`0x280` (640 样本)；**其它值 `bl 0x124730` 报错**。
  - 对位率码 `dpb[0]` **不做范围校验** → 原理上帧长可换。
- 也就是说：`dpb[1]` 是「7 kHz 带宽（16 kHz 采样 / 320 样本 / 14 region）」与「14 kHz 带宽
  （32 kHz / 640 / 28）」两档的开关，`dpb[0]` 决定帧长 —— 分档能力确实存在，只是本作只用了一档。

### 结论 3：本作（以及前作）都只有一个音库、一种配置

- base dpb = `{23, 1, 1, 16}` → 18400 bps、14 kHz 带宽、单声道、16 bit，即**高档**。
- 全库单一配置的判据：92655 条 `size` **全是 46 的倍数**，且 `.spp` 被 46 B 帧整除
  （687534906 = 46 × 14946411）。若存在别的帧长/配置，size 不会一致地对齐 46。
- 卡带 RomFS 名表（UTF-16，~4.60 MB 处）实测只有一套：`Siren14voice.bin` / `Siren14Voice.spp` /
  `Siren14Voice.dpb`；**没有 `Siren14VoiceEx.*`** → 追加データ（SoundEx）那套 dpb 不在卡带里，
  代码里为它预留的读取路径（状态 5 / `0x6d87a4`）在本作卡带内容上不会触发。
- 跨作品核对：`New Love Plus (Japan)` 与 `New Love Plus+ (Japan)` 两个 ROM 里，按 dpb 形状
  （`{1..64, 0..3, 1..2, 8/16/24/32}` 小端 u32）扫全盘，**形状成立且唯一的 dpb 都是 `{23,1,1,16}`**
  （+ 版 @ROM 偏移 747015024，非 plus 版 @965856128）→ 两作用同一档。

### 结论 4：逐帧的「保真度」变化来自 5 bit 速率控制，而不是逐条配置

- 每帧 5 bit 的 rate control（32 档）+ 7 类码本决定这一帧 28 个 region 里哪些分到多少 bit。
- 实测（最长的三条：2043 / 1720 / 1249 帧）：每帧**有码 region 数 24–28，中位 28**（分布
  28:1406 / 27:527 / 26:96 / 25:13 / 24:1）。说明 18400 bps 对 28 region 这档预算够用，
  本库里几乎不存在「被降到低带宽」的帧；帧间差异主要在量化精度与包络上。

### 操作含义（将来遇到别的音库）

- 若某音库的 `dpb[1] = 0`（7 kHz 档）：`siren14_wav.py --profile g7221-16k` + `N = 320` 合成。
- 若 `dpb[0] ≠ 23`：`--bitrate = dpb[0] × 800`（帧长 = `2 × dpb[0]` 字节；驱动已按 bps 推算帧长）。
- 找 ROM 里的 dpb 的两步法（本次用过，可复用）：① 搜 UTF-16 名表（3DS RomFS 名是 UTF-16LE，
  ASCII 搜不到）拿到 `*.dpb` 条目的 `(dataOffset, size=16)`；② 按 dpb 形状扫全盘、再用配套
  `.bin` 索引结构（`off[i+1] = off[i]+size[i]`、`size` 为偶数）反解 RomFS 数据区基址做自校验。

## 5i. ITU-T G.722.1 官参对照：三处修正与「无跨帧平滑」裁定（2026-10-17）

ITU-T G.722.1 **官参定点实现**已落地并作为本仓库 Siren14 解码器的 ground truth。

### 来源与编译（可复现）

- 源码：*ITU-T G.722.1 (2005-05) — Fixed point implementation for main body and Annex C*，
  Software Release 2.1 (2008-06)，© 2004 Polycom, Inc.（即标准配套的官参代码；未入库，
  仅作对照用，见 `repos/` 规则）。本会话放在 `/tmp/02_static-re/ref/`。
- 编译（`round` 与 `math.h` 冲突需改名；`tables.c` 含非 UTF-8 字节，读时用 `latin-1`）：
  `perl -pi -e 's/\bround\s*\(/stl_round(/g' *.c *.h` 之后
  `gcc -O2 -w -o refdec main_ref.c decoder.c coef2sam.c dct4_s.c tables.c huff_tab.c count.c common.c basop32.c`
- 自带驱动（本次新写，在 ref 目录内）：`refdec <in.spp> <out.pcm> <nregions> <bits> [coef_out from to]`
  （真实比特流解码；28 区域 / 368 bit → `frame_size=640`、`nvalid=560`）、
  `refsynth <coef.bin> <out.pcm> [dct_length] [mag_shift]`（只做合成）。
  输入 `.spp` 片是**原始字节**（不必 `swap16`；官参按 16 位小端字读、bit15 起取）。
- 官参参数档与本作一致：`NUM_CATEGORIZATION_CONTROL_BITS 4`/`POSSIBILITIES 16`、
  `MAX_… 5`/`32`、`NUMBER_OF_REGIONS 14`/`MAX 28`、`REGION_SIZE 20`、`MAX_DCT_LENGTH 640`、
  `ESF_ADJUSTMENT_TO_RMS_INDEX 7`、`MAX_BITS_PER_FRAME 960`、`bit_rate/50` fps。

### 逐系数对照（决定性判据）

`/tmp/02_static-re/cmp_coef_detail.py <voice> <模块> <帧数>`：分「编码位（cat≤4）」与
「噪声位（cat≤7 中 cat==7 的区）」比我们的系数与官参 `refdec` 导出的系数。

- **符号一致率恒为 100%**（编码位与噪声位都是）。
- 比值 = `22 × 2^mag_shift`：相邻帧若 `mag_shift` 差 1，比值就 22 ↔ 44 翻倍
  （官参 `mag_shift` 是纯定点动态范围技巧，`rmlt_coefs_to_samples` 在 OLA 前把 DCT 输出
  整体 `shr 2^mag_shift`，且 `old_samples` 存的是**移位后**的值，帧间不产生尺度跳变；
  本作是固定 Q13 窗、无逐帧定标 → **不需要移植**，只在对照时换算）。
- 噪声位比值恰好 `5793/256 = 22.6289`（cat 7）→ 游戏表 0x8bf98c 的 `23170/32768`
  精确到 <0.01%。

### 由此坐实、已落 `scripts/loveplus/siren14.py` 的三处修正（2026-10-17）

1. **噪声幅度与编码系数同单位**：游戏里 `系数 = (mlt_quant_Q12 × std) >> 12`、
   `噪声 = (tbl_Q15 × std) >> 15`，两者同单位；本实现给系数乘了 `SCALE_FACTOR=22`，
   噪声必须同乘，否则噪声低 22×（≈ −27 dB）。表 0x8bf98c 是**单一类别平台值**
   （cat5=5793/32768、cat6=8192/32768、cat7=23170/32768），**不是** FFmpeg 的按非零计数查表；
   已由官参 `decoder.c` 的 `noise_fill_factor[3] = {5793, 8192, 23170}` 独立证实。
2. **`dw` 伪随机状态跨帧持久**：游戏把状态存在解码器对象上（`dec+0x1420+slot*16`），
   官参的 `randobj`（`get_rand`）同样跨帧。模块级 `_DW_STATE` + `siren14.reset_dw()`
   （每条语音流起头调用；`siren14_wav.py` 的 `decode_voice` 已加）。
3. **噪声符号位按相邻 10 系数分块**：官参取两次 `get_rand`、各覆盖**相邻** 10 个系数
   （0–9 / 10–19）；FFmpeg 写成 `dw1/dw2` 偶奇交错。照抄 FFmpeg 时长音频符号位与官参
   不一致，改分块后 100% 一致。

### 「平均 / 平滑」裁定：**没有跨帧平滑**

用户问「源码里有没有做平均/平滑」。逐条查完（官参全源 + 游戏 code.bin）：

- 官参里所有 `shr(...,1)` 都不是平滑：`common.c:359/443` 是类别量化步长
  `j = (offset − rms_index) >> 1`；`decoder.c:335` 是 `mag_shift` 搜索里把标准差之和
  逐次减半；`coef2sam.c:91` 是 `half_dct_size = shr(dct_length,1)`；`dct4_s.c:189/193`
  与 `dct4_a.c:228/315/320` 是蝶形归一化。
- **唯一的真「平均」**：合成 DCT 输入蝶形 `(x ± y + dither) >> 1`
  （官参 `dct4_s.c:187-193`，注释自述用于消除截断偏置；dither 是 0/1 固定位模式，
  表 `dither[320]` / `max_dither[640]`，定义在 `dct4_s.h:90/124`）。
  **游戏 code.bin 同构**：`0x75dd8c`–`0x75ddb4` 同一蝶形，dither 位取自
  `0x8bf8fc`（320 档）/ `0x8bf924`（640 档）的 **32 位打包位表**（取位循环 31→1、
  每用完 4 字节表指针 +4）。→ 这是**块内**蝶形缩放（整体增益意义），不是帧间平滑。
- OLA 本身本身就是相邻两帧的**加权交叉淡化**（游戏 `0x76b67c`：两次 `smulbb` 相加 +
  `+0x1000` 舍入 + `asr #13`；官参 `L_mac` 累加 + `stl_round(L_shl(sum,2))`）。
- **没有**：跨帧系数平滑 / EMA / 低通、后置滤波器、谐波噪声整形、自适应增益平滑。

### 仍未决：波形与官参不相关（谱一致）

- 逐帧 28 带（0–14 kHz）幅度谱：全部 **±0.6 dB** 内，逐帧谱形相关中位 0.974、
  逐帧总能量相关 0.885（见 `/tmp/02_static-re/cmp_spec.py`）。
- 样本级：lag 0 相关 ≈ 0；lag 640（一帧）处稳定为 **−0.3** 左右（15 条长音频全部如此）。
- 已排除：逐块反转、逐块反转+取负、整体取负、半块循环移、奇偶帧取负（逐帧相关符号
  **不交替**）、单系数探针变体、系数域顺序/偶数取负变体。
- 结论方向：两边「系数→样本」的**折叠/相位排布约定**不等价（官参是标准文本定义的
  「反序 MLT」：样本反序 + MLT + 偶数下标取负；FFmpeg 系是另一种等价排布）。
  但**谱一致**说明量值正确，差异在相位/排布层。
- **旁证**：两边解码时长逐条完全一致（同一 640 样本/20 ms → 32 kHz），样本级边界跳变
  指标（`boundary_continuity`）都在 0.88–1.07 的健康区间 → 「语速不对」不是解码器
  造成的（要怀疑的是播放端/游戏侧的采样率处理）。
- 关键判据（尚未做）：用官参**自带编码器**（`encoder.c`/`encode.c`/`sam2coef.c` 都在 ref 目录）
  对已知信号编码 → 两边解码对照，一次判死谁对；或做 640×640 算子矩阵比对。

## 6. 卡带文件系统与脚本容器（2026-10-17，新任务「语音 id ↔ 剧本情景」附带成果）

### 6a. patched 卡带布局（NLP_plus_patched.3ds，2 GB）

- NCSD 头在文件偏移 **0x100**（不在 0）；主程序 NCCH 在表项 `0x2E40400*0x200` 处但**已加密**。
- 全文件仅一个 IVFC 头 @**0x45E000**（RomFS 明文区），其 level1/2/3 描述与标准 3DS 不符
  （实测 level1 hash 区 @0x45E3A0 size 0x19680、level2/3 与官方布局对不上）——放弃标准解析。
- **文件项表**（明文，0x4776xx 附近起，扫 0x45E000–0x800000 共 2382 项）：
  `[u32 0xffffffff, u32 nameBytes, UTF16 名, u32 id, u32 flags, u32 offset, 0, u32 size, 0]`。
- 表里 offset 是虚拟地址；**明文内容 = offset + 0x496F80**（脚本/Siren14 系列实测一致；
  个别文件头另有 0x10–0x50 hash 块 → ±0x10 档）。
- 明文锚点：`Siren14voice.bin` 内容 @0x2C7B3BF0（唯一内容匹配）、dpb `{23,1,1,16}` @0x2C868B70
  （dpb 之后 64 B hash 即 spp 开头，与我们手里 `audio/Siren14Voice.spp` 前 64 B 一致）。
- 非 SBN2 的大文件（bcsar/bcstm/csidbin/spp/dpb/PAK 字体）都还在表里可提；
  `TextResource`（off=0x69E4, size=0x25D58）实为 **PAK/FNTB 字体块**，不是对话文本。

### 6b. SBN2/DBN2 脚本容器（解密）

- 依据 gdkchan/NLPTextTool（`repos/NLPTextTool/`，tarball master 8f19eb3）。
- **3 层 XOr 流，每层独立 Key**：`out[i] = data[i] ^ (KeyBytes[i%3] + Seed*(i//3))`，
  其中 `Key = LE u32 @magic+4`，`KeyBytes = Key 低 3 字节`，`Seed = Key 第 4 字节`；
  i 是**本层缓冲区内**位置（不是全文件偏移——初版因此解错）。
- SBN2 头：`SBN2`(4) + Key(4)；@8 BE u32 条目数；@0x10 每项 16 B：
  BE `hash0, hash1, off, len`（前两个 u32 疑为校验，NLPTextTool 的 DBN2 分支语义 `u0,u1,off,len` 同构）。
- 内层块再各自解一层：`SOB2`(4)+Key(4)+数据。**本作 535 个脚本的内层全部是 SOB2**（无 SDL2）。
- SOB2 = **Dream VM 字节码**（code.bin 里有 `Dream::ScriptProcess` 字符串 @0x27E9B7 VA；
  `SOB2`/`SDL2` 字面量池 @VA 0x1DD5BC 邻接 Shift-JIS 人名表指针 0x77914/0x779D0）。
  指令形态如 `32 01 00 XX`（push imm）、`87 02 …`、`83 01 00 XX`；块头 @0x0C=0x48（数据起点）、
  @0x24 起 28 B 疑 hash。**文本不在 SOB2 里**（UTF-8/Shift-JIS 日文均 0 命中）。

### 6c. 未决（下轮）

- 文本的真实存放处：候选 ① SOB2 引用的**外部字符串表**（TextResource 已排除=字体）；
  ② ExeFS/另一文件（`rom:/script/bin/script` 主脚本 @VA 0x6EEA35 字符串、`NLP_01/NLP_02`
  语言分支、`%s%s%s` 拼接 @0x6EEA50 邻域——加载器函数在 0x6EE830/0x6EE900/0x6EE9B0，
  无直接 ARM bl 调用者，可能经 vtable/内联）；③ kiwiz/nlpp-fmt 的 xml 是从**原版未打补丁**
  卡带 dump 的，或 SOB2 里 `32 01 00 XX` 的 XX 就是字符串 id（0x271f=10015 超出块长 → 指向池外）。
- 语音 id（如 55655=0xD947）在 t*.dbin2 中无 u32/u16 明文命中 → id 也在字符串/常量池间接引用，
  或由**台词序号**推导（NLPTextTool 的 SDL2.Dialogs 顺序 ↔ 语音序号）。
- 远期目标（TODO 5.2）：中文配音替换链 = 文本/语音对应关系 → TTS 音色克隆 → G.722.1 重编码
  → `.spp` 重打包 → 卡带回写（文件表 offset+0x496F80 定位、size 变更需重排或空洞填充）。

## 19

### 7. 脚本→语音映射（2026-10-17，02_static-re）：静态穷举结论 = 数据侧无解，走动态

目标：打通「脚本（SOB2 字节码）→ 语音 id（Siren14voice.bin 索引）」，产出 voice id → 场景/角色/前后台词 小批次表。

**静态穷举结果（全部已验证，均是否定）：**

1. **语音 id 不在 SOB2 明文**。用**正确解密**（`xor_stream(blk,key,0)[8:]`，magic+key 前 8B 是明文、XOR keystream 按绝对位置）解全部 535 文件后：
   - 13 个已知长语音 id（27480–27520、55653–55672）在全语料仅各出现 **8–16 次**（噪声级）；
   - `[10000,70000]` 区间共 1486487 次命中、50231 个不同值——均匀分布噪声；
   - 高频值 12800/13568/18432… 实为**操作码字节**（`32 01`=PUSH、`35 00`、`48 00`）被对齐 u16 误读。
2. **全部 38123 个内层块都是 SOB2**，0 个 SDL2 → NLPTextTool（只解 SDL2）对本作脚本无用。
3. **SOB2 体里无 UTF-16LE 日文对白**（最长 CJK 连续 run 仅 2–6 码元，纯巧合）；对白/文本不在脚本明文。
4. **`.sbin2` 是 PAK 归档**（a000.sbin2 含 2364 个 `PAK ` 子文件），非对白/语音表；dbin2/sbin2 是同名数据+PAK 配对，与语音映射无关。
5. **ROM 文件表 2381 项**无独立「voice map / msg table」；只有 dbin2、sbin2(PAK)、bcsar/bcstm（含 `STRM_VX_*_NN.bcstm` 按角色分库语音）、spp/dpb、FNTB 字体、TextResource(=字体)。

**SOB2 解密布局（实测，纠正旧笔记）：**
- 块 = `magic(4)+key(4)` **明文** + 密文。解密：`xor_stream(blk,key,0)[8:]`。
- 解密头 = `00000001 00000048`（count=1, code_off=0x48），`0x18=0x48`，`0x3C=0`，`0x40=0x48` 数据起点，之后 28B hash，代码 @0x48。
- 指令（已粗解）：`32 01 00 v`=PUSH(v 小整数)、`87 02 00 00`=CALL(2)、`01 00`/`00 XX` 其它操作。`83 01 00 NN`=CALL 子程 NN。

**SOB2 VM 解析链（code.bin，已定位）：**
- `0x1dd2d4` = SOB2/SDL2 块 loader：调 `0x1e0f2c` 读头、读 +9 处 type 字节、按 5 个角色类走各段加载（`0x6ee804`/`0x6ec684`）。
- `0x6ee890` = UTF-16LE→UTF-8 解码器（确认对白以 UTF-16LE 存于 SOB2 某段，但本作用密文/间接方式，未直接落盘明文）。
- `play_voice(ctx, id)` @`0x6d854c`，id 是槽号 0–15；真实大 id 在 16 槽 `slot[i].id`（`ctx+i*0x14+0x7c`）。`0x6d8280`/`0x6d870c` 是两个薄封装，无 `bl` 调用者、无字面量引用 → 经 vtable/函数指针**间接**触发（即脚本命令分发入口）。

**结论 / 下一步（动态）：**
- 数据侧已穷举无解：语音 id 由 SOB2 VM **运行时**解析。只能走 **headless azahar + GDB stub**：
  启动 `scripts/loveplus/run_emu.sh`（无 `--frames`=无限运行）或 MCP `start_emulator(gdb=true)`，
  用 `gdb-multiarch` 连 `127.0.0.1:24689`（target remote，halt on connect），
  在 `play_voice`（`0x6d854c`）或槽写入点 `0x742aec`（读 `slot[i].id`）下断，
  捕获每次播放的 (脚本文件, VM pc) → (slot, big_id)，回溯 SOB2 操作码如何压入 id。
- 模拟器已验证可启动运行（手动 `--frames 200` exit 0；之前 MCP 给 600 帧跑完即退，导致 live 端口 refused）。需注意 `--frames 0` 会立即退出。

## 20

语音索引链打通：conditionvoice_*.lmb → Siren14voice.bin → .spp


¶ 结论一句话

**voice_id 就是 `Siren14voice.bin` 的直接索引，无二级映射。** 中文配音链路的最后一环已闭合。

¶ 核心发现：conditionvoice_<0|1|2>.lmb 是语音索引表

卡带 PACK 归档里有 33 个 `.lmb`，其中 `conditionvoice_{0,1,2}.lmb` 是**条件语音索引表**。

- 这些文件是 **zlib 压缩流**（`78 9c` 开头）。注意：PACK 条目的 `Flags bit0` **没有**标记为压缩，必须自行判断 → 这是 PACK 提取器的一个坑。
- 解压后：`@0x00` u32 = 记录数（207），随后 **12 字节定长记录**：

```
struct LMBRecord {   // 12 B
    u32 flag;        // 高16位 = 条件组 id (0x0001, 0x0104, 0x0105 ... 严格递增)
                      // 低16位 = 组内序号    (1,2,3 ... 严格连续, 31/31 组全部验证通过)
    u32 _mid;        // 恒为 0
    u32 voice_id;    // Siren14voice.bin 直接索引; 同组内严格 +1 递增
};
// 相邻两条之间以 flag==0xFFFFFFFF 的记录作分隔
```

⚠️ 字段顺序踩坑：`voice_id` 是**第三个** u32，不是第二个。最初按 `(flag, voice_id)` 解出全 0，浪费了几轮。

### 「一段对话里多个音频索引是连续的」——已量化验证

用户提出的假设成立。实测 `conditionvoice_0.lmb`：

| 条件组 | 条数 | voice_id 区间 | 连续 |
|---|---|---|---|
| `0x0104` | 5 | `0x2a16–0x2a1a` | ✅ |
| `0x0105` | 5 | `0x2a1b–0x2a1f` | ✅ |
| `0x0106` | 3 | `0x2a20–0x2a22` | ✅ |
| `0x0107` | 3 | `0x2a23–0x2a25` | ✅ |
| `0x0108` | 3 | `0x2a26–0x2a28` | ✅ |
| `0x0109` | 3 | `0x685a–0x685c` | ✅ |

**同一条件下的一组语音，其 voice_id 是连号排列的** → 对中文配音极有利：替换一整段对话 = 替换一段连续 id 区间。

三个文件结构完全同构（均 207 条 / 31 组），仅 voice_id 基址不同：
- `_0` `0x2a16` 起 / `_1` `0x9821` 起 / `_2` `0x1069e` 起

¶ Siren14voice.bin 索引表验证

```
741240 B = 92655 条 × 8 B (offset u32, size u32)
offset 100% 单调递增 (92654/92654)
off+size 全部落在 .spp (687534906 B = 655.7 MiB) 内, 0 越界
size==0 仅 1 条 (尾哨兵)
```
实测 `conditionvoice` 的所有 voice_id **全部 in-range**（e.g. `0x2a16`→off=56661098 size=11454）。

¶ 角色 ↔ 脚本前缀（由 .spgdat 实证，非推测）

| spgdat | 脚本前缀 | 角色 |
|---|---|---|
| `Nene.spgdat` | `a00/a01/a50/a77/a99` | **宁宁 Nene** |
| `Rinko.spgdat` | `k00/k01/k50/k77/k99` | **凛子 Rinko** |
| `Manaka.spgdat` | `t00/t01/t50/t77/t99` | **爱花 Manaka** |
| — | `p*` | 主角 |
| 三方共有 | `t88` | 公共脚本 |

用户明确纠正：**Manaka = 爱花**（我此前臆造为"真奈加"，是错的）。三位角色只有这三个，不要编造第四个。

`.spgdat` 本身是精灵图区间表（`0→256→512→768` 步长 256），**与语音无关**，别再当语音索引。

¶ 文本数据：.mdc 邮件词典（含明文 UTF-8 日文）

- 全 ROM 扩展名统计（5683 PACK / 46521 文件）：`texi` 19681、`yaml` 3305、`mdl/smes/smat/bone` 各 2971、`arc` 2883、**`cdb` 1939**、**`rvbin` 25**（ReVoice 语音合成词典：`dtb`/`mdc`/`hmm`/`phn`）、**`lmb` 33**、**`twbdat` 12**（`EventTable_Stage*`）。
- `.mdc` 结构：`0x00 <len u8> <UTF-8 len 字节> 0x00`，记录间用 `0xffff` + `c1/c2/c4/c8/d0/e0/f0` 标志簇 + `00` 填充。该标志簇低字节为**一热编码的桶号**（`c1→c2→c4→c8→d0→e0`，单 bit 上移），第 4 字节 `ff/fe` 为配对奇偶位，尾部 `01/02` 为段号 → 印证多级连续索引结构。
- 解出真实台词量：`maildic_n` 598 / `maildic_m` 571 / `maildic_r` 552 条，`worddic_*` 各 31 条。

¶ 重要纠正：.texi 不是文本索引，是纹理描述

之前推断「`.texi` = 文本索引，文件名对应脚本」**是错的**。SERI 解开后参数名为
`w/h/mipmap/format/tex/type/ow/oh`，且 `type` 值 = `0x49584554` = ASCII **"TEXI"** → 纹理类型枚举。
`.texi` 是**纹理描述文件**，与文本无关。

（gdkchan 的 NLPUnpacker 原本不支持 `'TEXI'` 这个 +版扩展类型，所以解不出。）

¶ SERI 格式精确布局（gdkchan/NLPUnpacker Program.cs 权威）

```
@0x00 'SERI'
@0x04 u32  -> ValuesOffset = 该值 + 4     ← 注意：不加 BaseOffset
@0x08 u16  ParametersCount               ← 是 @0x08，不是 @0x0a（易错）
@0x0A  ParametersCount * { u16 NameOffset, u16 ValueOffset }
TypesTable @ ValuesOffset - ParametersCount   (每参数 1 字节类型码)
Values      @ ValuesOffset
类型码: 's'=str 'i'=int32 'f'=float 'b'=bool 'a'=array 'h'=nested-array
```
⚠️ **两个必踩的坑**：
1. 字符串（参数名和 's' 值）解析在 **PACK 容器的 StringTableOffset（ROM 缓冲）**里，不在 SERI 文件内。我最初拿文件自身缓冲去索引 → 参数名全空。
2. `ValuesOffset` 若再 `+4` 会算成 50 而非正确的 46+4=50… 实际要严格用 `@0x04 + 4`。

¶ PACK 容器布局（复刻自 gdkchan/NLPUnpacker）

```
@0x00 'PACK'
@0x04 u32 FileCount = 值>>16
@0x08 u32 StringPointersOffset (+Base)
@0x0C u32 StringTableOffset    (+Base)
@0x10 u32 DataOffset           (+Base)
@0x14 u32 DecompressedSectionLength
@0x18 u32 CompressedSectionLength
@0x1C u32 Padding
@0x20 + i*0x20 条目(0x20B): sig[4], unk0, DecompressedLength,
        DecompressedOffset(+Base), unk1, Flags(bit0=IsCompressed),
        CompressedLength, CompressedOffset(+Base)
文件名 = *(StringPointersOffset + i*4) → StringTableOffset + 偏移, NUL 结尾
```

¶ 工具与产物

- **`scripts/loveplus/02_static-re/nlp_voice.py`** —— 正式工具（已落盘），含上述全部结构体注释。
  子命令：`prefix` / `voicemap` / `verify` / `mdc`
- 产物落盘 `data/loveplus/nlp_plus/voice_map/`：
  - `conditionvoice_map.json` (30.3K) —— 条件组 → voice_id 映射
  - `mdc_lines.json` (98.5K) —— 各 `.mdc` 台词全文

¶ 尚未解决

1. **剧情对白主索引表尚未定位**。`conditionvoice_*` 是「条件语音」（满足游戏内条件才播的搭话/反馈），不等于剧情对白主线。`EventTable_Stage*.twbdat`（zlib，已解但未解析）是最可能的候选。
2. **脚本 SOB2 → voice_id 的引用方式未知**。已确认 SOB2 payload 是**带 tag 的对象序列化**而非裸 u32 数组（a000.dbin2 的 4 个 SOB2 块共 14600 字节，u32 值 ≤2000 的仅 5 个），所以静态按 u32 穷举语音 id 行不通——这是之前"静态穷举失败"的根本原因。
3. `keyword_*` 系列 lmb（2655 条）无 12B 定长结构，格式待解；`cdb`(1939)、`rvbin`(25) 未深入。
