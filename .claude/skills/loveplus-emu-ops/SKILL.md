---
name: LovePlus 模拟器与 harness 操作
description: 本仓库无头 azahar 模拟器（loveplus-emu MCP）与 harness 层操作细节：触摸坐标映射、长按规则、截图归档、读图与判定、图片压缩、MCP 重连、后台任务挂法、Code Mode、受阻处置。凡要用模拟器跑 loveplus（触摸/截图/OCR/输入）、改 loveplus_mcp.py、挂后台任务或读模拟器截图时加载本 skill；坐标与流程先查表再动手。
---

<!-- 生成物，勿手改：真源 `skills/loveplus-emu-ops/SKILL.md`；改完跑 `python3 multiagents/sync_skills.py` -->

# LovePlus 模拟器与 harness 操作

## 触摸坐标映射

- 控制命令（`touch`/`release`/`move`/`swipe`/`drag_path`/`tap`）用**原生 320×240 归一化** (x, y)，x,y ∈ [0,1]。
- `screenshot` 竖屏 dump 图为 240×320。经验映射（y 轴镜像）：

  `touch_x = 1 − dump_y/320`，`touch_y = dump_x/240`

- 具体实测坐标表：`memory/loveplus/touch_coords_nlpplus.md`、`memory/loveplus/headless_azahar.md`。

## 进新页面：先查表再动手

- 新页面先查 `memory/loveplus/touch_coords_nlpplus.md`。
- 表中无此页、或验证状态存疑时，先**按下 → 截图 → 变色确认**再长按；命中后**立即回填表格**。
- 每条坐标记录须含：**当前页面描述**（页面名/画面特征，防换页后坐标含义漂移）、touch 坐标、对应 dump 坐标、验证状态（变色验证 / 仅推算 / 未验证）。

## 长按与点击时长

- NLP+ 菜单/对话框必须**长按 ≥1 秒**：`tap`（12-14 帧≈0.2s）无效，需 `touch` + sleep(1.2~1.5s) + `release`。
- 具体实测坐标表在 `memory/`。

## 截图归档

- 交互截图按步骤归档：`/tmp/loveplus_shots/<步骤名>/NN_(u/b/a)_描述.jpg`。
- 步骤名如 `01_gamestart`；NN 为步骤内序号，文件名简述操作（如 `01_menu.jpg`、`02_hai_confirm.jpg`）。
- 同一会话跨多步骤时步骤目录递增编号；旧会话截图移 `_archive/` 不混放。
- **每步截图先归档再 read**，便于回溯失败操作与生成操作记录。

## 模拟器输入只能走标准 MCP

- 所有与模拟器交互的脚本/调用**必须走标准 MCP 工具**（`touch` / `release` / `move` / `swipe` / `drag_path` / `screenshot` / `buttons` / `ocr` / `tap` 等），**禁止直连内部 `loveplus_mcp._send`** 之类的私有 TCP 命令。
- 每次输入操作后把上屏 (u) 与下屏 (b) 截图落盘（`N_u_描述.jpg` / `N_b_描述.jpg`），上屏判定输入结果、下屏判定键盘/候选状态，直接 read 看图确认。
- 脚本侧统一封装对 MCP stdio 的 tool 调用，不要重开 socket 直连 `_send`。
- 工具选择优先级：有 MCP 时简单前台任务（截图/单点触摸/状态查询）直接调 MCP 工具；只有复杂编排（多步状态机、循环监控、批量转换）或后台常驻任务才写脚本落盘到 `scripts/loveplus/`。

## 画面判定：先等再判

- 画面看不懂、判定不了进度时：先 `sleep` 再重截图，不要立刻下结论。无头模拟器常在过场动画、loading、通信中、淡入淡出阶段截到**中间帧**（半透明、未渲染完、按钮还没画出来）。
- 处置顺序：① `sleep` 等 60~200 帧（1~3s，过场/加载取上限）→ ② 重新 `screenshot` → ③ 再 read 判定；仍判不了就再等一轮更长时间（5~10s）。
- 只有**连续 ≥2 轮间隔截图画面完全一致且无任何进展迹象**，才按"卡住"处理。
- **禁止凭单张中间帧截图下"流程错误/死循环"结论**。

## 读图与判定：用多模态，别写 CV 阈值

- 本环境 `read` 工具原生支持多模态读图。前台简单判定（按钮是否命中、确认当前画面、读键盘/候选文字）直接 `dump → 存图 → read 看图`。
- 不要写像素 diff / 亮度阈值代码：背景动画噪声（~27000/6s）足以淹没判定。
- 按钮命中判定流程：**touch 按下 → 立即 dump 截图 → read（按钮按下会变色）→ release**。

## 读图降级链 read → ocr → cv

`read` 多模态失败或返回异常时不要反复重试：

1. `read` 截图失败、或返回内容与请求文件不符（如读 .md 却返回图片）累计 ≥2 次
2. 改用 `ocr(which='b'/'u')`（返回文字 + dump 坐标 + touch 坐标，判定画面/找按钮）
3. OCR 仍拿不到关键信息（假名键、图形按钮等弱项）→ 用 CV：numpy/PIL 投影、色块检测（参考 `scripts/loveplus/grid_detect.py`、蓝色行块检测法），或裁剪局部放大后再 read。

**降级链每级至多重试 2 次，不要在失败级别死循环。**

## 图片压缩

- **最长边 >618 px 的图**：`read` 前先用 Python 压缩到 `/tmp/img_preview/`（最长边 ≤618 px、JPEG 质量 80）。
- **低分辨率图不必压缩**：模拟器截图（下屏 240×320、拼接 240×720）本身很小，直接 read 原图，文字更清晰。
- 标准流程（一次 shell 调用）：

  ```bash
  python3 - <<'EOF'
  from PIL import Image
  import os
  os.makedirs('/tmp/img_preview', exist_ok=True)
  for src in ['图片路径1', '图片路径2']:
      dst = '/tmp/img_preview/' + os.path.basename(src).rsplit('.', 1)[0] + '.jpg'
      im = Image.open(src); im.thumbnail((618, 618))
      im.convert('RGB').save(dst, 'JPEG', quality=80)
      print(dst, os.path.getsize(dst) // 1024, 'KB')
  EOF
  ```

- 需读图内文字、核对数值时，对**原图局部区域**裁剪后单独放大读取。
- 查原图尺寸用 `ls -l` 或 `python3 -c "from PIL import Image; print(Image.open(p).size)"`，不要直接 read 猜测。

## MCP 进程与重连（`/mcps` + 空格）

- 本项目 MCP 定义在项目文件 `opencode.json`（`mcp.servers.loveplus-emu`，command 指向 `scripts/loveplus/run_mcp.sh`）。`.py` 在进程启动时已加载进内存，**改文件不影响运行中的进程**，必须让进程重启。
- 手动操作：`/mcps` 打开 MCP 服务器对话框 → 选中 `loveplus-emu` → 按**空格**。键位 ID `dialog.mcp.toggle`，官方默认值 `space`；`mcp.list` 默认 `none`，"打开对话框"只能靠 `/mcps`。
- **opencode 的自动重连只覆盖"会话过期"（`MCP.SessionExpiredError`），不覆盖进程退出**。kill 的是 stdio 子进程，属连接关闭，不走该分支；进程退出后**必须由人在对话框 toggle**（`/mcps` + 空格）才能恢复。
- HTTP API 自动 connect 走不通：后台服务 location 锁死，`GET /api/mcp` 返回 `data:[]`，`POST /api/experimental/mcp/{server}/connect` 报 `McpServerNotFoundError`；`--standalone` 起的是新的私有服务，与当前会话无关。
- **状态检查用 `opencode mcp list`**（权威：✓ connected / ✗ failed），不要靠 `pgrep` 猜 PID。辅助脚本 `scripts/loveplus/restart_mcp.sh` 只负责安全 kill。
- 坑：勿用 `pkill -f loveplus_mcp.py`——会匹配到执行它的 shell 自身并自杀（`Killed by SIGTERM`）；只匹配 `\.venv/bin/python .*loveplus_mcp\.py`。
- 同类坑：`pgrep -f` / `ps -f` 也会匹配到跑该命令的 shell 自身。安全写法：
  `pids=$(ps -eo pid,args | awk '/<模式>/ && !/awk/ {print $1}')`，模式用正则转义，并始终排除 `awk` 自身。
- 验证生效：toggle 后 `opencode mcp list` 显示 ✓ connected，且 `frame()` 返回递增帧号。

## 后台任务按寿命选挂法

- **短任务（会话期间能跑完）**：用工具 `background=true`（返回 shell ID、输出流式落盘，**结束时自动通知主 agent**）。能用就用。
- **长任务（可能跨会话重启，如数小时的同步/下载）**：用 `setsid nohup bash script.sh >/tmp/x.out 2>&1 </dev/null &` 彻底脱离会话。代价是**没有完成通知**，必须自己 `tail` 日志轮询。
- 依据：`background=true` 挂的进程是 opencode 服务的子进程，**会话重启时随进程组一起收到 SIGTERM/SIGHUP 被杀**（实测 rsync 跑 6 小时后进度停在 65%）。`setsid` 使进程自建会话（免疫 SIGHUP），父进程重挂到 `/init`（实测会话重启后仍在运行）。
- **共同前提：脚本必须可被 kill 后重跑并续传**（rsync `--partial --partial-dir`、`aqt -k` 保留压缩包），否则"重试"等于从头再来。
- **不要用裸 `nohup cmd &` / `&` / `disown`**：曾出现假后台（进程随 shell 退出，或 pgrep 查不到）。要脱离就写完整的 `setsid nohup ... </dev/null` 形式，并 `ps -o pid,ppid,sid,args` 确认 `ppid=/init` 且 `sid` 自成一列后再离开。
- `subagent` 工具支持 `background=true` 异步执行、完成后自动通知主 agent；`opencode` CLI 无 subagent 子命令、`run --agent` 仅前台，需要后台子任务时用内置工具。

## Code Mode（`execute` 调 MCP）

- 交互脚本优先用 `execute`（Code Mode）调 MCP 工具：在 Code Mode runtime 里用 `tools.<namespace>["tool-name"](input)` 直接调 MCP 工具、串联多步并 `Promise.all` 并发，不必为每个小操作写 .py 脚本落盘。
- 适用范围：简单前台编排（sleep → 截图 → 触摸 → 再截图）。仍写脚本的情况：复杂状态机、循环监控、后台常驻。
- Code Mode 内**只能用 catalog 里列出的工具**，忽略 catalog 外的；无 `fetch` 之外的**文件系统直访**，图片一律先落盘再 `read`。
- 调 MCP 时工具名按 catalog 的**完整路径 + 精确签名**，不要改写/归一化。

## 细小元素识别受阻时：停下提问

- 连续 2 次定位/识别失败即停下，把卡点讲清楚（元素多大、试了什么、为什么失败），由用户给方案，不要无限盲试。
- 方案常在用户手里；用户的 CV 投影思路（多通道、横/纵方向对 dark 像素求投影曲线，按跳变定位行列边界坐标，再切割逐格识别）优先于继续肉眼估读。

## 已有资料指针

- `memory/loveplus/headless_azahar.md`：无头环境、交互式控制通道、坐标与长按实测。
- `memory/loveplus/touch_coords_nlpplus.md`：NLP+ 触摸坐标表与验证状态。
- `scripts/loveplus/SCRIPTS.md`：脚本索引、坐标体系、常见坑速查。
