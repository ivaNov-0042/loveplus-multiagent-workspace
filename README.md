# loveplus 研究工作区（多 agent 并行框架）

本仓库是一个以主题为单位的研究工作区：围绕一个主题做数据获取、清洗、分析与可视化，把脚本、数据、图表、报告与沉淀的经验统一归档。仓库自带一套多 agent 并行的协作框架（身份、任务板、记忆、skill），让多个 agent 会话在同一工作区里互不撞车。

仓库同时在做两件事：① 维护这套框架本身；② 用它做 New Love Plus+（NLP+）的逆向研究与自动游玩。

## 创建原因

opencode v2 已经支持多窗口 TUI。
你可以同时开多个会话窗口、并行处理多个任务——单看每个窗口，体验都很好。

但窗口之间是互相不知道对方存在的。对同一个项目开多窗口让多个 agent 协作时，问题立刻出现：
两个会话抢同一个身份、都改同一个文件丢更新、各自记的笔记互相覆盖、不知道对方认领了什么任务、
skill 在每个 CLI 里各一份很快改漂移。窗口多了，协同本身成了最难的活。

本仓库与配套模板（opencode-multiagents-project-templates）就是给这个场景补的骨架——刚好够用，不多不少：
一个 `agentctl.py`（纯标准库）管身份、任务板、记忆、加锁文件编辑；
会话第一步认领身份，写入走锁，记忆各写各的节，skill 单一源镜像分发。
复杂项目里「多个 agent 并行干活」需要的最小公约数，都在这了。

## 你可以怎么用

| 身份 | 要做的 |
| --- | --- |
| 做研究 | 认领一个主题（`todo topic add`），脚本、数据、产出分别落 `scripts/<主题>/`、`data/<主题>/`、`output/<主题>/` |
| 借框架 | 只取 `multiagents/` + `skills/` + `AGENTS.md` 模板 + `README.md`，装到你自己的项目里 |
| 贡献者 | 改框架与 skill 真源，跑 `sync_skills.py`、`multiagents/.tests/test_framework.py` 与 `memory verify --all` 收尾，把规则写回 `memory/` 与对应 skill |

框架不依赖本仓库的游戏资源即可运行：`multiagents/agentctl.py` 与 `multiagents/sync_skills.py` 只用 Python 标准库。

## 初次安装三步

完整清单（7 条命令）见 skill `first-run`，真源 `skills/first-run/SKILL.md`。三步概览：

1. 装依赖：`cp .env.example .env` 按注释填机器路径；`python3 -m venv .venv && ./.venv/bin/python -m pip install -r requirements.txt`（须 Python <3.13，见仓库根 `.python-version`）。
2. 认身份：`python3 multiagents/agentctl.py me`。认领不到时退出码 3 属正常分支，用 `python3 multiagents/agentctl.py new <角色> --display "…"` 建自己的 agent。
3. 建主题：`python3 multiagents/agentctl.py todo topic add "主题名" --owner <agent>`。

skill 目录没被发现时，先跑 `python3 multiagents/sync_skills.py`。

框架自检：`python3 multiagents/.tests/test_framework.py`（只读，不写任何真源；覆盖不变量 / 只读面 / 字段引用完整性，见 `multiagents/.tests/README.md`）。

## web_doc（网页文档）

- `web_doc/multiagents-site/`：multiagents 框架官网单页的**开发副本**（中/英/日三语 + robots/agents/sitemap）。
  发布源在模板仓库 `multi_agents_templates/web_doc/multiagents-site/`，已推送 GitHub（私有 `multiagents-site`）；
  本副本仅作历史留档，改动请在模板仓库做。

## 目录导航

| 路径 | 是什么 |
| --- | --- |
| `AGENTS.md` | 面向 agent 的硬约束与指针，开工前读 |
| `multiagents/` | 框架本体：名册与档案、任务板与记忆真源（`state/`）、`agentctl.py`、`sync_skills.py`、协议 `README.md` |
| `skills/` | skill 真源（CLI 中立），一 skill 一目录 |
| `memory/` | 记忆视图（`.md` 为生成物）；真源在 `multiagents/state/memory/` |
| `scripts/` | 脚本，按主题分目录，各配 `SCRIPTS.md` |
| `data/` | 清洗后的中间数据，受开源边界约束 |
| `output/` | 报告与图片：`output/<主题>/{report,img}/` |
| `tools/` | 第三方工具与源码（azahar / 3dstool / r2 / gdb） |
| `TODO.md` | 任务板视图（生成物），真源 `multiagents/state/todo.json` |

## skill 真源与镜像

skill 真源只有一份，放在 CLI 中立的 `skills/<id>/SKILL.md`。各家 code CLI 的 skill 目录不同，用 `python3 multiagents/sync_skills.py` 生成镜像：

```
skills/<id>/SKILL.md  ──sync_skills.py──▶  .opencode/skills/  .claude/skills/  .agents/skills/
```

镜像目录整体是生成物，改真源后重跑同步；`--check` 只查漂移（有漂移 exit 1）。

## 多语言输出

框架的 CLI 输出走资源字符串：源码里是 `i18n.t("中文原文", **占位)`，译文在 `multiagents/locales/<lang>.json`，**键就是中文原文**。中文是源语言、不需要目录，查不到译文就回落中文（漏译因此是静默的，用 `--check` 查）。

```bash
python3 multiagents/agentctl.py lang            # 看当前语言与可选语言
python3 multiagents/agentctl.py lang en         # 持久切换（写 multiagents/state/settings.json）
python3 multiagents/agentctl.py --lang ja todo list   # 只影响本次运行
AGENTCTL_LANG=en python3 multiagents/agentctl.py roster   # 环境变量
```

维护目录：`python3 multiagents/i18n_extract.py`（补新 msgid、删失效键）｜`--new <lang>`（建骨架）｜`--check`（查漏译与占位符不一致）。

## 开源与隐私边界

本仓库当前含真实机器路径、真实会话 ID、真实研究记录与游戏资源。开源前需清理或抽取的清单，以及「整仓开源 / 只抽框架子集」两种做法的取舍，见 `memory/others/first_run.md` 的「私有内容与开源边界」节。

## 许可

待定。
