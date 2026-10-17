# loveplus 脚本指南（SCRIPTS.md）

> 本目录所有脚本的用途、用法与依赖。通用约定见仓库根 `AGENTS.md` 的硬约束与 skill 地图；
> 无头模拟器环境与踩坑记录见 `memory/loveplus/headless_azahar.md`。

## 环境与通用约定

- Python 解释器：仓库根 `./.venv/bin/python`（依赖：Pillow、python-dotenv、mcp、numpy、capstone）。
- 本地路径一律经 `.env` 注入（`LOVEPLUS_REPO` / `AZAHAR_HEADLESS` / `NLP_PLUS_ROM` / …），
  脚本内 `from common_paths import *` 获取，**禁止硬编码机器绝对路径**。
- 无头模拟器由 `run_emu.sh` 启动（后台，PID 写 `/tmp/emu.pid`，控制端口 24777，
  日志 `/tmp/emu_live.log`）。**不要 `pkill -f azahar_headless`**（会误杀 shell 自身）。
- MCP 服务 `loveplus_mcp.py` 由 opencode 拉起；界面按空格可重启 MCP 以加载代码修改。

## 屏幕坐标体系（重要）

- dump 下屏图 `240x320`（竖屏），上屏 `240x400`。MCP `screenshot(which)`:
  `bottom` = 下屏；`all` = 上下拼接（上屏在前，**换算下屏坐标必须先减上屏高度 400**，
  建议直接用 `bottom` 避免换算错误）。
- 触摸命令坐标：原生 320x240 归一化 `(x,y)`，与 dump 的映射
  **touch_x = 1 − dump_y/320，touch_y = dump_x/240**（y 轴镜像）。
- **帧语义**：headless 每帧 = 一次 RunLoop，60fps → 1 帧 ≈ 16.67ms。
  NLP+ 菜单/键盘**必须长按 ≥60 帧**：用 MCP `drag_path(points=[[x,y]], hold_frames=[90..200])`
  实现"按住-停留-松开"；`tap`（~14 帧）对菜单无效。长按时长一律用帧数描述。
- 按钮命中判定：`touch` 按下 → 立即 `screenshot` → 看按钮是否变色 → `release`。

## 脚本一览

### 爱用 MCP 工具（优先，脚本次之）
简单前台任务（单次触摸/截图/状态）直接调 MCP：`tap/touch/release/drag_path/swipe/
screenshot(fmt="jpg", wait_frames=N)/pause/resume/buttons`。
复杂编排（状态机、循环监控）才写脚本。

### loveplus_mcp.py — MCP 服务
- opencode 经 `opencode.json` 拉起（`run_mcp.sh`）。工具详见文件 docstring。
- 截图默认存 JPEG（`fmt="jpg", quality=80`），`wait_frames=N` 截图前先等 N 帧推进画面。
- 修改本文件后需重启 MCP（opencode 界面按空格）才生效。

### emulator_ctl.py — 裸 TCP 控制客户端
```
./.venv/bin/python scripts/loveplus/emulator_ctl.py tap 0.5 0.5   # 原始命令直发
```
MCP 不可用时备用；`EmuControl` 类可 import。

### shot_ub.py — 双屏截图 + 触摸（推荐，输入操作首选）
一次「触摸 + 同时落盘上屏(u)/下屏(b)」，命名 `<step>/NN_u|b_描述.jpg`，id 自动递增。
走标准 MCP（`touch/screenshot`），不直连 `_send`。
```
# 只截当前双屏
./.venv/bin/python scripts/loveplus/shot_ub.py --step 09_profile --desc now
# 长按 90 帧(1.5s) 点某处，落盘 按下态 + 放开态 两组
./.venv/bin/python scripts/loveplus/shot_ub.py --step 09_profile --desc ok \
    --touch 0.297 0.5 --hold 90 --also-release
```
NLP+ 菜单/对话框必长按 ≥1s（hold_frames≥90）；输入文字时务必 u/b 成对落盘。

### shot_ocr.py — 双屏截图 + OCR
分别 dump u / b 两张图、**分别 OCR**（禁止 `all` 拼接，坐标会错位），可 `--find-u/--find-b`
直接给出文字的 touch 坐标。走标准 MCP（`screenshot/ocr`）。
```
./.venv/bin/python scripts/loveplus/shot_ocr.py --step 09_profile --desc now
./.venv/bin/python scripts/loveplus/shot_ocr.py --step 09_profile --desc cand \
    --find-b 削除 漢字 虚 --find-u 苗字
```

### type_input.py — 按 dump 坐标连续输字
把 dump 坐标换算 touch 后，按 `--seq` 连续多点（press/rel 双相成对落盘）。
```
./.venv/bin/python scripts/loveplus/type_input.py --step 09_profile --seq 61 79 63 107
```

### grid_detect.py — 交互网格检测/切块
对下屏截图做横/纵投影找行列边界，切成小格，**文件名带 dump 坐标**，
便于精确定位按钮/键盘键位（touch = (1−y/320, x/240)）：
```
# 默认取最新 /tmp/az_live_*_bottom.ppm
./.venv/bin/python scripts/loveplus/grid_detect.py --out /tmp/img_preview/cells
# 指定来源（须是 240x320 下屏；拼接图先裁 y400-720）与灵敏度
./.venv/bin/python scripts/loveplus/grid_detect.py --src shot.png --out /tmp/img_preview/cells --th 5 --gap 5
```
- 输出块名：`cell_r{行}_c{列}_x{起x}_y{起y}_w{宽}_h{高}.png`
- `--th` 提高可滤淡纹理；`--gap` 为最小格宽。检出后**用 read 看小格确认字键**，
  再按文件名坐标换算触摸点。
- 注意：候选列表/滚动区行距不均时会切碎，需人工按图微调（当前已知局限）。

### monitor_shots.py — 定时截图监控（配合 opencode bkgshell 后台跑）
```
./.venv/bin/python scripts/loveplus/monitor_shots.py   # 每5分钟截一张，3小时超时
```
长任务（如 extdata 创建 ~3 小时）挂 `background=true` 后台 shell，完成自动通知。

### dialog_monitor.py — 对话推进常驻监控（2026-10-16）
```
setsid ./.venv/bin/python scripts/loveplus/dialog_monitor.py --interval 5 \
    --log output/loveplus/monitor_ocr.log > /tmp/dialog_monitor.log 2>&1 < /dev/null &
```
每 interval 秒 dump u/b → **只保留最近一张** `/tmp/loveplus_shots/latest_{u,b}.png`
（不堆积文件）；u/b 双屏各自 OCR，整图无字时**裁剪对话框放大 3x 再 OCR 兜底**
（日志 Bz/Uz 行）；OCR 结果变化才追加写日志（带时间戳），连续 12 次无变化写 STABLE。
PID → /tmp/dialog_monitor.pid。用于 AUTO 对话推进/长过场时后台盯画面。

### monitor_create_text.py — 创建画面文本监控（旧版，pixel dark 计数）
按检测区暗像素判断「SDカードに追加データ…」是否仍在；注意背景动画噪声大，
已改为连续 2 次才判定。新任务优先用 monitor_shots.py（多模态看图更可靠）。

### run_emu.sh / run_mcp.sh — 启动器
- `run_emu.sh`：后台启动 azahar_headless（读 .env），日志 `/tmp/emu_live.log`。
- `run_mcp.sh`：MCP stdio 启动包装（opencode.json 引用）。
- `run_gui.sh`：启动 **GUI（Qt）版** azahar（同样带控制通道、同样读 .env）。
  默认导出 `LIBGL_ALWAYS_SOFTWARE=1` + `AZAHAR_GRAPHICS_API=OpenGL` —— 这是本机唯一
  「画面正确且不卡」的组合（GPU GL 会彩色噪点花屏、Vulkan 渲染器呈现时冻结；原因见下方
  「GPU / WSL 图形诊断」节与 `memory/others/diary/2026-10-17_02_static-re.md`）。pid 写 `/tmp/ui_gui.pid`。
  用法：`setsid bash scripts/loveplus/run_gui.sh > /tmp/ui_gui.log 2>&1 < /dev/null &`
- **同步模拟器用户数据（存档 / extdata，约 550M）**：本机 `sdmc` 全新时优先从远端拉现成的，
  省掉 ~3 小时的「追加データ」本机创建。**务必先停掉本机模拟器**：
  `rsync -a --partial --exclude 'log/' -e "ssh -o BatchMode=yes" \
     "${LOVEPLUS_REMOTE:-tx-new}:.local/share/azahar-emu/" "$HOME/.local/share/azahar-emu/"`
  （远端用户数据目录：`~/.local/share/azahar-emu/`；存档在 `sdmc/.../title/`，
  追加数据在 `sdmc/.../extdata/`；NAND 里没有本作存档。）

### 构建与同步（本机 UI 版 azahar，2026-10-17）

本机（WSL/Ubuntu 26.04）与远端 tx-new（Ubuntu 24.04）SONAME 不同（`libFLAC.so.14` vs `.12`、
pulse 17 vs 16），**远端编译出的二进制在本机跑不起来**，故本机需自行编译；远端继续用现成无头版。
以下脚本只读项目根 `.env`，不硬编码机器路径。

- `sync_from_txnew.sh` —— 从远端拉整个仓库（`--dry-run` 只看差异不传）。排除项分两类：
  ① 本机重新生成的构建产物（`tools/azahar/build_headless`、`tools/azahar/build_qt`、
  `tools/3dstool/build`、`tools/3dstool/bin/Release`、`.venv`）；
  ② **远端旧布局的整棵子树** `/azahar/`、`/3dstool/`——2026-10-17 本机把这两棵树移进了
  `tools/`（远端未动），不排除就会在根目录重新拉出一份来。
  代价要说清：`tools/azahar`、`tools/3dstool` 的源码**不再随 pull 更新**，改由各自 `.git` fetch。
  `tools/azahar/externals/*/build*` 是上游源码目录，**不可**排除。带 `--update` 保护本机
  新写的文件。**小时级传输必须 `setsid` 挂后台**（见 skill `loveplus-emu-ops`「后台任务按寿命选挂法」）。
- `aqt_mirror.ini` + `fetch_qt.sh` —— 预下载 Qt 6.10.3 到 `tools/azahar/build_qt/externals/qt`。
  镜像坑见 ini 顶部注释（要点：只给 `-b` 换镜像**无效**，元数据索引与校验和走 `trusted_mirrors`）。
- `build_azahar_qt.sh` —— configure（可选 `make -j`）UI 版。参数基线抄自
  `memory/loveplus/headless_azahar.md` 的实测无头配方，只翻 UI 相关开关
  （`ENABLE_QT=ON`/`ENABLE_VULKAN=ON`），Qt 走 `-DUSE_SYSTEM_QT=ON -DCMAKE_PREFIX_PATH=…/6.10.3/gcc_64`。
  编译器默认优先 `g++-13`：UI 目标 `citra_qt.cpp` 用了 `<format>`，libstdc++ 12 没有（GCC 13 才引入），
  本机系统只装了 g++-12，故需 `sudo apt install -y g++-13 gcc-13`。
  运行：**用 `run_gui.sh`**（它已带渲染器与 `LD_LIBRARY_PATH` 设置），或手动
  `LD_LIBRARY_PATH=tools/azahar/build_qt/externals/qt/6.10.3/gcc_64/lib \
   QT_QPA_PLATFORM=wayland LIBGL_ALWAYS_SOFTWARE=1 tools/azahar/build_qt/bin/Release/azahar`。
  **为什么要手动给库路径**：迁移到 `tools/` 后，二进制的 RUNPATH 仍钉着旧目录
  `/…/azahar/build_qt/externals/qt/…`（本机没装 `patchelf`，没改二进制），
  ELF 规范里 RUNPATH 的搜索顺序在 `LD_LIBRARY_PATH` 之后，故这样补得上。

### GPU / WSL 图形诊断（2026-10-17）

本机 WSL 的 Vulkan 走 Mesa **dzn（Dozen，Vulkan-on-D3D12）**。排查工具：

- `check_gpu.sh [秒数]` —— GPU 健康自检三步：`/dev/dxg` 存在 → `vulkaninfo` 能枚举设备 →
  `vkcube` 实跑 N 秒（默认 6）不出错。**注意：vkcube 测的是最脆的 WSI 路径**，
  单次成功不足以定论（实测同一台机器 6 秒过、20 秒挂），判断"是否可用"至少跑 20 秒 ×2 轮。
- `vk_submit_probe.c` —— 最小 Vulkan **提交**探针，不建窗口/不建 surface。
  编译运行：
  ```bash
  gcc -O1 -Itools/azahar/externals/vulkan-headers/include \
      -o /tmp/vk_submit_probe scripts/loveplus/vk_submit_probe.c -l:libvulkan.so.1
  /tmp/vk_submit_probe     # 选 Direct3D12 设备，3 次提交 + fence 等待，2 轮
  ```
  用途：**区分「dzn 核心坏了」与「只有呈现路径坏了」**。2026-10-17 实测：
  核心 6/6 次提交全部成功，而 `vkcube`（有窗口）3/3 失败 → 故障限于 WSI。

结论与对策（详见 `memory/others/diary/2026-10-17_02_static-re.md` 十二～十四节）：
- 社区同一报错（`dzn is not a conformant` + `D3D12: Removing Device.`）已定位为**应用侧非法 blit**
  （从 `TILING_LINEAR` 的 `B8G8R8A8_UNORM` 图做 `vkCmdBlitImage`，缺 `BLIT_SRC` 权限）→ D3D12 移除设备；
  上游仍 open（mesa#16041 / microsoft/wslg#1492）。
- **绕开办法：azahar 改用 OpenGL 渲染器**（走 Mesa 的 `d3d12_dri.so`，不经过 dzn 的 WSI）。
  需要带 `-DENABLE_OPENGL=ON` 重编；运行时可临时覆盖渲染器：
  `AZAHAR_GRAPHICS_API=OpenGL|Vulkan|Software`（`live_control.cpp` 实现，取值见 `common/settings.h`）。

### 调试类（Siren14 断点调试用，存档创建后再用）
`rsp_client.py`（GDB RSP 客户端库）、`rsp_probe.py` / `rsp_sample.py` / `rsp_bp_hit.py`
/ `rsp_verify.py`（断点/单步/采样）、`debug_siren.py`（主调试脚本）。
用法见 `output/loveplus/report/gdb_breakpoint_debugging.md`。

### R2 静态逆向辅助（2026-10-17）

反汇编对象固定为 `data/loveplus/nlp_plus/code_text_unpacked.bin`（**不是** 压缩体 `code.bin`），
加载参数 `-a arm -b 32 -m 0x00100000`，VA = 0x00100000 + 文件偏移。
完整地址表与结论见 `memory/loveplus/reverse_code_bin.md`。

- `find_code_xref.py <VA…>`：找「谁引用了某个数据地址」。先搜文件里存该 VA 的 4 字节（字面量池），
  再用 capstone 回溯窗口内的 `ldr rX,[pc,#imm]`。
  `--pool <池地址…>` 反向用法：直接给池地址，找加载该池的指令（本项目最常用）。
  ```bash
  ./.venv/bin/python scripts/loveplus/find_code_xref.py --pool 0x6d73dc 0x6d8294
  ```
- `arm_func_boundary.py <池地址…>`：字面量池紧跟函数末尾，据此向前找序言/返回，推出
  **拥有该池函数的起点**，供 r2 `af @ <起点>; pdf/pdc/pdd/pdg` 用。以 `b`/尾调用结束的函数会定位失败，需人工核对。
- `scan_arm_patterns.py`（2026-10-17 新增，**直接读二进制、不依赖 r2**，全仓扫一遍约几秒）：
  ```bash
  S="./.venv/bin/python scripts/loveplus/scan_arm_patterns.py"   # --bin 默认 code_text_unpacked.bin
  $S prologue --range 0x6d6f00-0x6da000      # 函数序幕 → 函数起点地图（含区间统计）
  $S bl --range 0x6d6f04-0x6d99e8 --external-only   # 该区间所有 bl 目标（看模块依赖谁）
  $S findbl --target 0x6d854c                # 反查谁调用某地址
  $S immoffs --vals 0x1b4,0x1b8 --range 0x6d6000-0x6da000   # 按 imm12 找字段读写
  $S vfp --window 0x1000 --top 20            # VFP 指令密度直方图（找浮点重的编解码/DSP）
  $S shift3 --shift 3                        # 找 `…, lsl #3` 索引寻址（定 stride）
  $S xrefin --range 0x76d000-0x76f000        # 谁 bl 进该区间（按 调用者窗→目标窗 聚合）
  $S ptrtab --range 0x76d000-0x76f000        # 池里存该区间地址的字 → 函数指针表（间接调用）
  ```
  已知边界：序幕扫描只匹配**含 lr 的 push**，不保存 lr 的叶子函数会漏（如 `0x742638`、`0x742668`）；
  判定「一段代码属于谁」的推荐顺序：`xrefin`（直接调用）→ `ptrtab`（间接调用）→ `prologue`（函数起点）。
  实例：0x76d000-0x76f000 无直接调用者、经 0x76bc34 的函数指针表进入 ⇒ 不属语音链（见
  `memory/loveplus/reverse_code_bin.md` §5f 勘误）。**「VFP 密度高」不能当归属证据**。
  大结构偏移（>0xfff）在池里**找不到数值**，要按 imm12 反查 `add`/`mov`（如 `#0x34000`→`0x90D`、`#0x34c00`→`0xBD3`、
  `mov rX,#0x1440`→`0xD51`），详见 `memory/loveplus/reverse_code_bin.md` §7。
### Siren14（G.722.1）解码核验与移植

`code.bin` 0x75c000-0x767000 是本作内置的 G.722.1 实现（结论与表地址见
`memory/loveplus/reverse_code_bin.md` §5d/§5e）。以下脚本从二进制**直读定点表**做核验。

- `siren14_framecheck.py codebook`：**判定性**核验——枚举两套码本（游戏的堆式树 + 按行长
  整除 vs FFmpeg 的值即下标 + 幂掩码）的全部比特路径，比较分量下标元组。7 类 100% 一致
  即证明「游戏流 = 标准 G.722.1 流」，FFmpeg 派生的表可直接复用。
- `siren14_framecheck.py bits`：逐帧解码统计（用位 vs 理论需求、帧尾剩余位数）。
  **注意「位消耗必须等于帧长」不是有效判据**（编码器不填满帧，实测留 0~21 bit）；
  该子命令只用于「解码不跑飞/越界」的回归检查。
  ```bash
  P="./.venv/bin/python scripts/loveplus/siren14_framecheck.py"
  $P codebook
  $P bits --voice 0 --frames 40 --convention both
  ```
- `siren14.py` / `siren_tables.py`：FFmpeg 派生移植（表已证等价，§5e）。**已参数化**：
  `siren14.configure(nregions=14|28)` 切档 —— 本作 = 28 region / 640 样本 / 32 kHz /
  5 bit（32 种）速率控制，`frame_size = 320·nregions/14`、`rate_control_bits = 4 + log2(nregions/14)`；
  另带 `GAME_ARP_MAX`、`AVAIL_CAP`、`STATS` 与「跳过已达 7 的区域」守卫（本作特有行为）。
  2026-10-17 按 ITU-T G.722.1 官参逐系数对照修正三处（见 memory §5e/§5f）：噪声用**单一平台值**
  `GAME_NOISE_TBL`（游戏表 0x8bf98c）且与编码系数**同单位**（×`SCALE_FACTOR`）；`dw` 伪随机状态
  **跨帧持久**（模块级 `_DW_STATE`，每条语音流起头调 `siren14.reset_dw()`）；噪声符号位按参考的
  **相邻 10 系数分块**（替代 FFmpeg 的偶奇交错）。修正后编码位与噪声位符号一致率均 100%。
- `siren_transform.py`：MLT 合成层（逆 MLT + 正弦窗 + 50% 重叠相加）。`Synthesizer` 逐帧解码；
  `synth_folded` 是 FFmpeg siren.c 式「折叠输出 + 旋转式重叠相加」的等价排布（用于交叉核对，
  与 `Synthesizer` 逐样本一致）；`out_scale_default(n) = sqrt(2/n)/32768` 是整体输出标量。
  直接运行 = 自检（分析核 vs 标准 MDCT 定义式、完美重构、窗正交、两排布一致）：
  ```bash
  ./.venv/bin/python scripts/loveplus/siren_transform.py
  ```
  相位约定**不做 (−1)^k 翻转**，判据见 `memory/loveplus/reverse_code_bin.md` §5g。
- `siren14_wav.py`：端到端驱动，`Siren14voice.bin` 索引 → `.spp` → 系数 → 16 bit WAV。
  ```bash
  P="./.venv/bin/python scripts/loveplus/siren14_wav.py"
  $P --voice 0 1 2                       # → data/loveplus/nlp_plus/decoded/voice_00000.wav
  $P --voice 0 --ref-check --probe       # 折叠·旋转排布逐样本校对 + 系数/相位诊断
  $P --voice <…> --no-wav --stats-csv /tmp/<agent>/stats.csv    # 批量统计（报告复核用）
  ```
  `--profile siren14`（默认）/`g7221-16k`；`--gain` 整体缩放；`--max-frames` 限量；
  `--stats-csv` 输出逐条 `voice,off,size,frames,samples,seconds,peak,rms,crest,disc,nz_median,raw_peak`。
- `verify_siren14_claims.py [报告路径]`：核验 `output/loveplus/report/siren14_decode.md` 里的
  可核验数字——左列取报告正文（正则抓取），右列**现场重算**（自检 + 重解 12 条抽样 + 谱相关 +
  索引勘验 + 读 328 条抽样产出表），逐条比对后落表
  `data/loveplus/nlp_plus/decoded/report_claims_check.csv`。退出码 1 = 有 MISMATCH。
  ```bash
  ./.venv/bin/python scripts/loveplus/verify_siren14_claims.py output/loveplus/report/siren14_decode.md
  ```
  口径提醒：谱一致性固定用 **28 个 500 Hz 带（0–14 kHz）**，不要再混用 32 带（0–16 kHz）的旧数字。

- `build_r2ghidra.sh [日志]`：编译安装 r2ghidra（`pdg`），**幂等可重跑**，自带多镜像备依赖、
  依赖补丁应用、mk 打桩防联网。装 r2dec（`pdd`）另见 `memory/others/diary/2026-10-17_02_static-re.md`。
  ```bash
  setsid nohup scripts/loveplus/build_r2ghidra.sh >/dev/null 2>&1 </dev/null &
  ```
  用法速查（出 C 首选 `pdg`）：
  ```bash
  r2 -q -a arm -b 32 -m 0x00100000 -e asm.bits=32 \
     -c 'ahb 32 @ 0x<addr>' -c 'af @ 0x<addr>' -c 's 0x<addr>' -c pdg code_text_unpacked.bin
  ```
  `pdc`（内置，会标注字符串）→ `pdd`（r2dec，ARM 条件执行会拉平）→ `pdg`（Ghidra，最准）。

### 卡带文件系统与脚本容器（2026-10-17，02_static-re）

> 目录 `scripts/loveplus/02_static-re/`。背景：NLP+ 的 patched 卡带不是标准 3DS RomFS 布局，
> 全部发现与锚点详见各脚本 docstring；上游参考 gdkchan/NLPTextTool 已归档在
> `repos/NLPTextTool/`（tarball master 8f19eb3，出处与 commit 见 repos/NLPTextTool/.upstream）。

- `romfs_extract.py`：从卡带文件表（明文 @0x45E000）扫出全部文件项并提取 SBN2 脚本
  （1015/2382 项成功）→ `data/loveplus/nlp_plus/script/`。
- `extract_scripts.py`：同表提取非脚本大文件（bcsar/bcstm/csidbin/spp/dpb 等）。
- `sbn2_parse.py`：SBN2/DBN2 容器解密（3 层 XOr 流：magic4+Key4 起头，`out[i]=data[i]^(key[i%3]+seed*(i//3))`），
  列出内层块（目前全是 SOB2 = Dream VM 字节码）。
  **尚未解**：SOB2 内文本/语音 id 引用形式；文本可能在别处（TextResource PAK 实为字体 FNTB 段）。

## 常见坑速查


| 坑 | 结论 |
| --- | --- |
| `tap` 点不动菜单 | NLP+ 需长按 ≥1s，用 `drag_path(hold_frames=[90+])` |
| 拼接图算下屏坐标错 | 用 `which="bottom"`；all 图下屏 y 需减 400 |
| MCP 改 `.py` 后怎么重连 | **无自动重连**（仅覆盖会话过期，不覆盖进程退出）；必须
  `/mcps` → 选中 `loveplus-emu` → **空格** toggle。详见 skill `loveplus-emu-ops`「MCP 进程与重连
  （`/mcps` + 空格）」一节。HTTP API `connect` 在 v2.0.22 走不通（location 锁 HOME）。 |
| `opencode mcp list` 显示 failed | 可能是真失败（进程被 kill 后不会自拉起），也可能快速探测误报；
  以 `frame()` 是否返回递增帧号为准 |
| extdata 创建像卡死 | 正常需 ~3 小时/550MB，勿凭短观察窗口提前下结论（已吃过 3 次亏） |
| 长任务后台化 | 会话内短任务用 `background=true`；**小时级、会跨会话重启的**必须 `setsid nohup … </dev/null &`，否则会话重启时随进程组一起被 SIGTERM（2026-10-17 实测）。详见 skill `loveplus-emu-ops` |
| 触摸无反应的对话框 | 先试触摸（**长按** ≥1s），再试 A 键（`buttons("1")` 按住若干帧再 `buttons_off`） |
| r2 静态分析 | 对 `code_text_unpacked.bin`（非压缩体）；`r2 -q -a arm -b 32 -m 0x00100000`。`Ps` 存项目会 `Cannot save project`，`anal.from/to`、`anal.in=range` 对 `aa` 无效（只出入口区 43 个函数）→ 改成只对目标函数 `af @ <起点>` |
| r2pm 装插件 | 首次必须 `r2pm -U`；r2dec 需 meson+ninja → `uv pip install meson ninja`（装进项目 venv）。**`env PATH=…:$PATH` 必须加引号**：PATH 里有 `/mnt/c/Program Files/…`，不加会被拆成两段报 `env: 'Files': Permission denied` |
| r2dec 装好了但 `r2 -L \| grep r2dec` 看不到 | 插件名是 `pdd`/`libcore_pdd.so`，`-L` 里不显 r2dec 字样；直接 `pdd` 能出结果即成功 |
| WSL 里 `vkcube` 挂、`vulkaninfo` 却能枚举设备 | 不矛盾：`vulkaninfo` 只查属性、不提交。跑 `vk_submit_probe.c` 判别——核心提交过=故障只在 **WSI**（呈现路径），不是 GPU 坏 |
| GUI（Vulkan 渲染器）卡在 ~94 帧、CPU 1000% | dzn 的 WSI 在 WSL 上不可靠（`D3D12: Removing Device.`）。用 `AZAHAR_GRAPHICS_API=OpenGL` 绕开，或改软件渲染器 |
| 怀疑"驱动不稳"前先查 | 残留进程可能一直占着 `/dev/dxg` 的 D3D12 分配，令后续分配全部失败：`for p in /proc/[0-9]*; do ls -l $p/fd 2>/dev/null | grep -q dxg && …; done`。`pause` 状态的无头实例 SIGTERM 不生效，要 `kill -9` |
