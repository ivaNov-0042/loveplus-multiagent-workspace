#!/bin/bash
# 通用递归子模块拉取：读取 <repo>/.gitmodules，对每个 path 拉取并检出到 pin commit。
# 处理 azahar 网络不稳（TLS 抖动）与 --no-checkout 未检出工作树的问题。
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="${LOVEPLUS_REPO:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
if [ -f "$REPO/.env" ]; then set -a; . "$REPO/.env"; set +a; fi
ROOT="${LOVEPLUS_REPO:-$REPO}/tools/azahar"
MAXDEPTH="${1:-3}"

fetch_repo() {
  local repo="$1"; local depth="$2"
  [ "$depth" -gt "$MAXDEPTH" ] && return 0
  local gm="$repo/.gitmodules"
  [ -f "$gm" ] || return 0

  # 解析 .gitmodules
  local paths urls
  paths=$(git config -f "$gm" --get-regexp '^submodule\..*\.path$' 2>/dev/null | awk '{print $2}')
  for relpath in $paths; do
    local url
    url=$(git config -f "$gm" --get-regexp '^submodule\..*\.path$' >/dev/null 2>&1; \
          git config -f "$gm" --get-regexp '^submodule\..*\.url$' 2>/dev/null | awk '{print $2}' | head -1)
    # 更稳妥：按 path 找对应 url
    url=$(awk -v p="$relpath" '
      /^\[submodule /{name=$0}
      /path = /{path=$3}
      /url = /{url=$3}
      {if(path==p){print url; exit}}
    ' "$gm")
    [ -z "$url" ] && continue

    local abs="$repo/$relpath"
    local modname
    modname=$(echo "$repo/${relpath}" | sed 's|/|_|g')

    if [ ! -e "$abs/.git" ] && [ ! -d "$abs/.git" ]; then
      echo "  [$depth] missing: $relpath"
      # 目标 pin commit
      local pin
      pin=$(git -C "$repo" ls-tree HEAD "$relpath" 2>/dev/null | awk '{print $3}')
      [ -z "$pin" ] && pin=$(git --git-dir="$repo/.git" ls-tree HEAD "$relpath" 2>/dev/null | awk '{print $3}')
      for a in 1 2 3 4 5; do
        mkdir -p "$abs"
        if git clone --no-checkout --depth 1 "$url" "$abs" >/dev/null 2>&1; then break; fi
        sleep 2
      done
      [ -e "$abs/.git" ] || { echo "    clone FAILED $relpath"; continue; }
    fi
    # 确保能取到 pin
    local pin
    pin=$(git -C "$repo" ls-tree HEAD "$relpath" 2>/dev/null | awk '{print $3}')
    if [ -n "$pin" ]; then
      local gd="$abs/.git"
      if ! git --git-dir="$gd" cat-file -e "$pin^{commit}" 2>/dev/null; then
        for a in 1 2 3 4 5; do
          git --git-dir="$gd" fetch --depth 1 origin "$pin" >/dev/null 2>&1 && break
          sleep 2
        done
        git --git-dir="$gd" reset --soft "$pin" >/dev/null 2>&1
      fi
    fi
    git --git-dir="$abs/.git" --work-tree="$abs" checkout -f >/dev/null 2>&1
    local n
    n=$(find "$abs" -type f 2>/dev/null | grep -v '/\.git' | wc -l)
    echo "    checkout $relpath -> $n files"

    # 递归
    fetch_repo "$abs" $((depth+1))
  done
}

echo "== fetching nested submodules of $ROOT =="
fetch_repo "$ROOT" 1
echo "== done =="
