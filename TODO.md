# 项目任务板（TODO）

> **生成物，勿手改**：真源是 `multiagents/state/todo.json`，本文件由
> `python3 multiagents/agentctl.py todo export --write` 重新生成；改动请走脚本（对 JSON 加 `flock`）。
> 每条任务可被任一 agent 认领，认领是唯一的协调动作。
>
> ```bash
> python3 multiagents/agentctl.py todo list
> python3 multiagents/agentctl.py todo claim <主题号.子号> --owner <agent>
> python3 multiagents/agentctl.py todo done  1.3
> python3 multiagents/agentctl.py todo add "新任务" --topic 2
> python3 multiagents/agentctl.py todo note 1.1 "补充说明"
> python3 multiagents/agentctl.py todo export --write      # 重新生成本文件
> python3 multiagents/agentctl.py todo verify             # 检查本文件与真源是否漂移
> ```
>
> 格式：`- [ ] **主题号.子号** 描述 ｜ 认领: <agent|-> ｜ 状态: <todo|doing|blocked|paused|done> ｜ 更新: <时间>`；
> 紧跟其后的**缩进子行是备注**（用 `todo note` 维护）。协议见 `multiagents/README.md`。


**主题编号**（真源是 `todo.json` 的 `topics`；新增用 `todo topic add "名称"`；不复用、不回收）：

| 主题号 | 主题 | 主责 agent |
| --- | --- | --- |
| 1 | Siren14 语音解码（逆向 → 可复现的解码实现） | 02_static-re |
| 2 | 模拟器 / GUI（azahar 本机运行、控制通道、流程驱动） | 01_emu-gui |
| 3 | 本机环境与构建（WSL 图形、venv、Qt、路径隐私） | 01_emu-gui |
| 4 | 多 agent 并行规约 | 01_emu-gui |
| 5 | 远期：Gaming Agents（模拟器 agent 化框架） | — |
| 6 | 框架与开源 | 00_haruhi |
| 7 | 语音替换 / 中文配音（远期） | 02_static-re |
| 8 | multiagents 官网单页（web_doc/multiagents-site，独立 git） | 01_emu-gui |

---

## 1. Siren14 语音解码

细粒度清单（阶段 A–D、断点/采样率/校核）在 `output/loveplus/TODO_siren14.md`，owner `02_static-re`；
本板只放可认领的粗粒度项，两者不重复展开。

- [x] **1.1** 静态定位并还原 Siren14 解码函数 ｜ 认领: 02_static-re ｜ 状态: done ｜ 更新: 2026-10-17 17:21
  - 目标文件：`data/loveplus/nlp_plus/code_text_unpacked.bin`（解压后文本段，基址 `0x00100000`；
    **不要**用 `code.bin`，它是 LZSS 压缩的）。
  - 已有坐标：三件套字符串/指针数组 `0x8a829c`、RomFS 路径构造函数 `0x6d6f04`、加载基址 `0x00100000`。
    详见 `memory/loveplus/reverse_code_bin.md`。
  - 工具：r2 6.0.7 + `pdd`(r2dec) / `pdg`(r2ghidra)，用法见 `memory/others/diary/2026-10-17_02_static-re.md`。
  - 进度：已定位解码函数群——实现库 0x75c000-0x767000，帧解码入口 0x75e69c（含 4/5bit 速率控制与 MSB-first 位读器），envelope 0x75e0c0、categorize 0x75c3dc、decode_vector 0x75e2b8；解码器对象静态内嵌于驱动 obj+0x4000+i*0x800+0x98；变换层 0x76b67c 起（浮点）。'还原成 C' 尚余 0x75e0c0/0x75c3dc/0x75e2b8 全量 + 0x76b67c 下游。细节见 memory/loveplus/reverse_code_bin.md §5d。
- [x] **1.2** 判定采样率（16 kHz/320 样本 或 32 kHz/640 样本）与区域数（14） ｜ 认领: 02_static-re ｜ 状态: done ｜ 更新: 2026-10-17 16:31
  - 静态确认（2026-10-17，02_static-re）：.dpb={23,1,1,16} 经驱动 0x68b950 存成 码率=dpb[0]*800=18400bps、采样率参数=7000<<dpb[1]=14000、声道=1、位深=16；解码器 0x142568 只接受 7000/14000 两支 → 7000=14 region/320 样本(16kHz)，14000=28 region/640 样本(32kHz)。本作走 14000 → 32 kHz/640 样本/28 region。既有 siren14.py(FRAME_SIZE=320,14 region) 与 siren_ref.c(sample_rate=16000) 与此不符，应改 640/28/32000。依据：memory/loveplus/reverse_code_bin.md §5c 与 audio_siren14.md。
- [x] **1.3** 还原解码算法并写出可复现实现（Python；参考 FFmpeg `libavcodec/siren.c` 的 G.722.1/Siren14） ｜ 认领: 02_static-re ｜ 状态: done ｜ 更新: 2026-10-18 02:51
  - 勘误待办（01_emu-gui 转达 02_static-re）：memory/loveplus/audio_siren14.md 的「code.bin 静态线索」节（/Plus/ 0x3f8923 等）与 reverse_code_bin.md §1「压缩体内偏移非地址」的判定冲突。新 skill loveplus-siren14-re 已把该节标注作废；请确认真源该节是否删除或改写，以免再被引用。
  - 勘误已办（2026-10-18，02_static-re）：audio_siren14.md 该节已整体改写为「code.bin 静态线索（2026-10-18 更正：偏移已作废）」——正文加作废声明 + 正确的反汇编对象与地址映射，旧偏移仅留痕；memory verify --all 全绿。
- [x] **1.4** 用实现解 `.spp`（`Plus/Sound/Siren14Voice.spp`，656M）产出可听 WAV 并抽查 ｜ 认领: 02_static-re ｜ 状态: done ｜ 更新: 2026-10-17 18:02
- [x] **1.5** 结论写入 `memory/loveplus/audio_siren14.md` + 报告 `output/loveplus/report/siren14_decode.md` ｜ 认领: 02_static-re ｜ 状态: done ｜ 更新: 2026-10-17 18:15
  - 报告与核验脚本：output/loveplus/report/siren14_decode.md（304 行）+ scripts/loveplus/verify_siren14_claims.py，13 条核验全 OK
- [ ] **1.6** 暂缓：动态取真值 PCM（断在解码器出口 dump 一帧；输入 `46B × N` 与输出成对记录） ｜ 认领: 02_static-re ｜ 状态: paused
  - 停因：**用户要求逆向只做静态**；且动态路线本身有阻塞 —— azahar HLE DSP 的 semaphore IPC
    未实现（`GetSemaphore`/`ClearSemaphore` 为 `nullptr`），LLE DSP 缺 `dspfirm.cdc` 固件。
  - 备用路线（若解禁）：`DspHle::Tick()` 里 env 门控把混音帧直接落盘；离线 libg7221（源码 `/tmp/g7221src/`）。
- [ ] **1.7** 全量 92655 条语音 → 32 kbps/32 kHz/双声道 MP3（解码走官参 refdec） ｜ 认领: 03_audio-dec ｜ 状态: doing ｜ 更新: 2026-10-18 02:47
- [ ] **1.8** 官参 vs 自研 A/B 音质裁决：ref 更好；分析差异根因（已排除大小端/精度，指向整帧对齐） ｜ 认领: 03_audio-dec ｜ 状态: todo ｜ 更新: 2026-10-18 02:44

## 2. 模拟器 / GUI

- [ ] **2.1** 用 GUI 版跑通整条流程到 Main Menu ｜ 认领: 01_emu-gui ｜ 状态: doing ｜ 更新: 2026-10-17 15:45
  - 现状：实例停在「追加データ 新規作成 → 作成開始しますか？」确认框（未点）。
  - extdata + 存档已从 `tx-new` 同步（extdata 549.7MB / 33 files；savedata 82 文件、464K）。
  - 预期路径：标题 → Touch Start（长按）→ データ選択（DATA No.01）→ Main Menu。
  - 警告屏（違法配信…）用 A 键推过（`buttons("1")` 按住约 120 帧）—— 该页不在坐标表里，属本日新经验。
- [ ] **2.2** 排查「extdata 已完整但游戏仍提示新建追加データ」 ｜ 认领: 01_emu-gui ｜ 状态: todo
  - 线索：azahar SD extdata 路径大小写不一致 —— `GetExtSaveDataPath` 用大写 `{:08X}`，
    `GetExtDataPathFromId` 用小写 `{:08x}`（后者仅 Qt 前端调用）。
- [ ] **2.3** 继续新游戏流程到「创建玩家信息」画面（玩家名/生日/血型）——**到该画面停下向用户确认** ｜ 认领: 01_emu-gui ｜ 状态: todo
- [ ] **2.4** 把 MCP 自动化切到本机无头版跑一遍，确认 `--live-port` 控制通道在本机可用 ｜ 认领: 01_emu-gui ｜ 状态: todo
  - 本机产物：`tools/azahar/build_headless/bin/Release/azahar_headless`（`.env` 的 `AZAHAR_HEADLESS` 已指向它）。
- [ ] **2.5** 数据同步收尾 ｜ 认领: 01_emu-gui ｜ 状态: doing ｜ 更新: 2026-10-17 15:45
  - `data/loveplus/roms_patched`：远端 2.1G，本地未开始；`nlp_plus`：856M 传至约 550M。
  - 续传用 `scripts/loveplus/sync_from_txnew.sh`；**pull-only**（本地与远端有意分叉，不 push）；
    长任务须 `setsid nohup … </dev/null &` 挂后台，避免会话重启被杀。
- [ ] **2.6** 可选：软件 GL 的 CPU 占用约 500%，试 `QT_QPA_PLATFORM=x11` / `QT_OPENGL=desktop` 等变体省 CPU ｜ 认领: 01_emu-gui ｜ 状态: doing ｜ 更新: 2026-10-17 15:50
- [ ] **2.7** 可选（需用户在 Windows 侧操作）：`wsl --update` + 更新 Intel Arc 驱动，看能否修好 GPU 呈现路径 ｜ 认领: 01_emu-gui ｜ 状态: todo
  - 依据：映射进 WSL 的 `igd12umd64.dll` 时间戳 2024-04-23，偏旧；上游 `mesa#16041` 仍未修。
- [x] **2.8** 工具目录迁移：azahar/3dstool → tools/（构建树 2508 文件路径改写、Qt 二进制 LD_LIBRARY_PATH、同步排除远端旧布局、仓库引用 60+ 处） ｜ 认领: 01_emu-gui ｜ 状态: done ｜ 更新: 2026-10-17 16:16

## 3. 本机环境与构建

- [ ] **3.1** 路径隐私收尾 ｜ 认领: 01_emu-gui ｜ 状态: todo
  - `run_emu.sh` / `run_mcp.sh` / `fetch_*.sh` 改为 source `.env`（仍写死 `<repo>/...`）。
  - 删除一次性改写器 `scripts/loveplus/_scrub_paths.py`；验证所有脚本 import 正常。

## 4. 多 agent 并行规约

- [x] **4.1** 根 `TODO.md` 改造成任务板 + 三处旧 TODO 迁移归档 ｜ 认领: 01_emu-gui ｜ 状态: done ｜ 更新: 2026-10-17 16:22
  - 2026-10-17 二次改造：真源迁到 multiagents/state/todo.json，TODO.md 改为脚本导出（见日记 §8）
- [x] **4.2** 记忆归属登记 + 当日杂项记忆按 agent 隔离（`memory/others/<日期>.md` 已发生一次真实的双写覆盖） ｜ 认领: 01_emu-gui ｜ 状态: done ｜ 更新: 2026-10-17 16:46
  - 2026-10-17 三次改造（用户拍板）：记忆正文真源迁到 multiagents/state/memory/**/*.json，memory/**/*.md 变导出视图；写入一律 memory append|set|drop（长文 --file），勿手改视图（见日记 §9）
- [ ] **4.3** 补核 `clients.json` 中 claude-code / codex / codebuddy 的探测标记与会话 ID 获取方式（现为 `enabled=false`） ｜ 认领: 01_emu-gui ｜ 状态: todo
- [x] **4.4** `/tmp/r2nlp`（两 agent 共用）迁到 `/tmp/02_static-re/r2nlp`，原目录保留只读 ｜ 认领: 02_static-re ｜ 状态: done ｜ 更新: 2026-10-17 15:49

## 5. 远期

- [ ] **5.1** 开源 headless-citra + MCP 的模拟器 agent 化框架（暂定名 Gaming Agents） ｜ 认领: - ｜ 状态: todo
  - 愿景、输入/观测抽象待补项、Gaming Agents 排行榜设想等完整描述见
    `archive/loveplus/TODO_root_2026-10-17.md`「远期 TODO」节。
- [ ] **5.2** 探明「脚本→语音 id→槽→播放」全链路与 .spp/.dbin2 重打包路径，为中文配音（音色克隆 TTS → G.722.1 重编码 → 重打包回 ROM）铺路（远期，用户 2026-10-17 提出） ｜ 认领: 02_static-re ｜ 状态: todo ｜ 更新: 2026-10-18 02:55
  - 【2026-10-17 进展】静态链路已穷举闭环：① 解密纠偏——SOB2 正确 payload = xor_stream(blk,key,0)[8:]（keystream 按绝对位置，前8B明文不入密文），旧写法 xor_stream(blk[8:],key,0) 会错位假阳性；② 语音 id 不在 SOB2 明文（13 已知 id 全语料仅各 8-16 次命中=噪声，区间 148 万次均匀分布；高频 12800/13568/18432 实为操作码字节）；③ 38123 内层块全是 SOB2、0 SDL2→NLPTextTool 不可用；④ .sbin2 是 PAK 归档非对白表；⑤ ROM 无独立 voice-map。⑥ 运行时衔接已定位：play_voice@0x6d854c(slot 0-15)，真实大 id 在 slot[i].id(ctx+i*0x14+0x7c)，0x6d8280/0x6d870c 经 vtable 间接触发，SOB2 loader@0x1dd2d4。→ 结论：语音 id 由 SOB2 VM 运行时解析，数据侧无解。下一步须动态追踪：azahar 无头 + ARM gdb（缺，待 apt install gdb-multiarch）连 127.0.0.1:24689，在 play_voice/槽写入点下断抓 (脚本,VM pc)→大 id。用户本轮选「先暂停」。详见 reverse_code_bin.md §7 与 report 2026-10-17_2300_02_static-re.md。
  - 主线已切换（用户 2026-10-18 02:5x 拍板）：**当前做的是「游戏脚本文件本身的结构体」（SBN2/DBN2 容器 → SOB2/Dream VM 字节码），不是语音侧。**
    语音侧（voice_id ↔ 条件组）已于 2026-10-18 由 conditionvoice_*.lmb 打通，语音 id = Siren14voice.bin 直接索引，该支线已闭合。
    本条的「全链路」目标不变，但**下一块拼图是脚本结构体**：先把 SOB2 的段表/常量池/指令编码解出来，才能谈「脚本→语音 id」与重打包。
    结构体现状（详见 memory/loveplus/reverse_code_bin.md §6b/§7 与 §20）：容器 3 层 XOr 已解、535 个 dbin2 全部内层为 SOB2（0 个 SDL2）、
    指令形态仅粗解（`32 01 00 v`=PUSH、`87 02`=CALL、`83 01 00 NN`）、段头 @0x0C=0x48、@0x24 起 28B 疑 hash；**对白文本仍未落出明文**。
- [ ] **5.3** 还原 SOB2 段头/段表结构（code_off=0x48 之后各段语义、@0x24 起 28B 是否 hash） ｜ 认领: 02_static-re ｜ 状态: todo ｜ 更新: 2026-10-18 02:55
- [ ] **5.4** 解 SOB2 指令编码：定出 opcode 宽度/操作数格式，出 opcode 直方图与最频繁 20 条 ｜ 认领: 02_static-re ｜ 状态: todo ｜ 更新: 2026-10-18 02:55
- [ ] **5.5** 定位 SOB2 常量/字符串池：段内还是外部表（TextResource 已是字体，须另找） ｜ 认领: 02_static-re ｜ 状态: todo ｜ 更新: 2026-10-18 02:55
- [ ] **5.6** 从脚本里落出对白明文（UTF-16LE 经 0x6ee890 解码器），先拿 a000/a001 验证 ｜ 认领: 02_static-re ｜ 状态: todo ｜ 更新: 2026-10-18 02:55
- [ ] **5.7** 脚本→语音 id 引用：在结构体解出后回查（此前静态 u32 穷举已证无效） ｜ 认领: 02_static-re ｜ 状态: todo ｜ 更新: 2026-10-18 02:55
- [ ] **5.8** cross-check：脚本条目数/顺序与 voice_id 连号区间能否对齐（验「一段对话=连续 id」） ｜ 认领: 02_static-re ｜ 状态: todo ｜ 更新: 2026-10-18 02:55
- [ ] **5.9** 理清 SBN2 vs DBN2 容器差异与 535 个 dbin2 的分类统计 ｜ 认领: 02_static-re ｜ 状态: todo ｜ 更新: 2026-10-18 02:55

## 6. 框架与开源

- [ ] **6.1** 框架初次安装包：00_haruhi 全字段实例 + skills/ 真源与镜像 + README 与隐私边界 ｜ 认领: 00_haruhi ｜ 状态: doing ｜ 更新: 2026-10-17 18:15
  - 目标：别人克隆本仓库后，跑最少步骤就能被引导 agent 介绍清楚并初始化起来
  - 自检：验证统一锁
- [x] **6.2** 简报追加生成附录（个人待办 / 名下板项） ｜ 认领: 01_emu-gui ｜ 状态: done ｜ 更新: 2026-10-17 18:33
- [x] **6.3** 「主题级 todo 真源」取舍结论记档（DESIGN §17；暂不拆，附触发条件） ｜ 认领: 01_emu-gui ｜ 状态: done ｜ 更新: 2026-10-17 18:33
- [x] **6.4** 加锁的文件编辑并入 agentctl.py（原 editfile/filelock；三条真源写入统一同锁） ｜ 认领: 01_emu-gui ｜ 状态: done ｜ 更新: 2026-10-17 18:33
- [ ] **6.5** 在上一级目录建 multi_agents_templates 开源模板（去项目专有、可开箱即用，用户验收） ｜ 认领: 01_emu-gui ｜ 状态: doing ｜ 更新: 2026-10-17 18:52
  - 用户 2026-10-17 直接指派 01_emu-gui；topic 6 的 owner 是 00_haruhi，已在其 claims 之外（新目录在仓库外），无占用冲突。
  - 模板已建好并跑通：init ✓ exit 0 / sync_skills --check 0 / memory verify ✓ / todo verify ✓ / me 打印名册+三选项 exit 3；专有内容扫描 0 命中。
- [x] **6.6** first-run 增加「研究代码 → 仓库放哪」询问与 repos/ 目录约定（clone 或 symlink） ｜ 认领: 01_emu-gui ｜ 状态: done ｜ 更新: 2026-10-17 18:52
  - 落在三处：模板 skills/{first-run,repo-conventions} + 仓库本体同名 skill（已重镜像）+ v2 草案目录表；agentctl.py 的示例名与引导员提示一并改成从名册推导（不再写死 00_haruhi）。
- [x] **6.7** 读别人状态的口子：todo list 按 --owner/--topic/--state 过滤、读路径不打「落盘」提醒、新增只读 card 子命令 ｜ 认领: 01_emu-gui ｜ 状态: done ｜ 更新: 2026-10-17 19:09
- [x] **6.8** multiagents/.tests/：框架自检测试目录（stdlib unittest、只读）+ 文档接线（SCRIPTS.md / README / skill） ｜ 认领: 01_emu-gui ｜ 状态: done ｜ 更新: 2026-10-17 19:13
- [x] **6.9** rename 子命令 + 开源模板引导员换成 00_yuki（長門有希）：开场白三语（标志句只直译）、「目录+能力」自我介绍、语言选项框 ｜ 认领: 01_emu-gui ｜ 状态: done ｜ 更新: 2026-10-17 19:20
- [x] **6.10** 框架输出多语言（资源字符串 i18n）：i18n.py + locales/ + --lang/lang 子命令 + i18n_extract 维护工具；同步到开源模板 ｜ 认领: 01_emu-gui ｜ 状态: done ｜ 更新: 2026-10-17 19:45
- [x] **6.11** 根 AGENTS.md 换成 v2（规程下沉到 9 个 skill；413 → 113 行）+ 全仓悬空指针修正 + 模板同步 ｜ 认领: 01_emu-gui ｜ 状态: done ｜ 更新: 2026-10-17 19:58
- [x] **6.12** 同步 rigorous-writing 文风 skill：远端 tx-new → skills/ 真源 + 三处镜像 + report-writing 门禁闭环（style_lint.py） ｜ 认领: 01_emu-gui ｜ 状态: done ｜ 更新: 2026-10-17 20:14
- [x] **6.13** 模板验收通过后复位出厂状态（清 .env / state/locks / __pycache__；00_yuki 档 client/sessions/todo 复位）+ 补同步 rigorous-writing（真源 7 skill + 三镜像 + AGENTS.md 地图） ｜ 认领: 01_emu-gui ｜ 状态: done ｜ 更新: 2026-10-17 20:27
- [x] **6.14** onboard 初次安装进度功能：真源 state/first_run.json + onboard status/step/reset/finish + me 进度提示（继续/重新开始）+ i18n 28 条 + .tests 22 项；同步模板 ｜ 认领: 01_emu-gui ｜ 状态: done ｜ 更新: 2026-10-17 20:42
- [x] **6.15** 脚本归档规约：scripts/<主题>/<agent>/ 落点 + 每个有作用脚本进 SCRIPTS.md 索引（弃用先归档）+ src/<主题>/<项目>/ 收大型代码；两侧同步 ｜ 认领: 01_emu-gui ｜ 状态: done ｜ 更新: 2026-10-17 20:54
- [x] **6.16** 引导员兼任本地 contributor 身份：focus/claims(multiagents/)/skills(rigorous-writing)/display/history + 记忆档 §05；模板 00_yuki 与仓库 00_haruhi 同款 ｜ 认领: 01_emu-gui ｜ 状态: done ｜ 更新: 2026-10-17 21:06
- [x] **6.17** quick-report：目录改名+命令改名（report→quick-report 别名兼容）+落点 output/quick-report/，三处同步 ｜ 认领: 01_emu-gui ｜ 状态: done ｜ 更新: 2026-10-17 23:20

## 7. 语音替换 / 中文配音（远期）


## 8. multiagents 官网单页（web_doc/multiagents-site，独立 git）


---

## 已完成（归档，不再逐条跟踪）

2026-10-16/17 的环境与显示问题已闭环，原始清单见 `archive/loveplus/TODO_root_2026-10-17.md`：
本地 venv 用 uv/CPython 3.12 重建、`.env` 适配本机、Qt 6.10.3 预下载（aliyun 镜像）、
UI 版 azahar 编译通过（GCC 13 + 1815 目标）、GUI 实机运行验证、Qt 前端 live 控制通道、
本机 WSL 图形问题定位与解法（软件 GL + OpenGL 渲染器，封装为 `scripts/loveplus/run_gui.sh`）、
extdata 创建与从 `tx-new` 拉取、仓库根清理。

历史清单归档：

| 原文件 | 归档位置 |
| --- | --- |
| 根 `TODO.md`（2026-10-17 版） | `archive/loveplus/TODO_root_2026-10-17.md` |
| `archive/loveplus/TODO_memory_2026-10-17.md`（最初的 10 步目标，已被主题 1 取代） | `archive/loveplus/TODO_memory_2026-10-17.md` |
| `archive/loveplus/TODO_build_2026-10-17.md`（构建/环境清单，开放项已折进主题 1、3） | `archive/loveplus/TODO_build_2026-10-17.md` |
| `output/loveplus/TODO_siren14.md` | **留在原地**（owner `02_static-re`，主题 1 的细项展开处） |

已归档的原始文件不是垃圾：它们记录了当时的完整细节与踩坑，需要时按上表回查。
