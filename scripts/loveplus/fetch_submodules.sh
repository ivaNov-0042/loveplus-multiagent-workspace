#!/bin/bash
# 逐个拉取缺失的 azahar 子模块并检出工作树（网络不稳定，带重试）。
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="${LOVEPLUS_REPO:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
if [ -f "$REPO/.env" ]; then set -a; . "$REPO/.env"; set +a; fi
cd "${LOVEPLUS_REPO:-$REPO}/tools/azahar"

# 名字 -> (path, url)  仅列无头构建需要的；其余 QT/GL/Vulkan/Android 相关跳过
declare -A URLS=(
  [soundtouch]="https://github.com/azahar-emu/soundtouch.git externals/soundtouch"
  [teakra]="https://github.com/wwylele/teakra.git externals/teakra"
  [lodepng]="https://github.com/lvandeve/lodepng.git externals/lodepng/lodepng"
  [nihstro]="https://github.com/neobrain/nihstro.git externals/nihstro"
  [xbyak]="https://github.com/herumi/xbyak.git externals/xbyak"
  [zstd]="https://github.com/facebook/zstd.git externals/zstd"
  [xxHash]="https://github.com/Cyan4973/xxHash.git externals/xxHash"
  [microtar]="https://github.com/azahar-emu/microtar externals/microtar"
  [vma]="https://github.com/GPUOpen-LibrariesAndSDKs/VulkanMemoryAllocator externals/vma"
  [sirit]="https://github.com/azahar-emu/sirit.git externals/sirit/sirit"
  [enet]="https://github.com/lsalzman/enet.git externals/enet"
)

fetch_one() {
  local name="$1" url="$2" path="$3"
  local commit
  commit=$(git ls-tree HEAD "$path" 2>/dev/null | awk '{print $3}')
  echo "== $name -> $path (want ${commit:0:12}) =="
  for attempt in 1 2 3 4 5; do
    if [ ! -d "$path/.git" ] && [ ! -f "$path/.git" ]; then
      git clone --no-checkout --depth 1 "$url" "$path" >/dev/null 2>&1 || { echo "  clone attempt $attempt failed"; sleep 2; continue; }
      # 将工作目录 gitdir 指向模块目录
      rm -rf ".git/modules/$name" 2>/dev/null
      mkdir -p ".git/modules/$(dirname $name)"
      mv "$path/.git" ".git/modules/$name" 2>/dev/null
      echo "gitdir: $(python3 -c "import os;print(os.path.relpath('.git/modules/$name','$path'))")" > "$path/.git"
    fi
    # 尝试取到目标 commit
    if [ -n "$commit" ] && ! git --git-dir=".git/modules/$name" cat-file -e "$commit^{commit}" 2>/dev/null; then
      git --git-dir=".git/modules/$name" fetch --depth 1 origin "$commit" >/dev/null 2>&1 || { echo "  fetch attempt $attempt failed"; sleep 2; continue; }
      git --git-dir=".git/modules/$name" reset --soft "$commit" >/dev/null 2>&1
    fi
    git --git-dir=".git/modules/$name" --work-tree="$path" checkout -f >/dev/null 2>&1
    local n
    n=$(find "$path" -type f 2>/dev/null | grep -v '/\.git/' | wc -l)
    if [ "$n" -gt 2 ]; then echo "  OK files=$n"; return 0; fi
    echo "  checkout attempt $attempt produced $n files"
    sleep 2
  done
  echo "  FAILED $name"
  return 1
}

for name in "${!URLS[@]}"; do
  set -- ${URLS[$name]}
  fetch_one "$name" "$1" "$2" || true
done
