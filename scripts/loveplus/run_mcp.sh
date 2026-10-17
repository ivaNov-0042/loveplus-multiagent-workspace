#!/bin/bash
# 以项目 venv 启动 LovePlus+ 模拟器 MCP 服务（stdio 传输）。
# 让 .mcp.json 指向此脚本，客户端即可自动发现并调用工具。
set -euo pipefail
# 从项目根 .env 载入本地路径（不写死机器目录）；缺失时退回脚本位置推导。
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="${LOVEPLUS_REPO:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
if [ -f "$REPO/.env" ]; then set -a; . "$REPO/.env"; set +a; fi
REPO="${LOVEPLUS_REPO:-$REPO}"
cd "$REPO"
exec "$REPO/.venv/bin/python" "$REPO/scripts/loveplus/loveplus_mcp.py"
