# Gaming Agents：MCP 与 Headless Emu（Gaming Sandbox）设计报告

> 日期：2026-10-15
> 状态：设计讨论稿（本会话不涉及逆向，主线创建流程后台运行中）
> 关联：TODO.md 远期项「Gaming Agents」；原型代码 `scripts/loveplus/loveplus_mcp.py`、
> `emulator_ctl.py`、`tools/azahar/src/citra_headless/headless_main.cpp`

## 0. 背景与动机

本项目在逆向 New Love Plus+ 语音格式过程中，搭建了一套可用的无头模拟器 agent 化原型：

- **citra_headless**（azahar fork 最小前端）：软件渲染、无 GUI 依赖、可长时间运行；
- **TCP 控制通道**（ControlServerLoop）：tap/touch/move/release/buttons/dump/frame/pause/resume；
- **GDB stub**：断点/单步/内存读写（调试与内省）；
- **MCP 服务**（`loveplus_mcp.py`）：把上述能力暴露为标准 MCP 工具，agent 可直接调用。

实践验证了核心假设：**LLM agent 可以通过 MCP 工具面完整操控一台 3DS 模拟器**
（我们用纯 MCP 调用走通了从启动、菜单、确认框到 SD 卡创建的完整流程）。

## 1. 核心创新点：难度-能力匹配

现代 3A 游戏需要数十小时长程规划、复杂开放世界导航与实时 3D 决策，远超当前模型能力；
而老游戏（8/16-bit 至 DS/PSP 时代）**机制简单、规则显式、状态空间小、单局流程短**，
恰好落在当前模型"够得着"的区间——能真的玩明白、能产生有效训练信号。

**老游戏是当前模型游戏能力的最佳训练场与评测场**，随模型能力增长再逐步升级游戏年代。

## 2. 问题形状：四个正交维度

| 维度 | 问题 | 现状（原型） |
|---|---|---|
| 观测 Observation | agent 看到什么 | L0 裸帧截图（PPM→PNG） |
| 动作 Action | agent 能做什么 | 触摸 + 8 个 HID 数字键 |
| 状态 State | 快照/恢复/检查点 | 无（仅游戏自身存档） |
| 协议 Protocol | 对话语言 | MCP 工具（request/response） |

## 3. 观测层：分层观测设计

裸帧流直接给多模态模型成本高且信噪比低。设计为四层，按需取用：

| 层级 | 内容 | 用途 |
|---|---|---|
| L0 原始帧 | 整屏 PNG/JPEG | 训练数据、视频回放 |
| L1 感知压缩 | 变化检测 + ROI（对话框/菜单/血条） | agent 实时决策 |
| L2 结构化 | OCR/模板匹配出的文本与状态值 | 低成本高频轮询 |
| L3 内省 | RAM 快照、符号值（HP/位置/旗标） | ground truth、奖励计算 |

设计原则：

- **L2/L3 是 opt-in 作弊层**：评测只开 L0/L1（纯感知）；训练感知可用 L3 做 distillation
  （教模型从画面推断状态）。
- **音频**：老游戏大量信息在音频（语音/BGM 提示/音效）。v1 先丢弃，v2 作为独立模态
  加入（本项目 Siren14 逆向正是音频感知的典型场景）。
- **帧同步是硬要求**：观测必须严格对应动作边界（"该按键后第 N 帧的画面"），
  需要 `step(frames)` 原语。pause/resume + dump 已验证此路可行。

## 4. 动作层：两级动作空间 + 自动锚定

两种极端各有缺陷：

- 原始输入（touch(x,y)）：通用但 agent 每局都要重新"找按钮"（本项目坐标校准踩坑数日）；
- 语义动作（click_button("start")）：高效但语义来源仍需感知，且逐游戏适配。

**方案：两级动作 + 锚点缓存**

```
原始层:  input.touch(x, y) / input.button("A", hold=1.2) / input.stick(x, y)
语义层:  ui.locate("はじめから") -> anchor   # 一次性校准，存入游戏 profile
         ui.click(anchor) / ui.navigate(...)
```

**锚点即资产**：每个游戏首次游玩时做一次 UI 校准（可由模型看图自行完成），
按钮坐标/对话框布局存为游戏 profile，后续所有会话复用。玩得越多 sandbox
对游戏理解越深——知识可积累。

**模拟量输入接口原则：归一化 + 时长语义**：`stick(0.7, -0.3, hold_ms=500)`；
压感键统一 `pressure(0.0-1.0)`。

### 输入抽象待补全清单（当前仅触摸 + 8 HID 键）

- 模拟量轴：摇杆 x/y、扳机压力、3DS 圆摇杆 / 新3DS C-Stick、PS1/2 双摇杆
- 压力感应：PS2 十二键压感、Wii 平衡板
- 体感/指针：Wii 光标 + 六轴、PS Move、Sixaxis
- 外设：光枪、轨迹球、方向盘、跳舞毯
- 键位映射层：agent 统一语义（"左摇杆右推到底"）→ 各模拟器原生输入

### 观测/通用能力待补全清单（输入之外）

- 音频输出流（BGM/语音/音效）
- 存档管理：save state 快照/回滚、导出导入
- 内存/cheat 读取：RAM 快照、符号值查询（感知不可见状态）
- 帧级确定性：固定种子重放、逐帧步进（数据可复现）
- 数据管道：操作-画面-状态轨迹结构化落盘（jsonl + 视频流），训练直读

## 5. 状态层：sandbox 的灵魂

与"游戏录像回放"工具的本质区别所在，也是对训练数据质量影响最大的设计：

1. **Save state 快照**：全内存 + 时间点。agent 大胆探索——死了就回滚，试错成本
   为零；敢尝试低置信度动作，轨迹多样性质变。
2. **确定性重放**：固定种子 + 输入轨迹 = 完全可复现。排行榜公平性的根基；
   同一轨迹可多次评估。
3. **检查点树**：游戏流程 = 树（节点 = save state + 到达路径），agent 探索 = 树遍历。
   完成度/覆盖率/探索策略可量化。

实现选择：v1 用模拟器原生 savestate（快、粗粒度），v2 对重点模拟器做帧级内存快照。

## 6. 协议层：MCP 的边界

游戏是有状态的实时循环，MCP 是 request/response 工具协议。三种模式：

| 模式 | 描述 | 适合 |
|---|---|---|
| A 纯工具 | agent 每步 observe→act→observe | 回合制/慢节奏（老 RPG/AVG，约 80% 老游戏） |
| B 环境 | reset/step/observe Gym 风格 session | 训练批量 rollout |
| C 事件流 | sandbox 推送观测变化 | 实时游戏（ACT/格斗），需 SSE（MCP 不支持推送） |

**v1 决策：模式 A + 游戏类型分层**；ACT 类留 v2。

### MCP 工具面草案

```
observe.screen(layers: [L0|L1|L2|L3], format)
observe.audio(duration)
act.input.raw(...) / act.input.semantic(...)
state.save(label) / state.load(label) / state.tree()
emu.step(frames) / emu.speed(x) / emu.reset(seed)
game.profile() / game.achievements()
```

## 7. 多模拟器抽象：最大工程量

每个模拟器的 savestate / 输入注入 / 帧步进 API 均不同。两条路线：

- **libretro 统一路**：RetroArch headless + MCP frontend，一套代码覆盖全部 libretro
  core（GBA/SNES/PS1/N64…）。缺点：部分 core 质量差、深度 hack 受限。
- **逐模拟器 native 桥**：如本项目 hack citra_headless。质量高、工程量大。

**务实路线：libretro 打底（广度）+ 2-3 个重点模拟器 native 桥（深度）**。
3DS 用现成 citra_headless；PS1 选 duckstock…（duckstation，savestate/step 支持好）；
其余走 libretro。

## 8. 数据管道（训练视角）

轨迹自描述格式：

```jsonl
{"t": 1234, "obs_hash": "...", "obs_ref": "frames/001234.jpg",
 "action": {"type": "button", "key": "A", "hold": 0.2},
 "state_ref": "states/ck_0007.save", "tags": ["dialog", "choice"]}
```

画面增量存 jpg、状态引用检查点 ID、事件标签由 L2 自动打。同一份轨迹可重放出
SFT 轨迹、DPO 对比对、reward model 标注等多种训练视角。

## 9. Gaming Agents 排行榜（评测基准）

用固定种子 + 确定性重放 + 标准化游戏集（不同年代/类型/难度：RPG 解谜、ACT 反应、
AVG 推理、模拟经营）做统一评测，模型同规则同观测自主游玩至通关，按以下指标
生成公开排行榜：

- 通关率 / 用时 / 操作效率（无效操作率）
- 关键决策点表现（BOSS 战、解谜、资源管理）
- 长程任务能力（数小时流程的记忆与规划）

定位：**SWE-bench 之于代码 = Gaming Agents 之于游戏能力**。

### 待拍板问题

1. **评测游戏集**：每个年代 3-5 个、类型分散；版权可分发或用 **homebrew 替代**
   （可能是版权雷区的解法）。
2. **作弊层边界**：纯感知评测（禁 L3）与辅助感知评测（开 L3）**分榜**。
3. **进程模型**：每游戏一模拟器进程（冷启动 1-2 分钟贵）vs **常驻池化**
   （评测吞吐关键，倾向池化）。

## 10. 原型 → 产品的差距清单

| 模块 | 原型现状 | 产品化需要 |
|---|---|---|
| 输入 | 触摸 + 8 HID 键 | 全输入族 + 锚点缓存 + 映射层 |
| 观测 | L0 截图落盘 | 分层观测 API + 帧同步 step |
| 状态 | 无 | savestate 管理 + 检查点树 |
| 协议 | MCP 工具面（16 工具） | 分层观测 + session +（v2）事件流 |
| 模拟器 | 仅 citra_headless | libretro 打底 + 重点 native 桥 |
| 数据 | 无落盘 | jsonl 轨迹 + 检查点引用 + 标签 |
| 评测 | 无 | 游戏集 + 榜单 + 公平性基建（种子/重放） |

## 11. 落地路径建议

1. **Phase 1（现已完成）**：单游戏可用原型（NLP+ 全流程 MCP 操控）。
2. **Phase 2**：观测分层 + step 原语 + savestate 管理（仍在 citra_headless 单模拟器内），
   跑通一个老 RPG 的自主游玩 demo。
3. **Phase 3**：抽象层剥离（emu-agnostic 接口），接入 libretro，扩 3-5 个平台。
4. **Phase 4**：Gaming Agents 评测基建 + 公开榜单。
