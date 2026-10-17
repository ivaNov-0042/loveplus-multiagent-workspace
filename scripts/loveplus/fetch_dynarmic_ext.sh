#!/bin/bash
# 拉取 dynarmic 的嵌套子模块(biscuit/mcl/robin-map/xbyak/oaknut/zydis/zycore)。
set -u
DY="<repo>/tools/azahar/externals/dynarmic"
GD="<repo>/tools/azahar/.git/modules/dynarmic"

declare -A U=(
  [biscuit]="https://github.com/lioncash/biscuit.git"
  [mcl]="https://github.com/azahar-emu/mcl.git"
  [robin-map]="https://github.com/Tessil/robin-map.git"
  [xbyak]="https://github.com/herumi/xbyak.git"
  [oaknut]="https://github.com/merryhime/oaknut.git"
  [zydis]="https://github.com/zyantific/zydis.git"
  [zycore]="https://github.com/zyantific/zycore-c.git"
)

for name in biscuit mcl robin-map xbyak oaknut zydis zycore; do
  url="${U[$name]}"
  abs="$DY/externals/$name"
  pin=$(git --git-dir="$GD" ls-tree HEAD "externals/$name" 2>/dev/null | awk '{print $3}')
  echo "== $name (pin ${pin:0:12}) =="
  if [ ! -e "$abs/.git" ]; then
    for a in 1 2 3 4 5; do
      rm -rf "$abs"; mkdir -p "$abs"
      git clone --no-checkout --depth 1 "$url" "$abs" >/dev/null 2>&1 && break
      echo "  clone retry $a"; sleep 2
    done
  fi
  [ -e "$abs/.git" ] || { echo "  FAILED"; continue; }
  if [ -n "$pin" ] && ! git --git-dir="$abs/.git" cat-file -e "$pin^{commit}" 2>/dev/null; then
    for a in 1 2 3 4 5; do
      git --git-dir="$abs/.git" fetch --depth 1 origin "$pin" >/dev/null 2>&1 && break
      echo "  fetch retry $a"; sleep 2
    done
    git --git-dir="$abs/.git" reset --soft "$pin" >/dev/null 2>&1
  fi
  git --git-dir="$abs/.git" --work-tree="$abs" checkout -f >/dev/null 2>&1
  echo "  files=$(find "$abs" -type f 2>/dev/null | grep -v '/\.git' | wc -l)"
done
echo "DONE"
