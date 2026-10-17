#!/usr/bin/env python3
"""把 NLP+ 坐标真源渲染进本 skill 的 SKILL.md（只替换标记之间的内容）。

真源：multiagents/state/memory/loveplus/touch_coords_nlpplus.json（正文按 `## 标题` 切节）
目标：skills/loveplus-nlpplus-guide/SKILL.md 中（skill 真源；改完由 `multiagents/sync_skills.py` 各 CLI 镜像）
      `<!-- COORDS:BEGIN -->` 与 `<!-- COORDS:END -->` 两行之间。

用法（任意 cwd 均可，仓库根向上自动定位）：
    python3 skills/loveplus-nlpplus-guide/scripts/sync_coords.py            # 写入
    python3 skills/loveplus-nlpplus-guide/scripts/sync_coords.py --dry-run  # 只打印差异
    python3 skills/loveplus-nlpplus-guide/scripts/sync_coords.py --check    # 有差异则 exit 1

标记缺失即报错退出，不会整文件重写；输出幂等（内容一致时不写盘、连跑两次结果相同）。
"""
import argparse
import difflib
import json
import sys
from pathlib import Path

BEGIN = "<!-- COORDS:BEGIN -->"
END = "<!-- COORDS:END -->"
SKILL_REL = "skills/loveplus-nlpplus-guide/SKILL.md"
SRC_REL = "multiagents/state/memory/loveplus/touch_coords_nlpplus.json"


def repo_root():
    """向上找含 AGENTS.md 与 multiagents/ 的目录，不写死机器路径。"""
    here = Path(__file__).resolve()
    for p in (here, *here.parents):
        if (p / "AGENTS.md").is_file() and (p / "multiagents").is_dir():
            return p
    sys.exit("错误：向上未找到仓库根（含 AGENTS.md 与 multiagents/ 的目录）")


def demote(body):
    """正文标题降两级（真源节标题占 ###），代码围栏内的行不动。"""
    out, fence = [], False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
            out.append(line)
        elif not fence and line.startswith("#"):
            out.append("##" + line)
        else:
            out.append(line)
    return "\n".join(out).strip("\n")


def render(data):
    head = [
        "> 本节由 `scripts/sync_coords.py` 从真源 json 生成，**勿手改**；",
        "> 机器真源 `{}`（视图 `{}`），共 {} 节，更新 {}。".format(
            SRC_REL, data["source"], len(data["sections"]), data["updated"]),
        "",
    ]
    pre = data.get("preamble", "").strip()
    if pre:
        head += [pre, ""]
    blocks = ["### {}\n\n{}".format(s["title"], demote(s["body"])) for s in data["sections"]]
    return "\n".join(head + ["\n\n".join(blocks)]).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只打印差异，不写文件")
    ap.add_argument("--check", action="store_true", help="有差异则退出码 1")
    args = ap.parse_args()

    root = repo_root()
    skill, src = root / SKILL_REL, root / SRC_REL
    for p in (skill, src):
        if not p.is_file():
            sys.exit("错误：文件不存在 {}".format(p))

    text = skill.read_text(encoding="utf-8")
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        sys.exit("错误：{} 中 {} / {} 标记必须各出现一次".format(SKILL_REL, BEGIN, END))

    data = json.loads(src.read_text(encoding="utf-8"))
    block = render(data)
    i = text.index(BEGIN) + len(BEGIN)
    new = text[:i] + "\n" + block + text[text.index(END):]

    if new == text:
        print("无变化：SKILL.md 已是真源渲染结果")
        return 0

    diff = list(difflib.unified_diff(text.splitlines(), new.splitlines(),
                                     "SKILL.md(旧)", "SKILL.md(新)", lineterm="", n=1))
    if args.dry_run or args.check:
        print("\n".join(diff))
        return 1 if args.check else 0

    skill.write_text(new, encoding="utf-8")
    print("已写入 {}：渲染 {} 节 / {} 行（差异 {} 行）".format(
        SKILL_REL, len(data["sections"]), len(block.splitlines()), len(diff)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
