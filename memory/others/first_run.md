<!-- 生成物，勿手改：真源 `multiagents/state/memory/others/first_run.json`；改动走 `python3 multiagents/agentctl.py memory …`，本文件由 `memory export --write` 重渲染。 -->

# 框架初次安装与使用

> 从 GitHub 克隆本框架后，让 agent 与用户把项目跑起来的最小路径。执行版是 skill `first-run`（真源 `skills/first-run/SKILL.md`），本档是给人读的说明、依据与边界。

2026-10-17 建了开源模板 `../multi_agents_templates/`（正本仓库的上一级目录，兄弟目录），当晚经用户验收通过。

模板内容：

- 框架本体：`multiagents/`（`agentctl.py`、`sync_skills.py`、`clients.json`、协议 `README.md`、速查 `SCRIPTS.md`）。
- 6 个通用 skill（`first-run` / `multiagent-workflow` / `repo-conventions` / `plotting-standards` / `quant-analysis-rules` / `report-writing`）＋ 三处镜像 `.opencode/skills/`、`.claude/skills/`、`.agents/skills/`。
- `AGENTS.md`（v2 草案去专有化）、根 `README.md`、`.env.example`、`.gitignore`、`requirements.txt`（框架本体只用标准库，列的是可选依赖）、`repos/.gitkeep` 等目录骨架。
- 种子真源：`state/todo.json`（1 个初始化主题 + 1 项）、`state/todo.footer.md`、`state/memory/others/first_run.json`；默认引导员 `multiagents/00_guide.json`。

不含：loveplus 研究内容、`scripts/loveplus/`、`memory/loveplus/`、`tools/azahar`、roms、真实 `.env`、`opencode.json`、`.mcp.json`、`DESIGN.md`（本仓库变更史）。

两处为「开箱即用」而做的框架改动：

- `init --fix` 现在也 `touch` 缺失的 `jobs[].log`：新克隆上该日志必然还不存在，原先 `init` 会报不一致；补上后全新目录直接 `init` exit 0。
- `agentctl.py` 里写死的示例名（`todo claim … --owner 02_static-re`）与「认领引导员」提示（`00_haruhi`）改为从名册推导（`created_by == "framework"`）或占位符，模板与仓库两份副本因此不再分叉。引导员在模板里叫 `00_guide`（角色 `guide`），仓库仍叫 `00_haruhi`。

`repos/` 约定（外部代码仓库）：

- `repos/<名字>/` 放研究或依赖对象的代码库，形态是 clone 或 symlink；`src/` 只放自己写的模块级代码，`tools/` 放要跑/构建的第三方工具。混放会分不清哪些是自己写的（许可与跟上游同步都变麻烦）。
- `repos/` 默认不入版本库；可复现性靠记忆补：URL + commit（或 tag / branch）+ 是否打过 patch 写进 `memory/<项目>/`。
- 初始化时由引导员问用户「这份代码从上游 clone 进来，还是链到你本机已有的那份」，不替用户决定；默认 clone（自包含、可复现），复用已有克隆（打过 patch 还要在本机跑）或磁盘紧张用 symlink 并把真实路径写进 `.env`。

落地位置：skill `first-run` 第 2 步与「研究目标决定目录」表、skill `repo-conventions` 新节「外部代码仓库（`repos/`）」、v2 草案目录表新增 `repos/` 行；仓库本体与模板两份都改，镜像已重同步（`sync_skills.py --check` 为 0）。

- **仓库自己的引导员**是 `00_haruhi`（人设 = 凉宫春日）；**开源模板** `multi_agents_templates` 的引导员是 `00_yuki`（長門有希 / Nagato Yuki，角色 `yuki`）。两者的说话方式都定在 `skills/first-run/SKILL.md` 的「人设与口吻」一节，只是内容不同：改模板那份别动仓库这份。
- 模板引导员的自我介绍分两段：**开场白**（中文 / 日本語 / English 三份，按用户选定语言取一段；角色的标志句「対有機生命体コンタクト用ヒューマノイド・インターフェース。それが、わたし」**只做直译**——不改写、不意译、不按框架语境本地化，日语版即原文）＋**「目录 + 能力」介绍**（每个目录做什么、我自己能做什么，用同一口吻）。开场前先用客户端的选择题机制问一次语言（opencode `question`、Claude Code `AskUserQuestion`；没有该能力就退化成一句普通提问）。
- 改 agent 名字用 `agentctl.py rename <旧> <新>`（2026-10-17 加，见 `DESIGN.md` §19）：档名 / `name` / `/tmp/<旧名>`（连内容搬） / `jobs[].log` / 板子认领人 / 记忆节归属 / `created_by` 一并改并重导视图；README、skill、记忆正文里的旧名只打印「文件:行」交人工核对（叙述里的旧名常常**不该**改）。
- 首跑就撞到一个坑，被 `init` 抓住：`rename` 只改了 `/tmp/<旧名>` **字段**、没搬目录，`init` 立刻报 `jobs[首次自检]` 的日志不存在，模板 `.tests/` 里「`init` 干净」那条断言也一起失败。补 `move_tmp_dir()`（旧目录连内容搬到新名；两边都在则不覆盖、提示人工合并）。这类「字段指到新路径、文件留在旧路径」的错，正是 `init` 自检值得跑的理由。

根 `AGENTS.md` 的 v2（候选稿 + 逐节映射在 `archive/others/AGENTS_proposal_v2_2026-10-17{,_notes}.md`）
已应用：413 → 113 行、非空 360 → 88，原件备份 `archive/others/AGENTS_pre_v2_2026-10-17.bak.md`。
结构是「硬约束 + skill 地图 + 每个 skill 何时加载」，过程性规程全部在 skill 真源 `skills/` 里，
根文件只留每次都要遵守的四条硬约束（脚本模块化 / 路径隐私 / 真源与视图 / 改通用文件走加锁接口）。

相对候选稿只动三处（都由落地必需推出）：① 候选稿末尾「附：…（待并入正文）」并进硬约束第 4 条；
② skill 地图补 `first-run` 一行（模板那份本就有）；③ 补回「临时文件放 `/tmp/<agent>/`」——`new`/`spawn`
的用户可见提示引的就是这条，不写则提示成假指针。

同时修掉 13 处按节名引用旧节的活指针（脚本 4 个文件 → skill `loveplus-emu-ops`；`multiagents/README.md`
与 `SCRIPTS.md` 的「多 agent 并行」→「身份与多 agent」；3 个 skill 真源的旧表述；4 处记忆真源），并修了
`sync_coords.py` 写错目标（它一直写镜像 `.opencode/skills/...`，真源搬到 `skills/` 后会被下一次
`sync_skills.py` 冲掉；改为写真源再镜像）。日记/简报/DESIGN/归档里的历史提及不回改。

验收：非空行 88 ≤ 90；9 个 skill 目录与 frontmatter 齐；硬数字与命令名可 grep；无日期括号、无否定句式、
无 emoji；指针逐条比对无悬空；`memory verify --all` / `todo verify` / `sync_skills.py --check` / `init` /
`.tests`（20 项）全绿。模板侧同步了 3 处 skill 真源表述并重镜像（模板根 `AGENTS.md` 结构本就相同）。

## 框架是什么

一句话：把一次研究工作组织成「多 agent 并行 + 真源/视图分离」的工作区。

- 多 agent 并行：同一工作区可同时有多个 agent 会话，且可来自不同客户端。身份唯一来源是 `agentctl.py me`——会话匹配则自动登记并打印身份卡；匹配不到就打印名册与三个选项（名册某项 / `new` 新增 / 暂不登记），退出码 3 是正常分支，不得自行认领。
- 真源 JSON 与导出视图：任务板真源 `multiagents/state/todo.json`、视图是根 `TODO.md`；记忆真源 `multiagents/state/memory/**/*.json`、视图是 `memory/**/*.md`。视图由机器生成，手改会被下次导出覆盖（`todo verify` / `memory verify --all` 能查出漂移），写入一律走 `agentctl.py`（对 JSON 加 flock 原子改）。
- skill 按需注入：真源 CLI 中立，放在 `skills/<id>/SKILL.md`；用 `multiagents/sync_skills.py` 镜像到 `.opencode/skills/`、`.claude/skills/`、`.agents/skills/`，`--check` 只查漂移。
- 三个落点：任务板（可被认领）、记忆（共享知识）、简报（`agentctl.py report` 落 `multiagents/report/<日期时间>_<agent>.md`）。
- 目录按主题归档：`scripts/<主题>/`、`data/<主题>/`、`output/<主题>/{report,img}/`，细则见 skill `repo-conventions`。

协议全文 `multiagents/README.md`，工具速查 `multiagents/SCRIPTS.md`，设计草案 `multiagents/DESIGN.md`。

## 初次安装（最小可跑）

| # | 步骤 | 命令 | 校验 |
| --- | --- | --- | --- |
| 1 | 自报家门 | 无 | 讲清框架是什么、我是谁、能做什么 |
| 2 | 配路径 | `cp .env.example .env` | 填齐 `.env.example` 的键 |
| 3 | 装依赖 | `python3 -m venv .venv && ./.venv/bin/python -m pip install -r requirements.txt` | `./.venv/bin/python -c "import mcp, dotenv, PIL"` |
| 4 | 同步 skill | `python3 multiagents/sync_skills.py` | `--check` 返回 0 |
| 5 | 认领身份 | `python3 multiagents/agentctl.py me` | 退出码 0；退出码 3 则走 `new <角色>` |
| 6 | 建主题 | `python3 multiagents/agentctl.py todo topic add "主题名" --owner <agent>` | `todo list` 出现新主题号 |
| 7 | 报告结果 | 无 | 列出跑通项、卡点与下一步建议 |

`.env` 的键：`LOVEPLUS_REPO`（仓库绝对路径，其余路径默认相对它推导）、`AZAHAR_HEADLESS`、`AZAHAR_QT`、`NLP_PLUS_ROM`、`NLP_CODE_UNPACKED`、`NLP_CODE_BIN`、`EMU_LIVE_PORT`、`EMU_GDB_PORT`、`EMU_DUMP_PREFIX`（默认 `/tmp/az_live`）、`LOVEPLUS_REMOTE`（远端 ssh 别名，可留空）。

依赖前提：Python <3.13。`requirements.txt` 文件头写明 `rapidocr-onnxruntime` 声明 Requires-Python <3.13，在 3.14 上无可安装版本；仓库根 `.python-version` 为 3.12。只做纯分析主题时不碰模拟器，`EMU_*` 与 ROM、code.bin 的键可先留占位。

## agent 档案的每个字段用在哪

一 agent 一档：`multiagents/<name>.json`（靠有没有 `name` 键与非档案 json 区分）。下表给出「字段是什么 + 它引用的文件/对象实例是什么」，可照此初始化一个新 agent。

| 字段 | 是什么 | 引用的对象/文件实例 |
| --- | --- | --- |
| `name` | 唯一标识，格式 `<两位自增序号>_<role>` | 档文件名 `multiagents/<name>.json`；序号不复用、不回收 |
| `role` | 角色短标识（如 `emu-gui`、`static-re`、`haruhi`） | `name` 的后缀；改名须同步文件名与 `name` |
| `display` | 中文职责说明，给人看 | 无 |
| `client` | 当前客户端（默认 `opencode`） | 探测规则表 `multiagents/clients.json` |
| `status` | `active` / `paused` / `blocked` / `done` | 无 |
| `updated` | 最后写入时间戳 | 每次写操作与 `json touch` 刷新 |
| `focus` | 一句话说在做什么 | 无 |
| `sessions[]` | 已登记会话（`client`/`session_id`/`title`/`state`/`last_seen`） | 客户端会话实例（如 `ses_…`）；`me` 靠它匹配身份 |
| `board[]` | 我认领的项目级任务号 | 任务板真源 `multiagents/state/todo.json` 里的 `1.3` 这类编号（视图 `TODO.md`） |
| `todo[]` | 我自己的私人清单（不共享、不可认领） | 存在本档内，用 `task add/done/…` 操作；与 `todo` 命令的项目板分家 |
| `claims.files` | 我占用的仓库文件或目录 | 具体仓库路径（动手前先扫别人的 `claims`） |
| `claims.tmp` | 我的临时目录 | `/tmp/<agent>/` |
| `claims.resources` | 我占用的设备/工具等资源 | 如 `r2`、`azahar-gui` |
| `memory[]` | 我维护或贡献的记忆档（含 `role`） | 真源 JSON `multiagents/state/memory/<项目>/<档>.json` |
| `skills[]` | 我这个 agent 该用的 skill ID | `skills/<id>/SKILL.md`（镜像在各 CLI 的 skills 目录）；`me` 会打印 |
| `jobs[]` | 长任务登记（`name`/`pid`/`log`/`note`） | `log` 指向日志文件（如 `/tmp/<agent>/build.log`） |
| `artifacts[]` | 我产出的文件 | 产出文件本体（脚本、图、报告） |
| `handoff` | 交接留言（给某个 agent） | 无独立文件；`me` 打印 |
| `created_by` | 由哪个 agent 或来源创建 | 生成方的 `name`（`spawn` 时写入）；随框架发布的档写 `framework` |
| `history[]` | 变更记录（`t` 时间戳 + `e` 事件） | 无 |

写入口只有 `agentctl.py json …`（`get`/`set`/`add`/`remove`/`history`/`touch`/`memory`/`job`/`handoff`/`artifact`）。不要手写 JSON，脚本用 `flock` 原子改写。

## 私有内容与开源边界

按 2026-10-17 的仓库现状逐项核对（`ls -a`、`.gitignore`、`.env.example`、`multiagents/*.json`、`memory/**`）。

| 需清理或抽取的东西 | 现状 | 处理 |
| --- | --- | --- |
| `.env` | 真实机器绝对路径，已在 `.gitignore` | 不提交；发布用 `.env.example` |
| `opencode.json`、`.mcp.json` | 命令写死 `<repo>/scripts/loveplus/run_mcp.sh` | 改成相对路径或由 `.env` 派生 |
| `multiagents/01_emu-gui.json`、`02_static-re.json` | 含真实 `session_id`（`ses_…`）与会话标题 | 清空 `sessions[]`，只留字段结构 |
| `multiagents/report/**` | 简报含真实进展 | 抽框架时删 |
| `memory/**` | 真实研究记录（逆向笔记、坐标表、日记） | 抽框架时删；保留 `first_run` 这类框架档 |
| `archive/**`（4.1G） | 旧 TODO、md 快照、游戏截图、roms | 抽框架时删 |
| `data/**`（2.9G）、`archive/loveplus/roms` | 游戏 ROM 与解包资源，版权物 | 删 |
| `tools/**`（3.6G） | azahar / 3dstool / r2 / gdb 源码与构建产物 | 删 |
| `.venv/`（664M） | 虚拟环境 | 删；当前 `.gitignore` 未列 `.venv`，开源前补上 |
| `output/**` | 报告与图（含 `output/gaming_agents/` 框架设计稿） | 按需保留设计类文档 |
| 其它含 `<repo>` 的文本 | 工作区共 18 个文本文件命中（另有 11 个 `__pycache__/*.pyc`），分布在 `scripts/`、`multiagents/`（含 `state/**` 真源与 `DESIGN.md`）、`memory/`（含 `state/**` 真源）、`output/`、`TODO.md`、`AGENTS.md`、`opencode.json`、`.mcp.json`、`.env.example`。复算：`grep -rl <repo> --exclude-dir={.git,.venv,tools,archive,data} .` | 逐个改写为相对路径或占位；生成视图改真源即可 |
| `web_doc/` | 根 `AGENTS.md` 目录表列了它，当前仓库不存在 | 目录表与实际不符，待核 |

两种做法：

- 整仓开源：好处是研究过程与产出一起可复现；代价是要先清掉上表全部内容，工作量大，游戏资源本身也不适合公开发布。
- 只抽框架子集：发布 `multiagents/` + `skills/` + `AGENTS.md` 模板 + `README.md`（可加 `archive/others/` 的规约草案与 `memory/others/first_run`），loveplus 研究留在私有仓库。框架不依赖游戏资源即可运行：`sync_skills.py` 与 `agentctl.py` 只用 Python 标准库。

建议本次按「只抽框架子集」发布，整仓开源待版权与隐私理清后再议。

## 00_haruhi：默认引导员

- 角色 `haruhi`，`display` = 框架默认引导员（初次安装向导），随仓库发布；`created_by` = `framework`。
- 职责：介绍框架与 skill 机制、引导初始化、报告结果；不做具体研究任务（见其 `focus`）。
- **兼任本地 contributor**：经用户授意可修改与更新框架本体（`multiagents/`、`skills/`、根规约文件），
  该目录已在她 `claims.files` 里；改前照 skill `repo-conventions` 的加锁接口，改完 `init` / `.tests` /
  `sync_skills.py --check` 全绿才算完（2026-10-17 用户授意，模板 00_yuki 同款）。
- 新用户有两种走法：`me --name 00_haruhi` 认领它，或 `new <角色>` 建自己的 agent。认领前仍须由用户从名册里选。
- 档案 `multiagents/00_haruhi.json` 是全字段实例（含 `claims`、`memory[]`、`skills[]`、`jobs[]`、`artifacts[]`、`handoff`、`history[]`），可当初始化新 agent 的模板。
- 它挂的 skill：`first-run`、`multiagent-workflow`、`repo-conventions`、`rigorous-writing`（改规约文本过文风门禁）。
- 根 `AGENTS.md` 的「默认引导员 00_haruhi」节写了它（随 v2 应用落地）；名册仍归 `multiagents/`。

## 开源模板 multi_agents_templates 与 repos/ 约定

# 框架初次安装与使用

2026-10-17 建了开源模板 `../multi_agents_templates/`（正本仓库的上一级目录，兄弟目录），当晚经用户验收通过。

模板内容：

- 框架本体：`multiagents/`（`agentctl.py`、`sync_skills.py`、`clients.json`、协议 `README.md`、速查 `SCRIPTS.md`）。
- 7 个通用 skill（`first-run` / `multiagent-workflow` / `repo-conventions` / `plotting-standards` / `quant-analysis-rules` / `report-writing` / `rigorous-writing`）＋ 三处镜像 `.opencode/skills/`、`.claude/skills/`、`.agents/skills/`。
- `AGENTS.md`（v2 草案去专有化）、根 `README.md`、`.env.example`、`.gitignore`、`requirements.txt`（框架本体只用标准库，列的是可选依赖）、`repos/.gitkeep` 等目录骨架。
- 种子真源：`state/todo.json`（1 个初始化主题 + 1 项）、`state/todo.footer.md`、`state/memory/others/first_run.json`；默认引导员 `multiagents/00_yuki.json`。

不含：loveplus 研究内容、`scripts/loveplus/`、`memory/loveplus/`、`tools/azahar`、roms、真实 `.env`、`opencode.json`、`.mcp.json`、`DESIGN.md`（本仓库变更史）。

两处为「开箱即用」而做的框架改动：

- `init --fix` 现在也 `touch` 缺失的 `jobs[].log`：新克隆上该日志必然还不存在，原先 `init` 会报不一致；补上后全新目录直接 `init` exit 0。
- `agentctl.py` 里写死的示例名（`todo claim … --owner 02_static-re`）与「认领引导员」提示（`00_haruhi`）改为从名册推导（`created_by == "framework"`）或占位符，模板与仓库两份副本因此不再分叉。引导员在模板里叫 `00_yuki`（角色 `yuki`），仓库仍叫 `00_haruhi`。

`repos/` 约定（外部代码仓库）：

- `repos/<名字>/` 放研究或依赖对象的代码库，形态是 clone 或 symlink；`src/` 只放自己写的模块级代码，`tools/` 放要跑/构建的第三方工具。混放会分不清哪些是自己写的（许可与跟上游同步都变麻烦）。
- `repos/` 默认不入版本库；可复现性靠记忆补：URL + commit（或 tag / branch）+ 是否打过 patch 写进 `memory/<项目>/`。
- 初始化时由引导员问用户「这份代码从上游 clone 进来，还是链到你本机已有的那份」，不替用户决定；默认 clone（自包含、可复现），复用已有克隆（打过 patch 还要在本机跑）或磁盘紧张用 symlink 并把真实路径写进 `.env`。

落地位置：skill `first-run` 第 2 步与「研究目标决定目录」表、skill `repo-conventions` 新节「外部代码仓库（`repos/`）」、v2 草案目录表新增 `repos/` 行；仓库本体与模板两份都改，镜像已重同步（`sync_skills.py --check` 为 0）。

2026-10-17 夜（用户验收后）的两件收尾：

- **复位成出厂状态**：删掉验收期间的痕迹——`cp .env.example .env` 出的 `.env`、`multiagents/state/locks/`（加锁留痕与 `edits.jsonl`）、`multiagents/__pycache__/`；引导员档案把 `client` 清回 `""`、`sessions[]` 清空（等用户 `me --name 00_yuki` 认领），`todo[]` 里 a1 / a4 / a5 从 `done` 复位为 `todo`，`updated` 回到改名时刻 `2026-10-17T19:15:41+08:00`。复位后出厂文件共 88 个（比验收前多的 14 个是 `rigorous-writing` 的真源 8 个 + 三处镜像 6 个）。
- **同步 `rigorous-writing`**：该 skill（含 `scripts/style_lint.py` 门禁）连同本仓库 `report-writing` 的接线一起进模板——真源 7 个 skill / 14 个文件、三处镜像 0 漂移；模板 `AGENTS.md` 补 skill 地图一行、收尾清单那条改指 `rigorous-writing`。模板自检 `init` / `todo verify` / `memory verify --all` / `i18n_extract --check` / `.tests`（20 项）/ `style_lint.py --selftest` 全绿。

## 07 开源模板的引导员：00_yuki（長門有希）

- **仓库自己的引导员**是 `00_haruhi`（人设 = 凉宫春日）；**开源模板** `multi_agents_templates` 的引导员是 `00_yuki`（長門有希 / Nagato Yuki，角色 `yuki`）。两者的说话方式都定在 `skills/first-run/SKILL.md` 的「人设与口吻」一节，只是内容不同：改模板那份别动仓库这份。
- 模板引导员的自我介绍分两段：**开场白**（中文 / 日本語 / English 三份，按用户选定语言取一段；角色的标志句「対有機生命体コンタクト用ヒューマノイド・インターフェース。それが、わたし」**只做直译**——不改写、不意译、不按框架语境本地化，日语版即原文）＋**「目录 + 能力」介绍**（每个目录做什么、我自己能做什么，用同一口吻）。开场前先用客户端的选择题机制问一次语言（opencode `question`、Claude Code `AskUserQuestion`；没有该能力就退化成一句普通提问）。
- 改 agent 名字用 `agentctl.py rename <旧> <新>`（2026-10-17 加，见 `DESIGN.md` §19）：档名 / `name` / `/tmp/<旧名>`（连内容搬） / `jobs[].log` / 板子认领人 / 记忆节归属 / `created_by` 一并改并重导视图；README、skill、记忆正文里的旧名只打印「文件:行」交人工核对（叙述里的旧名常常**不该**改）。
- 首跑就撞到一个坑，被 `init` 抓住：`rename` 只改了 `/tmp/<旧名>` **字段**、没搬目录，`init` 立刻报 `jobs[首次自检]` 的日志不存在，模板 `.tests/` 里「`init` 干净」那条断言也一起失败。补 `move_tmp_dir()`（旧目录连内容搬到新名；两边都在则不覆盖、提示人工合并）。这类「字段指到新路径、文件留在旧路径」的错，正是 `init` 自检值得跑的理由。

## 08 输出多语言（资源字符串）：机制与四条纪律

框架本体（`multiagents/*.py`）的用户可见文本走资源字符串：机制在 `multiagents/i18n.py`，设计记录见 `multiagents/DESIGN.md` §20，用法与坑表见 `multiagents/SCRIPTS.md`。

- **msgid 就是中文原文**：源码写 `i18n.t("名册（{n}）:", n=3)`，译文在 `multiagents/locales/<lang>.json`（键 = 中文原文）。**改了源码里的中文原文等于换了 msgid，旧译文随即失效**——改完跑 `python3 multiagents/i18n_extract.py` 更新目录，`--check` 应回到「未译 0｜占位符不一致 0」。
- **缺译是静默的**：查不到译文就回落中文，既不报错也不崩（译文占位符写坏也只退回原文）；只有 `--check` 会报。所以「跑起来没问题」不等于「译全了」。译文里的占位符必须与原文逐字一致，**含 `{p0:<16}` 这类格式说明符**，`--check` 会比对。
- **语言从哪来**：`--lang` → `AGENTCTL_LANG` → `multiagents/state/settings.json` → `zh`（默认）。引导员初次安装时用 `agentctl.py lang <code>` 把用户选的语言落下来（skill `first-run`）；`.tests/` 用 `AGENTCTL_LANG=zh` 固定，免得被本机设置影响。
- **只翻用户可见的输出**：docstring、注释、开发脚本的内部断言保持中文——读者是维护者，翻它们只增加维护面。

## 09 根 `AGENTS.md` 换成 v2（413 → 113 行）与它修掉的指针

根 `AGENTS.md` 的 v2（候选稿 + 逐节映射在 `archive/others/AGENTS_proposal_v2_2026-10-17{,_notes}.md`）
已应用：413 → 113 行、非空 360 → 88，原件备份 `archive/others/AGENTS_pre_v2_2026-10-17.bak.md`。
结构是「硬约束 + skill 地图 + 每个 skill 何时加载」，过程性规程全部在 skill 真源 `skills/` 里，
根文件只留每次都要遵守的四条硬约束（脚本模块化 / 路径隐私 / 真源与视图 / 改通用文件走加锁接口）。

相对候选稿只动三处（都由落地必需推出）：① 候选稿末尾「附：…（待并入正文）」并进硬约束第 4 条；
② skill 地图补 `first-run` 一行（模板那份本就有）；③ 补回「临时文件放 `/tmp/<agent>/`」——`new`/`spawn`
的用户可见提示引的就是这条，不写则提示成假指针。

同时修掉 13 处按节名引用旧节的活指针（脚本 4 个文件 → skill `loveplus-emu-ops`；`multiagents/README.md`
与 `SCRIPTS.md` 的「多 agent 并行」→「身份与多 agent」；3 个 skill 真源的旧表述；4 处记忆真源），并修了
`sync_coords.py` 写错目标（它一直写镜像 `.opencode/skills/...`，真源搬到 `skills/` 后会被下一次
`sync_skills.py` 冲掉；改为写真源再镜像）。日记/简报/DESIGN/归档里的历史提及不回改。

验收：非空行 88 ≤ 90；9 个 skill 目录与 frontmatter 齐；硬数字与命令名可 grep；无日期括号、无否定句式、
无 emoji；指针逐条比对无悬空；`memory verify --all` / `todo verify` / `sync_skills.py --check` / `init` /
`.tests`（20 项）全绿。模板侧同步了 3 处 skill 真源表述并重镜像（模板根 `AGENTS.md` 结构本就相同）。
