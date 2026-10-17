#!/bin/bash
# 后台启动无头 azahar（带实时控制通道）。写 pid 到 /tmp/emu.pid 便于停止。
# 用法: setsid bash run_emu.sh > /tmp/emu_live.log 2>&1 < /dev/null &
set -u
# 从项目根 .env 载入本地路径（不写死机器目录）；缺失时退回脚本位置推导。
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="${LOVEPLUS_REPO:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
if [ -f "$REPO/.env" ]; then set -a; . "$REPO/.env"; set +a; fi
REPO="${LOVEPLUS_REPO:-$REPO}"
BIN="${AZAHAR_HEADLESS:-$REPO/tools/azahar/build_headless/bin/Release/azahar_headless}"
ROM="${NLP_PLUS_ROM:-$REPO/data/loveplus/roms_patched/NLP_plus_patched.3ds}"
DUMP_PREFIX="${EMU_DUMP_PREFIX:-/tmp/az_live}"
cd "$REPO"
# 不传 --frames => 默认 -1（无限运行）。注意: --frames 0 会因 `0>=0` 判定而立刻退出, 切勿用 0。
"$BIN" "$ROM" --live-port "${EMU_LIVE_PORT:-24777}" --dump-prefix "$DUMP_PREFIX" &
EMU_PID=$!
echo "$EMU_PID" > /tmp/emu.pid
wait "$EMU_PID"
