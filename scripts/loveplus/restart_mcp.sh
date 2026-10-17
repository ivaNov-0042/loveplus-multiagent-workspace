#!/bin/bash
# 重启 loveplus-emu MCP 服务（改完 loveplus_mcp.py 后让新代码生效）。
#
# 【重要事实（2026-10-16 实测）】OpenCode V2 的本地 stdio MCP **不会自动重连**：
#   - .py 在进程启动时已加载进内存，改文件不影响运行中的进程，必须杀进程；
#   - 杀掉进程后 opencode **不会**自动重新拉起（实测等待 20s 无新进程，
#     且此期间调用工具报 "Unknown tool"）；
#   - 必须由用户在 opencode 界面手动触发重连：按**空格**，或用 `/mcps` 断开再连接。
# 之前观察到的"新 PID"其实是用户手动重连的结果，不是自动行为。
#
# 因此本脚本只做一件事：安全地杀掉旧 MCP 进程，然后提示你去界面手动重连。
#
# 坑：不要用 `pkill -f loveplus_mcp.py`——该模式会匹配到执行这条命令的 shell 自身，
# 导致 shell 被自己杀掉（返回 "Killed by SIGTERM"）。这里用只匹配 venv python 的模式。
#
# 用法: bash scripts/loveplus/restart_mcp.sh
set -u

PAT='\.venv/bin/python .*loveplus_mcp\.py'
old=$(pgrep -f "$PAT" | tr '\n' ' ')

if [ -z "$old" ]; then
  echo "未发现运行中的 MCP 进程（已是断开态）。"
else
  echo "kill 旧 MCP: $old"
  # shellcheck disable=SC2086
  kill $old 2>/dev/null || true
  sleep 1
  left=$(pgrep -f "$PAT" | tr '\n' ' ')
  echo "剩余进程: ${left:-（无，已全部退出）}"
fi

echo
echo "=== 请手动重连 ==="
echo "opencode 不会自动重连本地 stdio MCP。请在界面："
echo "  1) 按【空格】重启 MCP 服务；或"
echo "  2) 输入 /mcps → 选 loveplus-emu → 断开后再连接。"
echo
echo "验证：重连后 tools[\"loveplus-emu\"] 应重新出现 screenshot/touch/frame 等工具，"
echo "      且调用 frame() 能返回递增帧号。"
