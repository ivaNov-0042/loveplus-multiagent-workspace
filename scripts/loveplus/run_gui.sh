#!/bin/bash
# 启动 GUI（Qt）版 azahar（带实时控制通道）。
#
# 显示配置（2026-10-17 实测，详见 memory/others/diary/2026-10-17_02_static-re.md 第十二～十四节）：
#   WSL 的 GPU 图形路径不可靠，三种组合的实测结果：
#     - Vulkan 渲染器            → 呈现时 `D3D12: Removing Device.`，画面冻结在 ~94 帧；
#     - OpenGL 渲染器 + GPU GL   → 彩色噪点 / 完全乱码（EGL-on-d3d12 路径）；
#     - OpenGL 渲染器 + LIBGL_ALWAYS_SOFTWARE=1（llvmpipe 渲染、由 Weston 呈现）
#                                → 画面正确、不卡 —— 本机选定配置。
#   注意：GPU 的 Vulkan 与 GL 坏的是同一条"WSL 呈现/共享"路（dzn 自身核心经探针验证正常，
#   scripts/loveplus/vk_submit_probe.c）；故不要改回 GPU GL，会花屏。
#
# 用法：
#   setsid bash run_gui.sh > /tmp/ui_gui.log 2>&1 < /dev/null &   # 后台（推荐）
#   bash run_gui.sh                                               # 前台
#   AZAHAR_GRAPHICS_API=Software bash run_gui.sh                  # 临时换渲染器
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="${LOVEPLUS_REPO:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
if [ -f "$REPO/.env" ]; then set -a; . "$REPO/.env"; set +a; fi
REPO="${LOVEPLUS_REPO:-$REPO}"
BIN="${AZAHAR_QT:-$REPO/tools/azahar/build_qt/bin/Release/azahar}"

# 2026-10-17 迁移到 tools/ 后，二进制的 RUNPATH 仍钉着旧目录
#（/…/azahar/build_qt/externals/qt/6.10.3/gcc_64/lib）；本机无 patchelf，
# 用 LD_LIBRARY_PATH 补（ELF 规范中 RUNPATH 的搜索顺序在 LD_LIBRARY_PATH 之后）。
QT_LIB="$REPO/tools/azahar/build_qt/externals/qt/6.10.3/gcc_64/lib"
if [ -d "$QT_LIB" ]; then
  export LD_LIBRARY_PATH="$QT_LIB${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
fi
ROM="${NLP_PLUS_ROM:-$REPO/data/loveplus/roms_patched/NLP_plus_patched.3ds}"

export LIBGL_ALWAYS_SOFTWARE="${LIBGL_ALWAYS_SOFTWARE:-1}"
export AZAHAR_GRAPHICS_API="${AZAHAR_GRAPHICS_API:-OpenGL}"
export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-wayland}"
export DISPLAY="${DISPLAY:-:0}"
export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-0}"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"

echo "[run_gui] bin=$BIN"
echo "[run_gui] renderer=$AZAHAR_GRAPHICS_API  LIBGL_ALWAYS_SOFTWARE=$LIBGL_ALWAYS_SOFTWARE"
echo "[run_gui] QT_QPA_PLATFORM=$QT_QPA_PLATFORM  WAYLAND_DISPLAY=$WAYLAND_DISPLAY"

cd "$REPO"
"$BIN" "$ROM" &
PID=$!
echo "$PID" > /tmp/ui_gui.pid
wait "$PID"
