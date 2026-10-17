# 多 Agent 并行工作流（设计草案 v1，待审）

> 状态：**已落地**（2026-10-17）。正式协议见 `multiagents/README.md`；本文件保留为设计草案与决策记录。
> 文中记忆路径按**当时的旧布局**书写（脚本已按新布局机械改写，语义以 `README.md` 为准）。
> 目的：让**多个 agent 会话**（可能来自**不同客户端**）在同一工作区并行工作时不撞车、可交接、可追溯。
> 起草：2026-10-17

## 0. 为什么需要（实测事故，不是假想）

当前工作区**已经**有两个 agent 并行，且已经互相干扰：

| 事故 | 证据 |
| --- | --- |
| 重复劳动：两边都在拆 `0x006bccd4` | 02_static-re 把它标为「优先」；01_emu-gui 也去拆了同一个函数 |
| 共用临时目录 | `/tmp/r2nlp/`（02 在 14:34 建的 r2 项目 `nlpcode`），01 在 15:01 又往同一目录写文件 |
| 共写同一记忆档 | `memory/loveplus/reverse_code_bin.md` 双方都在改，无归属标记 |
| TODO 散落 4 处 | 根 `TODO.md`、`archive/loveplus/TODO_memory_2026-10-17.md`、`TODO_build.md`、`output/loveplus/TODO_siren14.md` |
| 压缩后失忆 | 上下文压缩后 agent 不知道自己是谁、做到哪、占用了什么 |

已确认的两个会话（同目录 `<repo>`）：

| 代号 | 会话 ID | 标题 | 线 |
| --- | --- | --- | --- |
| `01_emu-gui` | `ses_ebc583d2cffenwDwrfKU51CWUS` | SSH到tx-new拉取loveplus项目 | 模拟器 / GUI |
| `02_static-re` | `ses_eb7ac4333ffehinPc10g5X0tpr` | OpenAI API 与 Anthropic API 区别 | 静态逆向（Siren14） |

**且客户端可能不止一个**：本机实测已装 `~/.codebuddy`（CodeBuddy CN）、`~/.codex`（Codex）、opencode。
规约因此必须是 **客户端无关**的——不能把任何单一客户端的私有变量或接口当作唯一依据。

## 1. 设计原则

1. **客户端无关**：客户端只作元数据（`client` 字段，默认 `opencode`）；协议靠「仓库内文件 + 通用脚本 + 用户确认」成立。
2. **一 agent 一文件，只写自己的**：并发写冲突从结构上消除；全局状态 = 读全部文件。
3. **单一权威**：项目任务在一处（根 `TODO.md`），agent 细节在一处（自己的 json），记忆在一处（`memory/`）。
4. **身份必须经名册确认**：上下文有显式声明就照用；否则**必须读 `multiagents/` 名册让用户选**，
   且选项里**永远含「新增一个 agent」**。脚本只提供匹配建议，不替用户决定。
5. **最小依赖**：只用 `python3` 标准库 + 仓库内脚本，不引入守护进程/外部服务。

## 2. 目录布局

```
multiagents/
├── README.md            # 协议 + **名册索引**（谁是谁、状态、占用了什么）——判定身份先读它
├── DESIGN.md            # 本草案（批准后并入 README.md）
├── 01_emu-gui.json      # 命名规则：自增序号_role；一 agent 一档
└── 02_static-re.json
multiagents/
├── SCRIPTS.md           # 脚本索引（AGENTS.md 硬性要求）
├── clients.json         # 客户端探测规则表（env 标记 → client 名，可扩展）
└── agentctl.py          # roster / attach / register / todo / memory-index
memory/MEMORY.md         # 记忆索引（共享，仿 scripts/loveplus/SCRIPTS.md）
TODO.md                  # 项目级任务板（可认领）
```

**命名规则**：`<两位自增序号>_<role>`，如 `01_emu-gui`、`02_static-re`、`03_report`。
序号按**首次登记顺序**递增，不复用、不回收；`role` 变更需同步文件名与 json 内 `name`。

## 3. 客户端探测（`client` 字段怎么来的）

`agentctl.py` 按序探测环境标记；**未命中记为 `unknown`，协议仍可用**（靠用户确认）。

| 序 | client | 探测依据 | 能否拿到会话 ID |
| --- | --- | --- | --- |
| 1 | `opencode` | `OPENCODE=1` 或 `OPENCODE_SESSION_ID` | ✅ `OPENCODE_SESSION_ID`（**已实测**：与我的会话一一对应） |
| 2 | `claude-code` | `CLAUDECODE=1`、`CLAUDE_CODE_ENTRYPOINT` | ⏳ 待核 |
| 3 | `codex` | `CODEX_HOME` 等 | ⏳ 可读 `~/.codex/sessions/YYYY/MM/*.jsonl`（待核） |
| 4 | `codebuddy` | `CODEBUDDY_*` | ⏳ 可读 `~/.codebuddy/logs/<date>/<proj>__<hash>.log`（待核） |
| 5 | 其它/未知 | — | ❌ 由用户确认 |

规则表放 `multiagents/clients.json`，不写死在代码里；探测结果**只作匹配建议**。

## 4. 身份协议（会话启动 / 上下文压缩后，第一步必做）

**只有两条来源，优先级从高到低**：

1. **上下文里有显式声明 → 照用。** 包括：用户开场说了「你是 02_static-re」、会话标题写明、或本会话此前已声明过。
2. **没有显式声明 → 必须读 `multiagents/README.md` 名册（或该目录下的 `*.json`），让用户从名册里选。**
   不得自行认领。**选项里永远包含「新增一个 agent」**。

脚本 `agentctl.py` 是助手而非决策者：探测客户端、打印名册、给**匹配建议**与排序，供用户参考。

```
$ agentctl.py roster                 # 也可直接读 multiagents/README.md
client : opencode                   (env:OPENCODE=1, session=ses_ebc583d2cffe…)
名册（2）:
  01_emu-gui    active [15:14] 模拟器/GUI 线       claims: -
  02_static-re  active [15:09] 静态逆向(Siren14)   claims: /tmp/02_static-re, data/…/r2/**
建议  : 01_emu-gui（本会话 session_id 与该档一致）── 仅建议，等用户拍板
```

**给用户的选项固定三类**：

- 名册里的某个 agent；
- **新增一个 agent**（名字按 `<序号>_<role>` 规则生成，role 可自取或采纳脚本推荐）；
- **暂不登记**（仅限看代码/问问题这类无副作用的工作）。

**用户直接点名时**（如「你是 static」）不做盲匹配：脚本模糊比对名册，**列出匹配项或提示新建**，
由用户确认——因为名字可能只是近似，也可能根本不存在。

选定后登记并声明：

```
$ agentctl.py attach --name 02_static-re    # 幂等：登记当前 client + 会话，刷新 updated
```

然后**显式声明一句**「我是 `02_static-re`（角色 static-re）」，读回该档的 `focus` / `board` / `todo` / `claims`，再动手。

**压缩后**：同样先查上下文有没有声明；没有就重走第 2 步（读名册 → 用户选）。压缩不会清 shell 环境，
客户端与会话 ID 仍可探测，但**探测结果只是线索，不能替代用户的选择**。

## 5. agent 档案（`multiagents/<name>.json`）

```jsonc
{
  "name": "02_static-re",
  "display": "静态逆向（Siren14 解码链）",
  "role": "static-re",
  "client": "opencode",                 // 当前客户端，默认 opencode
  "status": "active",                   // active | paused | blocked | done
  "updated": "2026-10-17T15:20:00+08:00",

  "focus": "定位并还原 Siren14 解码函数",
  "sessions": [                          // 同角色可挂多会话
    { "client": "opencode", "session_id": "ses_eb7ac4333ffe…",
      "title": "OpenAI API 与 Anthropic API 区别",
      "attached_at": "…", "last_seen": "…", "state": "active" }
  ],

  "board": ["1.3", "1.7"],               // 认领的项目级 todo（§6）
  "todo": [                              // 可选：仅本 agent 的细项；也可不含大 todo
    { "id": "b1", "task": "读 0x006bccd4 的位分配表引用", "state": "doing", "updated": "…" }
  ],

  "claims": {                            // 动手前先声明；别人先扫这里
    "files": ["data/loveplus/nlp_plus/r2/**"],
    "tmp": "/tmp/02_static-re",
    "resources": ["r2"]
  },
  "memory": [                            // 记忆归属的**权威记录**就在这里
    { "path": "memory/loveplus/reverse_code_bin.md", "role": "maintainer" },
    { "path": "memory/loveplus/audio_siren14.md", "role": "contributor" }
  ],
  "jobs": [ { "name": "r2ghidra 编译", "pid": 790886,
              "log": "/tmp/02_static-re/r2ghidra_build.log", "started": "…" } ],
  "artifacts": ["/tmp/02_static-re/", "output/loveplus/report/siren14_decode.md"],
  "handoff": "给 01_emu-gui：data/loveplus/nlp_plus/r2/ 归我，别动",
  "history": [ { "t": "2026-10-17T15:00", "e": "开始拆 0x006bccd4" } ]
}
```

- **必填**：`name` `role` `client` `status` `updated` `focus`
- **其余可选**：宁可缺，不要编——json 只记**能被验证**的东西。

## 6. 项目级任务板与认领

**编号规则**：`<主题号>.<子号>`。主题号在 `TODO.md` 顶部登记（1=Siren14、2=模拟器/GUI、3=本机环境与构建、4=多 agent 规约…）；
子号在每个主题内自增。例：

```markdown
# 项目任务板

主题编号：1=Siren14 解码 ｜ 2=模拟器/GUI ｜ 3=本机环境与构建 ｜ 4=多 agent 规约

## 1. Siren14 解码
- [ ] **1.3** 读 0x006bccd4 判断是否解码器 ｜ 认领: 02_static-re ｜ 状态: doing ｜ 更新: 2026-10-17 15:20
- [ ] **1.4** 补齐 0x6d7814 / 0x6d8294 函数起点 ｜ 认领: - ｜ 状态: todo
```

操作走脚本（`fcntl.flock` 加锁，读-改-写原子）：

```bash
agentctl.py todo list                     # 看全部
agentctl.py todo claim 1.3                # 认领（已被认领则拒绝并提示）
agentctl.py todo done  1.3
agentctl.py todo release 1.3
```

分工原则（回答「json 与 TODO 谁是权威」）：

- **项目级 TODO = 任务池**，每个任务**可被不同 agent 认领**；认领是唯一的协调动作。
- **agent json = 我的详细工作状态**：可以包含大 todo 的细分，也可以只引用 `board: ["1.3"]`；可引用项目级 memory。
- **禁止双写**：同一条任务的不同粒度只在一个地方展开，另一处只放 id / 指针。

主题级长清单（如 `output/loveplus/TODO_siren14.md`）保留，但登记 `owner`，细项折进 owner 的 json 或拆成项目板条目。

## 7. 记忆（共享 + 索引）

- `memory/` 是**共有**的：任何 agent 可读、可写。
- **归属的权威记录在各 agent json 的 `memory[]` 里**（`maintainer` / `contributor`），不在 memory 文件本身。
- memory 文件头那行是**给人看的**，非强制、可省略；写法示例：

  ```markdown
  > 读改过: 01_emu-gui, 02_static-re（维护） ｜ 更新: 2026-10-17 15:20 ｜ 状态: canonical
  ```

- **新建 `memory/MEMORY.md`**：仿 `scripts/loveplus/SCRIPTS.md` 的索引风格，列全部记忆档（路径 · 参与 agent · 更新时间 · 状态 · 一句话）。
  - 由 `agentctl.py memory-index` 汇总各 json 的 `memory[]` + 扫文件头生成；人工可再编辑。
  - 目前 `memory/MEMORY.md` **不存在**，而 AGENTS.md 已在引用它——本次一并补上。

## 8. 冲突与资源规约

1. **临时目录隔离**：一律 `/tmp/<agent>/…`（今天是 `/tmp/r2nlp/` 被双方共用，才有事故）。
2. **长任务登记**：编译 / rsync / 长时间 r2 分析写进 `jobs[]`（pid、日志、预计时长），避免别人重复起或误杀。
3. **破坏性操作**（删/覆盖他人产出）：必须先在对方 json 的 `handoff` 留言 + 项目板登记，再做。
4. **让路顺序**：先声明者优先；抢占要有理由并写进 `history`。

## 9. AGENTS.md 拟增条文（草稿原文，插在「核心原则」之后）

```markdown
### 多 agent 并行（强制：会话启动 / 上下文压缩后第一步）

1. **身份只有两个来源**：
   - 上下文里已有**显式声明**（用户说过、会话标题写明、或本会话此前声明过）→ 照用，随即可开工；
   - **没有显式声明** → 必须读取 `multiagents/README.md` 名册（或该目录下的 `*.json`），
     让用户**从名册里选**自己是哪一个；不得自行认领。
     选项须包含：名册某项 / **新增一个 agent** / **暂不登记**。
     用户口头点名时不盲目采用：模糊比对名册后**列出匹配项或提示新建**，由用户确认。
2. 用户选定后跑 `multiagents/agentctl.py attach --name <name>` 登记当前客户端与会话，
   并**显式声明**一句「我是 `<name>`（角色 X）」，读回该档的 focus / board / todo / claims 再动手。
3. 认领项目任务用 `agentctl.py todo claim <主题号.子号>`；占用文件/目录/资源写进自己 json 的 `claims`，
   动手前先扫其它 agent 的 `claims`；临时目录一律 `/tmp/<agent>/`。
4. **客户端无关**：`client` 字段记录当前客户端（默认 opencode）；不得依赖任何单一客户端的私有能力。
5. 记忆（`memory/`）共有；记忆归属的权威记录写在自己 json 的 `memory[]`，索引见 `memory/MEMORY.md`。
6. **名册不写在本文件**（会漂移）。本文件只规定「去哪儿看、怎么定」，名册唯一权威是 `multiagents/`。
```

## 10. 迁移计划（批准后执行）

| 现状 | 去向 |
| --- | --- |
| 根 `TODO.md` | 改成项目任务板：加主题编号表 + `主题号.子号` id + 认领字段 |
| `archive/loveplus/TODO_memory_2026-10-17.md` | 拆：项目级 → 根板；细项 → owner 的 json |
| `archive/loveplus/TODO_build_2026-10-17.md` | 同上（构建/环境线，归 01_emu-gui） |
| `output/loveplus/TODO_siren14.md` | 登记 `owner: 02_static-re`，长清单折进 `02_static-re.json` 或拆成项目板条目 |
| `memory/loveplus/reverse_code_bin.md` | 归属写进 `02_static-re.json` 的 `memory[]`；文件头可选加一行人类可读标注 |
| `memory/loveplus/diary/2026-10-17_01_emu-gui.md` | 按日日志被双方共写 → 拆成各自段落或分文件 |
| `/tmp/r2nlp`（共用） | 数据迁到 `/tmp/02_static-re/r2nlp`，原目录保留只读 |
| 建立两档 | `multiagents/01_emu-gui.json`、`multiagents/02_static-re.json`（内容见 §5，已填真实 session id） |

## 11. 已定事项（本轮拍板）

| 项 | 决定 |
| --- | --- |
| 命名 | 自增序号 + `_` + role，如 `01_emu-gui` / `02_static-re` |
| 任务 id | `<主题号>.<子号>`，如 `1.3`；主题号在 `TODO.md` 顶部登记 |
| 认领并发 | `fcntl.flock` 加锁，读-改-写原子 |
| 记忆归属 | 权威在 json 的 `memory[]`；memory 文件头那行面向人类、非强制 |
| 点名入口 | 不做盲 `--force`；必须经名册选择，永远含「新增 agent」选项，点名走模糊匹配确认 |
| 名册位置 | 只在 `multiagents/`；AGENTS.md 只写规则 |

## 12. 变更记录：存储真源 JSON 化（2026-10-17 下午，用户提议并拍板）

原设计（§6 / §7）把 Markdown 当真源：任务板是根 `TODO.md`，记忆正文是 `memory/**/*.md`。
用户提议「实际保存都用脚本操作 JSON，Markdown 只是脚本导出的人类可读视图」，拍板**全部 JSON 化**，
理由是**写操作天生带锁**。落地如下：

| 域 | 真源（机器写，`flock`） | 视图（生成物，勿手改） |
| --- | --- | --- |
| agent 档案 | `multiagents/<name>.json`（原本如此） | —（无 md 视图） |
| 项目任务板 | `multiagents/state/todo.json`（+ `todo.footer.md` 存板尾手写散文） | 根 `TODO.md` |
| 记忆正文 | `multiagents/state/memory/<项目>/<档>.json` | `memory/<项目>/<档>.md` |
| 记忆索引 | 由上述真源 + 各 json 的 `memory[]` 渲染 | `memory/MEMORY.md` |

配套规则（已写进 `AGENTS.md` / `README.md` / `SCRIPTS.md`）：

- **所有机器写的真源 json 收在 `multiagents/state/` 下**（用户要求 json 全部落在 `multiagents/` 内）。
- 视图由脚本渲染；改数据一律走 `agentctl.py todo …` / `memory …`。`todo verify` 与
  `memory verify --all` 做漂移检测（逐字节比对，漂移则非零退出）。
- **记忆按「节」存**：一档 = 由 `## 标题` 切出的有序 section 列表（首个 `##` 之前是 `preamble`）。
  追加以节为单位：两个 agent 同写一档时各写各的节，落盘串行化，互不覆盖。
- 正文传参仿 `git commit`：`--text` ≈ `-m`，`--file` ≈ `-F`（`--file -` 读 stdin）；长文用 `--file`。
- 旧手写 md 已一次性 `memory import` 进真源（10 档、非空行差异 0），原件归档
  `archive/loveplus/memory_md_2026-10-17/` 与 `archive/loveplus/TODO_board_md_2026-10-17.md`。
- §7 中「memory 文件头那行（`> 读改过: …`）给人看、非强制」的约定**作废**：文件头改由导出器
  写一行 HTML 注释，标明真源路径与改法。

## 13. 变更记录：身份获取与进展简报改由脚本做（2026-10-17 傍晚，用户要求）

用户的痛点有二：多 agent 并行时**难以跟踪每个 agent 在做什么**；以及**「确定我是谁」这一步本可交给脚本**
（原先写在 AGENTS.md 里，靠 agent 手工读名册 → 让用户选 → `attach` → 读回 `focus` / `board` / `claims`）。
据此新增子命令，**规约文本仍以 AGENTS.md 为准，脚本只把动作落地**：

| 子命令 | 作用 | 退出码 |
| --- | --- | --- |
| `me [--name X]` | 获取当前 agent：会话匹配 → **自动登记**（等价 attach）→ 打印身份卡（含可直接复述的「我是 `X`」声明句、任务板分组、个人清单、`claims`、交接、下一步）；未识别则打印名册 + 三个选项与对应命令，**不自行认领** | 0 命中 / 2 名册无此人 / **3 需用户选** |
| `new <角色> [--display] [--focus] [--no-tmp]` | 上面「新增一个 agent」那一支：建档 + 登记 + 建 `/tmp/<agent>/` + 身份卡 | 同 `me` |
| `report [--text\|--file] [--list]` | 用户问「在做什么 / 进展」时，把 agent 给的正文落盘到 `multiagents/report/<日期时间>_<agent>.md` | 0 / 1 正文空 / 2 名册无此人 |

设计取舍（用户明确要求）：

- **`report` 不从 json 推导内容**：脚本只做「定文件名 + 原样落盘」，正文由 agent 自己写；
  亦**不做文本统计**（不数行数/字符数），不注入表头，避免脚本变复杂。
- 同分钟内重复生成自动加 `-2`、`-3`，不覆盖旧简报。
- `me --name X` **点名优先于会话匹配**（否则会把用户点名的档回落成会话已登记的档，实测踩过）。
- `roster`（只读列名册）与 `attach` / `register` 保留，作为 `me` / `new` 内部的原始动作。
- AGENTS.md 暂不改（用户要求先不动）：待并入的两处——「多 agent 并行」第 1–2 条改为
  「第一步跑 `agentctl.py me`」，以及简报命令的位置；改前以 `README.md` §1 为准。

## 14. 变更记录：档案扩展（`skills[]` / `spawn` / `task`）与规程下沉到 skill（2026-10-17 夜间，用户要求）

用户先问「opencode 支持 agent 自主调用 skill 吗」，随后要求「AGENTS.md 更简单，其余通过 skill 注入，skill 加入 agent json」，
再要求「量化/分析防错等非 multiagent 内容拆成更细的 skill，记忆里的游戏攻略/手册也沉淀成 skill」。据此分两半落地。

**一半是脚本（`agentctl.py`）：**

| 新增 | 作用 |
| --- | --- |
| `spawn <角色> [--skill S] [--focus] [--handoff] [--no-tmp]` | 生成**另一个** agent：建档 + 注入 `skills` + 建 `/tmp/<名>/` + 摘要，**不**登记当前会话（`new --no-attach` 等价）。它自己的客户端与会话等它跑 `me` 时登记 |
| `task list\|add\|doing\|done\|drop\|set\|rm` | **个人**待办清单，写档案 `todo[]`（任务号 `a1`/`a2`…，`--board 2.1` 只做关联标注）。与项目任务板 `todo` 分家：板子可被认领，私人清单不可 |
| 档案 `skills[]`、`created_by` | 该 agent 该用的 skill ID（`me` 打印「技能」一行）；生成的档记 `created_by`。与 opencode 自身的 skill 权限（`agents.<id>.permissions` 里 `action: skill`，作用于 opencode agent 档案）**不是一回事** |
| 身份卡新增两行 | 「收到交接」（扫别人 `handoff` 里提到我的）、「由谁生成」（`created_by`） |

**另一半是文档层级（依据 opencode V2 skill 机制实测）：** skill 放 `.opencode/skills/<id>/SKILL.md`（**ID = 目录名**），
每个模型步只把 `ID + name + description` 广告给模型，正文**按需注入**（agent 自己调 `skill` 工具，或用户在提示里写 `@skill-id`）。
所以把「常驻注入」的 AGENTS.md 压薄、细节改放 skill，是拿**触发相关性**换**常驻体积**：

- 8 个 skill（`multiagent-workflow` / `repo-conventions` / `plotting-standards` / `quant-analysis-rules` /
  `report-writing` / `loveplus-emu-ops` / `loveplus-nlpplus-guide` / `loveplus-siren14-re`），由 4 个 subagent 并行产出；
- 后两个由 memory 沉淀（`touch_coords_nlpplus.md` → 攻略/流程/坐标，坐标节**由脚本 `sync_coords.py` 从记忆真源生成**，
  避免 skill 与 memory 双份维护漂移；`reverse_code_bin.md` / `audio_siren14.md` → 逆向操作版，长表只给真源指针）；
- 根 `AGENTS.md` 暂仍未改（用户未拍板），候选稿与逐节映射在 `archive/others/AGENTS_proposal_v2_2026-10-17.md` 与其 `_notes.md`
  （非空行 360 → 48）。

**已知缺口**：`AGENTS.md` 三处引用的 `.opencode/skills/rigorous-writing/SKILL.md` 与 `scripts/style_lint.py` 本机不存在，
文风门禁暂时跑不了；规范内容已由 `report-writing` 承接，替代做法是人工对照其禁用清单自查。

## 15. 变更记录：框架开源准备（CLI 中立 skill 真源、`00_haruhi` 引导员、`init` 自检）（2026-10-17 夜，用户要求）

用户说这套多 agent 框架「以后可能要开源」，要求：① 加一个 `00_haruhi` agent；② 默认内容里放「初次安装」引导，
让别人的 agent 从 GitHub 克隆后向用户介绍自己并初始化项目；③ 引导 agent 的档案要覆盖 agent 档案的**全部特性**，
且每个特性引用的文件都要有实例。落地分三块：

| 块 | 落地 | 为什么这样 |
| --- | --- | --- |
| skill 真源 | 真源移到 CLI 中立的 `skills/<id>/`；`multiagents/sync_skills.py` 镜像到 `.opencode/skills/`、`.claude/skills/`、`.agents/skills/`（幂等，`--check` 查漂移，镜像的 `SKILL.md` 在 frontmatter 后盖「生成物」戳） | skill 目录因 CLI 而异（用户指出），真源只能一份，否则同一份规程在多处各抄 |
| 引导员 | `multiagents/00_haruhi.json`（角色 `haruhi`，`skills` = `first-run` / `multiagent-workflow` / `repo-conventions`），随框架发布（`created_by: framework`），`sessions` 留空等用户认领；`me` 的未识别分支会提示「新克隆先按 `first-run` 引导」 | 新用户上来先有个默认身份；`me` 退出码 3 的分支正好是它的入口 |
| 初始化 | `agentctl.py init [--fix]`：逐档核对 `claims` / `memory[]` / `skills[]` / `artifacts[]` / `jobs[].log` / `todo[]` / `board[]` / `sessions[]` 引用的实例是否都在 | 把「每个特性都有实例」变成可检查的不变量；首次跑就抓出 `skills/first-run` 未建、以及 `claims.files` 里的 glob 认领被误判两处 |

`00_haruhi` 的档案是全字段实例：`claims.files` 指向它管的真实文件、`memory[]` 指向记忆档 `others/first_run`、
`jobs[].log` 指向自检日志、`artifacts[]` 指向引导产物、个人清单 `todo[]` 是初始化步骤、`board[]` 认领板子 6.1。
字段与实例的对照表写在 `memory/others/first_run.md`。

## 16. 变更记录：加锁的文件编辑并入 `agentctl.py`（2026-10-17 夜，用户要求）

先按用户当时的要求做了独立工具 `editfile.py` + `filelock.py`（加锁、原子写、编辑留痕、`who` 查 claims），
用户随即要求**合并进 `agentctl.py`**。合并顺带处理了两个隐患：

1. **单一入口**：`agentctl.py file edit|write|append|read|locks|who` 取代 `editfile.py`，`multiagents/` 回到
   「一个 py 工具 + 一个镜像脚本」的形态，与文件头「唯一工具」的自我描述一致。
2. **同一把锁**：原先 `mutate_agent` / `mutate_board` / `mutate_memory` 各自 flock 在**目标文件自身**上，
   而文件编辑锁在**旁挂锁文件**上——同一文件两把锁等于没有锁（`file edit` 改 agent 档案与 `json set`
   可以同时进）。现在三条真源写入改用同一套 `locked()`（锁键 = 仓库内相对路径），实测 holder 持锁时
   `json set` 等了 1.94s 才落盘。
3. 附带好处：全部写入改成「临时文件 + `os.replace`」，读方看不到写了一半的内容；`multiagents/filelock.py`
   这个名字原先与 `requirements.txt` 里钉的 PyPI 包 `filelock==4.2.0` **撞名**，合并后消失。

## 17. 变更记录：简报追加生成附录；为什么不为主题级 todo 再开一份真源（2026-10-17 夜，用户要求）

用户提出「agent 汇报可读时带上它的个人待办」，同时讨论要不要再加一层「主题级 todo 真源」。

**做的**：`report` 落盘时追加一节生成附录（个人待办 / 名下板项 / claims 占用），读真源现算，`--no-appendix` 可关。
原先 report 的原则是「脚本只定文件名 + 原样落盘，不读 json」，这一节是**有意的例外**：附录带「生成物」戳、与
agent 正文用 `---` 分隔，不冒充 agent 的叙述；换来的是简报自带「手上还压着什么」。

**没做的**：为「主题级清单」新开真源（`state/todo/<主题>.json`）。三条理由：

1. 板子本身已是两层（`topics[]` + 编号 `items[]`），「某主题的清单」就是按 `topic` 过滤的视图；两份真源等于同一件事两处写，
   `todo verify` 管不到第二份的一致性（与本项目「真源只留一份」的教训同源）。
2. 认领的最小单位是 item，item 已带 `topic`——细粒度项直接入板，认领 / 留痕 / `done` / `init` 校验全部复用。
3. 拆分的唯一实收益是「主题 owner 独占写权、少点锁竞争」，本仓库规模（几十项、写操作按分钟计）不值这套复杂度。

**将来真要拆的触发条件**：某主题 `items` > 50，或该主题并行 agent > 2 个。届时把 `items[]` 按主题分文件、根视图改为
遍历合并，并把 `todo verify` 扩成「逐文件 + 聚合」双层校验。

**同类待定项**：主题级人类可读清单走哪条路。现状是手写叙述体（`output/loveplus/TODO_siren14.md`，在 topic 的 `prose`
里点名，见 topic 1），叙述内容包括阶段划分、阻塞原因、校核基准；若改成 `todo export --topic N --write` 生成视图，
这些叙述就没了着落。两条路只能选一条（同一路径混着来会重演「手改被覆盖」），目前维持手写。

**后续（同日稍晚）**：用户随后提出过具体拆法——`root_todo.json` 加 `<id>_<主题>_todo.json`（id 前缀便于互相引用），
即上面「没做的」那条的命名方案。听完「单一真源 + 视图」的取舍后，用户确认**维持单份真源**（项目板 + 各 agent
`todo[]`），per-topic 真源未实施；可选的生成视图（`todo export --topic N --write`，配 item 的 `level` 折叠）同样
**未实施**，等触发条件满足再议。将来若真要做，「视图另起文件名、不覆盖手写叙述体」这条约束不变。

## 18. 变更记录：读别人状态的口子（`card` / 板子过滤 / 读路径不打写提醒）（2026-10-17 夜，用户要求）

用户问「`agentctl.py` 支不支持读其他 agent 的工作内容（todo 列表 / 记忆）」。逐条实测下来读的口子基本都有
（`roster` 概览、`json get <字段> --name X`、`task list --name X`、`todo list`、`memory show <档>`、
`report --name X`），但有三处不顺手，一并改掉：

1. **`todo list --owner <agent>` 原本被静默忽略**。`--owner` 只对 `add`/`claim`/`topic add` 生效，
   而 `task list --name X` 的输出偏偏提示「用 `todo list --owner X`」——提示指向一个不生效的参数。
   现在 `list` 真按 `--owner` 过滤，并加了 `--topic N`、`--state <状态>`（三者可组合；过滤后为空不是错误，退出码仍 0）。
2. **读别人的档不再打「确认无误再落盘」**。`resolve_agent(name, write=…)` 新增 `write` 开关：
   `json get` / `task list` 这类只读路径不再打印（读操作不落盘，那句话是写给写路径的）；
   `json set|add|remove|…`、`task add|…`、`report` 仍然打印。
3. **新增只读子命令 `card [<agent>]`**：一屏给出某 agent 的整档摘要（focus / 私人清单 / 名下板项 /
   认领占用 / 维护的记忆档 / `skills[]` / 作业 / 最近三条 `history[]`）。不登记会话、不改任何档。

**为什么要专门加 `card`**：`me --name X` 会把当前会话**登记**到 X（等价 `attach`）——名字像查询，
实际是写操作，想读别人的进度时它是错的工具。`card` 是它的只读对应物；`cmd_me` 带 `--name` 时也补一行
stderr 提示这一点。

**只读面的全貌**（同步写进 `SCRIPTS.md` 的用法块与「常见坑」表）：`card <agent>`｜
`todo list --owner <agent> [--topic N] [--state S]`｜`task list --name <agent>`｜
`json get <字段> --name <agent>`｜`memory show <档>`。记忆**没有** agent 私有区（共享），
归属看 `memory/MEMORY.md` 的「参与 agent」列，或反向 `json get memory --name <agent>`。

## 19. 变更记录：`rename` 子命令（改 agent 名字要动真源）（2026-10-17 夜，用户要求）

用户要求把开源模板的默认引导员从 `00_guide` 改成 `00_yuki`。改一个 agent 的名字**不只是 `mv` 档案**：
任务板的 `owner`、记忆各节的归属 `agent`、别人的 `created_by`、`claims.tmp` 与 `jobs[].log` 里的
`/tmp/<agent>` 都按名字引用；手改必漏，而且漏了 `init` 也查不出来（它只核对字段实例，不核对
「板上认领人是否还在名册里」）。于是补了 `agentctl.py rename <旧> <新>`：

- **自动改（机器写的真源）**：档文件名、`name`、`claims.tmp` 与 `jobs[].log` 里的 `/tmp/<旧名>`、
  任务板的 `items[].owner` 与 `topics[].owner`、记忆各节 `sections[].agent`（含 `archived[].dropped_by`）、
  其他档里 `created_by == 旧名` 的引用；最后重导 `TODO.md` / 记忆视图 / `memory/MEMORY.md`。
  档案里追加一行 `history[]`，写明谁在什么时候改的。`/tmp/<旧名>` 目录**连内容一起搬**到 `/tmp/<新名>`
  （两边都在时不覆盖，交人工合并——首次实测就漏了这一步：字段指到新路径、日志还留在旧目录，`init` 当场报出来）。
- **不自动改（叙述文字）**：README、skill、记忆正文、简报里出现的旧名。理由：叙述里的旧名常常
  **不该改**（本人历史、别人的引用、归档），机器替换会改坏语义；脚本只列出「文件:行」清单交人工核对。
- **拒绝**：新名不合规（只允许字母数字与 `_ . -`）、旧名不在名册、新名已有档（不覆盖别人的档）。

**测试落点**：`rename` 会写真源，与 `.tests/` 的「测试只读」约定冲突，故不进自动化套件（见
`multiagents/.tests/README.md`）；本次在模板上人工跑过一遍（含三条失败路径），改名后
`init` / `todo verify` / `memory verify --all` / 测试套件全绿。

## 20. 变更记录：多语言输出（资源字符串，2026-10-17 夜，用户要求）

用户要求「代码里硬编码的中文字符改成资源字符串形式，按用户所选语言配置不同的字符串」。落地如下。

**机制**（`multiagents/i18n.py`，纯标准库）：

- **msgid 就是中文原文**：源码写 `i18n.t("名册（{n}）:", n=3)`，译文在 `multiagents/locales/<lang>.json`
  （键 = 中文原文，值 = 译文）。取 gettext 的思路：源码可读，缺译时**逐字回落原文**（不报错、不丢字）。
  带占位符的按 `str.format` 填；译文占位符写坏时退回原文再格式化，不抛异常。
- **zh 不建目录**：中文是源语言，查不到译文就返回 msgid。
- **语言来源**（优先级）：`--lang <code>` → 环境变量 `AGENTCTL_LANG` → `multiagents/state/settings.json`
  的 `lang` → 默认 `zh`。`--lang` 在**模块导入时**按 `sys.argv` 预扫，所以 argparse 的 `help=` 文本也跟着变。
- **写入口子**：`agentctl.py lang [code]`（查看 / 持久设置，写 `state/settings.json`）；`AGENTCTL_LANG`
  给 CI 与脚本；settings.json 是机器本地设置（已 gitignore）。skill `first-run` 要求引导员把用户选的语言
  当场用 `agentctl.py lang <code>` 落下来。
- **边界**：用户可见输出（`print`、argparse help、导出视图的模板）走 `i18n.t`；**docstring、注释、
  开发脚本的内部断言保持中文**（读者是维护者）。这条写进了 skill `repo-conventions`。

**一次性转换**（AST 改写 + 等价性验证）：`agentctl.py` 170 处 f-string、190 处普通字面量改成 `i18n.t(...)`
（`sync_skills.py` 8 + 4）。规则：f-string 的 `{expr}` 变 `{占位名}`（表达式是简单标识符就直接用标识符名，
否则 `p0`/`p1`），格式说明符逐字保留（`{x:<16}` → `{p0:<16}`）。改完 16 处超过 132 字符的调用按值折行
（隐式拼接，值不变）。

**转换踩的坑**（都实测复现）：

- CPython 的 `col_offset` 是 **UTF-8 字节偏移**：含中文的行必须换算回字符偏移，否则按偏移切源码会切错
  （首次改写即产出非法语法，错行位置还因折行而漂移，容易误判）。
- `format_spec` 的源片段**带前导冒号**，要 `lstrip(":")`，否则生成 `{p0::<16}`。
- `t` 会和函数里的局部变量撞名（`build_parser` 里有 `t = sub.add_parser("todo")` → `UnboundLocalError`），
  转换后一律写 `i18n.t(...)`。

**等价性验证（本改动的核心保障）**：改前先用**原件**跑 37 条命令（覆盖 `roster` / `card` / `todo` /
`memory` / `task` / `json` / `file` / `init` / `me` / `--help` / 两种 skill 同步检查）存快照，改后同跑逐字
diff——**zh 下输出必须与改前完全一致**（唯一允许的差异是 `file locks` 的锁历史，它随写入增长）。再加
`init` / `todo verify` / `memory verify --all` / `sync_skills --check` / `.tests` 19 条全绿。

**目录维护**（`multiagents/i18n_extract.py`）：扫 `multiagents/*.py` 抓 `i18n.t("…")` 的 msgid →
`--new <lang>` 建骨架、无参跑更新（补新 msgid / 删失效键 / 保留已有译文）、`--check [lang]` 查空译文与
**占位符（名 + 格式说明符 + 转换符）逐字一致**，有命中 exit 1。检查器做过反向验证：故意把 `{p0:<16}`
改成 `{p0}` 能被报出来（漏译在运行时是静默的，只有这个口子会报）。

**交付**：`zh`（源语言，无目录）、`ja` 364/364、`en` 364/364。两份译文由后台 subagent 产出（en 那份在
服务重启后重跑了一次），主会话独立复核了占位符 token 与译文残留（英文无中文残留；日文抽查无简体字形混入）。

**模板**：同一批改动同步到 `multi_agents_templates`（框架代码逐字一致，另加 `locales/{ja,en}.json`、
`i18n*.py`、SCRIPTS/README/skill 相应更新），模板侧 `init` / `todo verify` / `memory verify --all` /
`.tests` / `sync_skills --check` / `i18n_extract --check` 同样全绿；模板不带 `state/settings.json`
（没有就是默认 zh）。

## 21. 变更记录：根 `AGENTS.md` 换成 v2（规程下沉到 9 个 skill 后落地）（2026-10-17 夜，用户要求）

**背景**：前几日把「过程性规程」从根 `AGENTS.md` 抽进 9 个项目 skill，候选稿与逐节映射备在
`archive/others/AGENTS_proposal_v2_2026-10-17.md` 和 `..._notes.md`（18 节全部有落点、5 条未落点、
10 项待拍板），按用户要求一直不动根文件。本次用户拍板「把本项目替换成 v2」。

**替换**：`AGENTS.md` 413 → 113 行（非空 360 → 88，notes 里定的预算 ≤90），原件备份
`archive/others/AGENTS_pre_v2_2026-10-17.bak.md`（md5 `533f3e8f…`）。相对候选稿只动三处，都由「落地必需」推出：

1. 候选稿末尾「附：改项目通用文件一律走加锁接口（待并入正文）」**并进「硬约束」第 4 条**——它自己标着
   「待并入正文」，并入后与开源模板 `multi_agents_templates/AGENTS.md` 的结构一致（那份更早并入）。
2. skill 地图**补一行 `first-run`**（模板那份地图本就有此行），并保留「项目专属 skill 按同样方式加」一句。
3. 「身份与多 agent」补回**临时文件放 `/tmp/<agent>/`**：`agentctl.py new/spawn` 的用户可见提示写着
   「（AGENTS.md：临时文件一律放这里）」，根文件若不写这条，提示就成了假指针；另一条路是改 msgid 加两份
   译文，成本更高。其余候选稿未动（含「每步自动注入」那节保留 opencode 插件钩子的说明，仍标为可选便利层）。

**悬空指针**：按节名引用被迁走内容的活指针 13 处，全部改指对应 skill：

- `scripts/loveplus/SCRIPTS.md`（4 处）、`scripts/loveplus/sync_from_txnew.sh`、`type_input.py`、`shot_ocr.py`
  → skill `loveplus-emu-ops`
- `multiagents/README.md`、`multiagents/SCRIPTS.md`：节名「多 agent 并行」→「身份与多 agent」
- skill 真源 3 处表述按新分工改写：`multiagent-workflow`（「AGENTS.md 只写抽象规则」）、
  `repo-conventions`（「通用抽象规则留在 AGENTS.md」）、`report-writing`（「根 AGENTS.md 三处引用
  `rigorous-writing`」——替换后此说已不成立）
- 记忆真源 4 处：`loveplus/headless_azahar` 节 13、`loveplus/touch_coords_nlpplus` 节 02、
  `others/diary/2026-10-17_02_static-re` 前言、`others/first_run` 节 05 的「待拍板」条目
- 顺带修 `skills/loveplus-nlpplus-guide/scripts/sync_coords.py` 的目标：它仍往**镜像**写
  （`SKILL_REL` = `.opencode/skills/...`），真源搬到 `skills/` 之后这等于「改镜像」，下一次
  `sync_skills.py` 就把它冲掉。改为写 `skills/loveplus-nlpplus-guide/SKILL.md`，再镜像（幂等性复跑一致）。

**保留**：日记、简报、`DESIGN.md` 与归档里对旧节名的叙述不回改——写下的就是当时事实；这类历史提及的
悬空风险由本节与当日日记承担。

**验收**（`/tmp/01_emu-gui/check_v2.py`，只读）：非空行 88 ≤ 90；9 个 skill 目录与 frontmatter 齐；
硬数字 `200`/`300`/`agentctl.py`/`todo.json`/`state/memory` 可 grep 到；无日期括号、无否定对比句式、
无 emoji；全仓库「AGENTS.md『节名』」式指针逐条比对（历史叙述除外）无悬空；`memory verify --all`、
`todo verify`、`sync_skills.py --check`、`init` 与 `multiagents/.tests/`（20 项）全绿。

**模板**：`multi_agents_templates` 的根 `AGENTS.md` 本就是同一结构（它更早把附录并入硬约束），本次只同步
3 处 skill 真源表述（`multiagent-workflow` / `repo-conventions` / `report-writing`）并重镜像。
## 22. 变更记录：同步 `rigorous-writing` 文风 skill（远端 → 真源 + 镜像 + 门禁闭环）（2026-10-17 夜，用户要求）

**背景**：缺口在 v2 替换前就存在——旧根 `AGENTS.md` 三处引用 `.opencode/skills/rigorous-writing/SKILL.md` 与
`style_lint.py`，两者本机都不存在；skill `report-writing` 写着「门禁脚本在本机不存在，体检只能人工做」。
本次用户要求「从远端同步一下 严谨文风 skill」，即把这条门禁补实。

**源**：远端 `tx-new`（`.env` 的 `LOVEPLUS_REMOTE`）上的
`work/schwab_api/agent_cowork/.opencode/skills/rigorous-writing/`，mtime 2026-10-01（与 `report-writing` 里
「2026-10-01 补充」对应，本仓库原先那份是它的摘要）。8 个文件：`SKILL.md` +
`references/{structure,sentence-level,claims-and-evidence,anti-ai-tone,checklist}.md` +
`scripts/{style_lint,style_rules}.py`（纯标准库；`--selftest` 内置 11 条正例，覆盖每条规则）。

**落点**：真源 `skills/rigorous-writing/`（与 `loveplus-nlpplus-guide` 带 `scripts/` 的先例一致），
`sync_skills.py` 镜像三处 → 真源 **10 个 skill / 18 个文件**。写入全部走 `agentctl.py file write`（加锁 + 原子替换）。

**去项目专有化**（`/tmp/01_emu-gui/adapt_rw.py`，片段级替换 + 唯一性断言；64 处 + 3 条出处正则）：

| 类别 | 处理 |
| --- | --- |
| 另一项目的仓库名与报告路径（表格「原文（出处）」列） | 出处改成通用写法或略去；反例文本本身保留 |
| `memory/<别项目>/README.md`、`AGENTS.md`「报告撰写」/「绘图」等旧指针 | 改指本仓库现落点：skill `report-writing`「数字核验」、skill `plotting-standards` |
| 机器绝对路径（`references/anti-ai-tone.md` §11 取证段的 `cd`） | 改为「在仓库根执行」+ 仓库相对命令 |
| `.opencode/skills/rigorous-writing/scripts/style_lint.py` | 改为真源路径 `skills/rigorous-writing/scripts/style_lint.py` |
| 源项目实测数字（加粗 95–146、破折号 218、emoji 539/148、横断面 37 文件 / 12,998 行 / 命中 1,486） | 数字保留，措辞改「导入时源项目实测」 |

**规则未改**：§三 11 条禁令、§一/§二/§四 的方法与 `references/` 的判据逐字保留；`scripts/style_rules.py`
与 `references/sentence-level.md` 逐字节拷贝。文件尾加「导入说明」（源版本 2026-10-01、同步日期、只做了哪些改动），
下次再同步按它对齐。

**真源 md5 与上游并列**（本地有意改过的不相同，其余相同）：

```
b75d4357a3ebd50777b03683be53f815  SKILL.md                        上游 9d57a88dc4b9f6c6f37fc1e94e7de32c
e4b5cf0f8bf5768115725c006409cfbb  references/anti-ai-tone.md      上游 8311cc17cb99ffa3287117b3d7f3cd3a
7ff356fe082cf97cb975aec41c06bba3  references/checklist.md         上游 d2dc9192611601d0edab568d239ad136
49cbfec18978040e3062ae2c5ac963ff  references/claims-and-evidence.md 上游 0ca27393d5a3d80b74efbf6f23084bf8
f50f1aab9a34b4190ad3f2bf7fe8cc94  references/sentence-level.md    上游同
2412262518cbbad862a7fbb38ebfcf83  references/structure.md         上游 9c62ff2d5eef3cc240f81e6396c478e3
ffc72f017c7925fcb891d851f8a46684  scripts/style_lint.py           上游 23c00f2cf17be1d6f6ae4003673d0cbd
3654b7b27fe3b8ac7c2740c3c88db992  scripts/style_rules.py          上游同
```

**顺手修掉上游一处自相矛盾**：`SKILL.md` §三 的硬标准是「加粗 ≤ 10 处/百行」，而 `style_lint.py` 的默认阈值是
`--bold-per-100 30`（只有 `references/checklist.md` 用了显式 `--bold-per-100 10 --dash-per-100 2`）。本次把
`SKILL.md` §四 与 `report-writing` 给出的命令统一成**显式阈值**：照默认值跑比标准松三倍，等于假通过。

**接线**：`report-writing` 不再重抄文风与否定句式两节（同一件事一处写），改为指 `rigorous-writing`，自己只留
门禁命令与「改文风不得改动数字」；根 `AGENTS.md` skill 地图补 `rigorous-writing` 一行、收尾清单那条改指
`rigorous-writing` 的 `style_lint.py`（非空行 88 → 89，仍在 ≤90 预算内）。

**验收**：`--selftest` 11 条正例全部报出；对 `output/loveplus/report/siren14_decode.md`（304 行）跑
`--bold-per-100 10 --dash-per-100 2` 得 0 命中（这份报告当初只能人工对照，这次补上机器复核）；
`sync_skills.py --check` 0 漂移；`init`（skill 真源 10 个）/ `todo verify` / `memory verify --all` /
`i18n_extract --check`（en、ja 各 364 键 0 未译）/ `multiagents/.tests/`（20 项）全绿。

**模板**：`multi_agents_templates` 仍是 6 个通用 skill，本次未动。`rigorous-writing` 是通用 skill，本该进模板，
但那份在用户验收中，等一句话再同步（成本＝真源目录 + 地图一行 + 重镜像）。

## 23. 新功能：初次安装进度 `onboard`（真源 `state/first_run.json`；中断可续）（2026-10-17 夜，用户要求）

**问题**：「项目是否 init 过」原先没有判断——`init` 是字段引用自检、不记状态；`me` 那句「刚克隆先按
`first-run` 引导」由名册 `created_by=="framework"` 推出，是常量；引导中途退出后没有任何进度可续。

**设计**（用户拍板：进度以机器判定为主）：

- 真源 `multiagents/state/first_run.json`：8 步（id / 标题 / 状态 todo|doing|done|skip / 时间戳），
  步骤标题与 skill `first-run` 的「最小可跑初始化清单」**逐字对应**（`.tests` 有一条断言盯这个）。
- 子命令 `agentctl.py onboard status | step <n> <state> | reset | finish`，走 `locked()` + `atomic_write`
  （与 todo.json 同一套）。`save_onboard` 会把新版本加的步骤补进旧档（前向兼容）。
- **机器判定优先**：步骤 3/4/5/6/7 现场算（`.env` 存在、`.venv` 可用、`sync_skills.py --check` 退出码、
  `current_agent()` 非空、主题数 >1），自报状态只对 1/2/8 这三步生效；机器判过的步骤显示证据短语。
  status 行末给「下一步：第 n 步」。
- **入口在 `me`**（两处）：未识别分支把原来那句常量提示换成 `onboard_hint_lines()`——无档 → 首装提示；
  有档未完成 → 进度 + 「继续 / 重新开始 / 暂不」；已完成 → 一行「已完成」（不再挂提示）。
  身份卡尾部同样挂这份提示。选项框由 agent 用客户端能力弹，脚本只报状态。
- i18n：28 条新 msgid，en/ja 各补全（392 键，`--check` 0 未译 0 占位符不一致）。
- 测试：`.tests` 20 → 22（`onboard status` 可跑、真源步骤与 skill 清单一致），模板同份测试（其 first_run.json
  不存在时 skip）。

**过程坑（记两条）**：

1. 给 `agentctl.py` 自己插大段代码时，`file edit` 的锚点行实际是 43 个 `-` + 空格 + 标题
   （我手抄成 45 个 `-` 没匹配上）；第一次手工 `Path.write_text` 等价替换救场成功，但**顺序上先试
   `file read` 精确取锚更稳**。同批 `import subprocess` 漏加（`onboard_auto` 要跑 `sync_skills.py --check`），
   `py_compile` 不报（名字错在运行期），第一次 `onboard status` 才炸——以后加依赖某模块的代码块要连 import 一起插。
2. **模板 `multiagents/SCRIPTS.md` 被整文件覆盖丢失了去专有化版**（我拿仓库版直接 cp 过去，且此前的
   `state/locks/edits.jsonl` 留痕已按「复位」删掉，无从比对）。处置：按仓库版逐段反推，替换回模板口径
   （示例 agent `01_worker`、板号 `1.1`、`<项目>/<主题>` 占位、通用示例词），全文 grep 无 loveplus / azahar /
   名册真名残留；结构（节序、表格、行数 195 vs 仓库 191）与删除前一致。教训：**对模板这类「同源异文」文件，
   永远用片段 edit，不做整文件覆盖**；edits.jsonl 是唯一编辑留痕，「复位出厂」前先留一份副本。

**同步**：`agentctl.py`、`locales/{en,ja}.json`、`.tests/test_framework.py` 同步进模板（框架文件两份同文）；
skill `first-run` 各自加 onboard 段（模板步骤 4 标题对齐其「装依赖」条目，机器判定跳过 `.venv`）；
`SCRIPTS.md` 两份各补 onboard 命令块。复位后模板 88 个文件，全套自检（init / todo verify / memory verify /
sync --check / i18n --check / .tests 22 项）两侧全绿。本仓库的 first_run.json 已 `finish`（7/8，步骤 8 是
本条报告本身）。
