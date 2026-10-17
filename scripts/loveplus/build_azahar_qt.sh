#!/usr/bin/env bash
# build_azahar_qt.sh —— 本机编译「带 Qt UI」的 azahar（仅本机 WSL 副本需要）
#
# 配方基线：memory/loveplus/headless_azahar.md 里远端实机验证过的无头版参数，
# 这里只把 UI 相关开关翻过来，其余原样照抄（含 CITRA_WARNINGS_AS_ERRORS=OFF、
# CITRA_USE_PRECOMPILED_HEADERS=OFF —— 远端也是显式关掉，否则换编译器必炸）。
#
# 前提：
#   1. Qt 6.10.3 已由 scripts/loveplus/fetch_qt.sh 下到 tools/azahar/build_qt/externals/qt
#   2. 系统装有 libsdl2-dev / libasound2-dev / libpulse-dev / pkg-config
#
# 用法：
#   bash scripts/loveplus/build_azahar_qt.sh configure   # 只 configure
#   bash scripts/loveplus/build_azahar_qt.sh             # configure + make -j
#   setsid nohup bash scripts/loveplus/build_azahar_qt.sh \
#       >/tmp/opencode/build_qt.log 2>&1 </dev/null &   # 长时间编译挂后台
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
if [ -f "$ROOT/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  . "$ROOT/.env"
  set +a
fi

REPO="${LOVEPLUS_REPO:-$ROOT}"
SRC="$REPO/tools/azahar"
BUILD="${BUILD_DIR:-$SRC/build_qt}"
QT_PREFIX="$BUILD/externals/qt/6.10.3/gcc_64"
JOBS="${JOBS:-$(nproc)}"

if [ ! -f "$QT_PREFIX/lib/cmake/Qt6/Qt6Config.cmake" ]; then
  echo "找不到 Qt：$QT_PREFIX/lib/cmake/Qt6/Qt6Config.cmake"
  echo "先跑 scripts/loveplus/fetch_qt.sh"
  exit 1
fi

# 编译器：azahar 的 Qt 前端用了 `#include <format>`，而 libstdc++ 12 没有 <format>
# （GCC 13 才引入）；本机系统只装了 g++-12，故默认优先 g++-13（远端 tx-new 是 13.3）。
#   装法：sudo apt install -y g++-13 gcc-13
CC_BIN="${CC_BIN:-$(command -v gcc-13 || command -v gcc)}"
CXX_BIN="${CXX_BIN:-$(command -v g++-13 || command -v g++)}"
CXX_MAJOR="$("$CXX_BIN" -dumpversion 2>/dev/null | cut -d. -f1)"
echo "[compiler] C=$CC_BIN  CXX=$CXX_BIN (GCC ${CXX_MAJOR:-?})"
if [ "${CXX_MAJOR:-0}" -lt 13 ]; then
  echo "警告：GCC ${CXX_MAJOR} 编不了 Qt UI（缺 <format>），只能 -DENABLE_QT=OFF 编无头目标"
fi

echo "[configure] $BUILD   (Qt: $QT_PREFIX)"
cmake -S "$SRC" -B "$BUILD" -G "Unix Makefiles" \
  -DCMAKE_C_COMPILER="$CC_BIN" -DCMAKE_CXX_COMPILER="$CXX_BIN" \
  -DCMAKE_BUILD_TYPE=Release \
  -DUSE_SYSTEM_QT=ON -DCMAKE_PREFIX_PATH="$QT_PREFIX" \
  -DENABLE_QT=ON -DENABLE_QT_TRANSLATION=ON -DENABLE_QT_UPDATE_CHECKER=OFF \
  -DENABLE_SDL2=ON -DUSE_SYSTEM_SDL2=ON \
  -DENABLE_VULKAN=ON -DENABLE_OPENGL=OFF -DENABLE_SOFTWARE_RENDERER=ON \
  -DENABLE_WEB_SERVICE=OFF -DENABLE_SCRIPTING=OFF -DENABLE_GDBSTUB=ON \
  -DENABLE_CUBEB=OFF -DENABLE_OPENAL=OFF -DENABLE_LIBUSB=OFF \
  -DENABLE_ROOM=OFF -DENABLE_TESTS=OFF -DENABLE_DISCORD_RPC=OFF \
  -DENABLE_FFMPEG=OFF -DENABLE_LTO=OFF \
  -DCITRA_WARNINGS_AS_ERRORS=OFF -DCITRA_USE_PRECOMPILED_HEADERS=OFF
rc=$?
[ "$rc" -eq 0 ] || { echo "configure 失败（退出码 $rc）"; exit "$rc"; }

if [ "${1:-}" = "configure" ]; then
  echo "[configure] 完成；未编译（传 configure 只做配置）"
  exit 0
fi

echo "[build] make -j$JOBS"
cmake --build "$BUILD" -j"$JOBS"
rc=$?
if [ "$rc" -eq 0 ]; then
  echo "[build] 成功。产物:"
  ls -1 "$BUILD/bin/Release/" 2>/dev/null | sed 's/^/  /'
  echo "  运行（WSLg 走 Wayland）：QT_QPA_PLATFORM=wayland $BUILD/bin/Release/azahar"
else
  echo "[build] 失败（退出码 $rc）"
fi
exit "$rc"
