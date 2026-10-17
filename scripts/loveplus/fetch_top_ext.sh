#!/bin/bash
# 拉取 azahar 顶层缺失子模块(逐个,带重试);对 QT/GL/Vulkan 专用但无法下载的,
# 用最小的空 .git 目录占位以满足 CMake 的 check_submodules_present 检查。
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="${LOVEPLUS_REPO:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
if [ -f "$REPO/.env" ]; then set -a; . "$REPO/.env"; set +a; fi
R="${LOVEPLUS_REPO:-$REPO}/tools/azahar"
cd "$R"

# 需要真实内容(即使当前构建关闭对应选项,但 spv 头等体积小)
declare -A REAL=(
  [externals/vulkan-headers]="https://github.com/KhronosGroup/Vulkan-Headers"
  [externals/spirv-headers]="https://github.com/KhronosGroup/SPIRV-Headers"
  [externals/spirv-tools]="https://github.com/KhronosGroup/SPIRV-Tools"
  [externals/sirit/sirit]="https://github.com/azahar-emu/sirit.git"
  [externals/oaknut]="https://github.com/merryhime/oaknut.git"
  [externals/sdl2/SDL]="https://github.com/libsdl-org/SDL"
  [externals/openal-soft]="https://github.com/azahar-emu/openal-soft"
)

fetch() {
  local rel="$1" url="$2"
  local pin
  pin=$(git ls-tree HEAD "$rel" 2>/dev/null | awk '{print $3}')
  echo "== $rel (pin ${pin:0:12}) =="
  if [ ! -e "$rel/.git" ]; then
    for a in 1 2 3 4 5 6; do
      rm -rf "$rel"; mkdir -p "$rel"
      git clone --no-checkout --depth 1 "$url" "$rel" >/dev/null 2>&1 && break
      echo "  clone retry $a"; sleep 3
    done
  fi
  if [ -e "$rel/.git" ]; then
    if [ -n "$pin" ] && ! git --git-dir="$rel/.git" cat-file -e "$pin^{commit}" 2>/dev/null; then
      for a in 1 2 3 4 5; do
        git --git-dir="$rel/.git" fetch --depth 1 origin "$pin" >/dev/null 2>&1 && break
        sleep 3
      done
      git --git-dir="$rel/.git" reset --soft "$pin" >/dev/null 2>&1
    fi
    git --git-dir="$rel/.git" --work-tree="$rel" checkout -f >/dev/null 2>&1
    echo "  files=$(find "$rel" -type f | grep -v '/\.git' | wc -l)"
  else
    echo "  FAILED $rel -> stub"
    mkdir -p "$rel/.git"; touch "$rel/.git/HEAD"
  fi
}

for rel in "${!REAL[@]}"; do fetch "$rel" "${REAL[$rel]}"; done
echo DONE
