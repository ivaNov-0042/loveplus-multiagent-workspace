#!/usr/bin/env bash
# fetch_qt.sh —— 预下载 Qt 6.10.3 到 tools/azahar/build_qt/externals/qt（本机 UI 构建用）
#
# 为什么不交给 azahar 自己下：tools/azahar/CMakeModules/DownloadExternals.cmake +
# aqt_config.ini 会把国内镜像列进 blacklist，且它按 "linux" 拼解包目录名（实际是
# gcc_64）。自己下好再用 -DUSE_SYSTEM_QT=ON -DCMAKE_PREFIX_PATH=<qt>/6.10.3/gcc_64
# 让 azahar 直接用，最省事。
#
# 依赖：仓库 .venv 里装了 aqtinstall==3.3.0（requirements 未含，需单独装）。
# 镜像与坑见同目录 aqt_mirror.ini 的注释。
#
# 用法（长任务，务必 setsid 脱离会话）：
#   setsid nohup bash scripts/loveplus/fetch_qt.sh \
#       >/tmp/opencode/qt-fetch.out 2>&1 </dev/null &
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
PY="$REPO/.venv/bin/python"
INI="$HERE/aqt_mirror.ini"
QT_VERSION=6.10.3
# aqt 的「包名」是 linux_gcc_64，但解包后的目录名是 gcc_64 —— CMAKE_PREFIX_PATH 要指向后者
QT_ARCH=linux_gcc_64
QT_OUT="${QT_OUT:-$REPO/tools/azahar/build_qt/externals/qt}"
# 硬超时：曾出现 worker 无限卡在 SYN-SENT（TCP 握手被黑洞），靠 timeout 兜住整次尝试
ATTEMPT_TIMEOUT="${ATTEMPT_TIMEOUT:-900}"
ATTEMPTS="${QT_ATTEMPTS:-15}"

[ -x "$PY" ] || { echo "缺少 $PY（先重建 .venv）"; exit 1; }
"$PY" -c "import aqt" 2>/dev/null || { echo "venv 里没有 aqtinstall：$PY -m pip install aqtinstall==3.3.0"; exit 1; }

# 历史教训：aqt 默认 --timeout 只有 5 秒，下载大包必读超时，故显式放大
AQT_ARGS=(-c "$INI" install-qt
  --outputdir "$QT_OUT" --timeout 90
  linux desktop "$QT_VERSION" "$QT_ARCH"
  -m qtmultimedia
  --archives icu qtbase qtdeclarative qtsvg qttools qttranslations qtwayland
  -k)   # -k 保留 .7z 于当前目录，重试不必重下已完成的包

# -k 把 .7z 留在当前目录，故切到一个仓库外的目录，避免污染仓库
ARCHIVE_DIR="${QT_ARCHIVE_DIR:-/tmp/opencode/qt_archives}"
mkdir -p "$ARCHIVE_DIR" "$QT_OUT" || exit 1
cd "$ARCHIVE_DIR" || exit 1
for i in $(seq 1 "$ATTEMPTS"); do
  echo "=== qt attempt $i start $(date '+%F %T') ==="
  timeout "$ATTEMPT_TIMEOUT" "$PY" -m aqt "${AQT_ARGS[@]}"
  rc=$?
  echo "=== qt attempt $i exit=$rc at $(date '+%F %T') ==="
  if [ "$rc" -eq 0 ]; then
    echo "=== QT FETCH COMPLETE $(date '+%F %T') ==="
    echo "    解包根: $QT_OUT/$QT_VERSION/gcc_64"
    exit 0
  fi
  sleep 10
done
echo "=== QT FETCH GAVE UP $(date '+%F %T') ==="
exit 1
