#!/usr/bin/env bash
# 编译安装 r2ghidra（r2 的 Ghidra 反编译器插件，提供 pdg）。
#
# 踩过的坑（都在这脚本里解决）：
#  1) master 与 r2 6.0.7 不兼容（r2 API/ABI 都变了）；release 的 amd64.deb 插件是 ABI 14，
#     本机 r2 是 ABI 39 → 装上也 Warning 后不工作。必须 checkout 与 r2 同版本的 tag。
#  2) tag 的 subprojects 依赖由 acr-wrap 自动 git clone，且 `git fetch --depth=1 origin <rev>`
#     （未通告对象）会卡死；github 直连本机间歇超时。→ 用镜像前缀自行备依赖。
#  3) pugixml 的 revision 写成 tag 名 v1.15，而 mk 里用 `git rev-parse HEAD`（SHA）比较
#     → 永远不等 → 每次 make 都 rm -rf 重拉。→ 打桩 *.mk 成 no-op，杜绝构建期联网。
#  4) 打桩会连带去掉依赖的补丁步骤（ghidra-native 的 getLanguageDescriptions 就是补丁 0002
#     加进去的，不应用就编不过）→ 本脚本按 WRAP_wrap_git_diff_files 自行 patch -p1。
#
# 用法：build_r2ghidra.sh [logfile]      默认 /tmp/r2ghidra_build2.log
# 后台：setsid nohup scripts/loveplus/build_r2ghidra.sh >/dev/null 2>&1 </dev/null &
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
set -a; . "$HERE/../../.env" 2>/dev/null; set +a
REPO="${LOVEPLUS_REPO:-$(cd "$HERE/../.." && pwd)}"

LOG="${1:-/tmp/02_static-re/r2ghidra_build.log}"
SRC="${R2PM_GITDIR:-$HOME/.local/share/radare2/r2pm/git}/r2ghidra"
TAG="${R2G_TAG:-6.0.7}"
R2G_SRC_URL="${R2G_SRC_URL:-https://ghfast.top/https://github.com/radareorg/r2ghidra}"
export PATH="$REPO/.venv/bin:$PATH"

PREFIXES="https://ghfast.top/ https://gitclone.com/ https://gh-proxy.com/"

log() { echo "[$(date +%H:%M:%S)] $*" >>"$LOG"; }

mirror_urls() {
    local gh="$1"
    echo "$gh"
    for p in $PREFIXES; do
        case "$p" in
            https://gitclone.com/) echo "${p}github.com/${gh#https://github.com/}" ;;
            *) echo "${p}${gh}" ;;
        esac
    done
}

# 备好 wrap 依赖：$1=目录名 $2=github url $3=revision(sha 或 tag)
prepare_dep() {
    local dir="$1" url="$2" rev="$3" mp d want
    d="$SRC/subprojects/$dir"
    want=$(git -C "$d" rev-parse -q --verify "${rev}^{commit}" 2>/dev/null) || want=""
    if [ -d "$d" ] && [ -n "$want" ] && [ "$(git -C "$d" rev-parse HEAD 2>/dev/null)" = "$want" ]; then
        log "   $dir 已就位（$(git -C "$d" describe --tags 2>/dev/null || echo "$want")）"; return 0
    fi
    for round in 1 2 3; do
        for mp in $(mirror_urls "$url"); do
            rm -rf "$d"
            log "   $dir 尝试 round=$round $mp"
            if timeout 420 git clone -q "$mp" "$d" 2>>"$LOG" \
               && git -C "$d" rev-parse -q --verify "${rev}^{commit}" >/dev/null 2>&1 \
               && git -C "$d" checkout -q "$rev" \
               && cp -rf "$SRC/subprojects/packagefiles/$dir/"* "$d" 2>/dev/null; then
                log "   $dir OK（$(git -C "$d" rev-parse --short HEAD)）"; return 0
            fi
        done
        sleep 5
    done
    log "   依赖 $dir 准备失败"; return 1
}

# 应用 wrap 声明的补丁（幂等：用 .patches_ok 标记）
apply_patches() {
    local dir="$1" files="$2" d f
    d="$SRC/subprojects/$dir"
    [ -f "$d/.patches_ok" ] && { log "   $dir 补丁已应用"; return 0; }
    local IFS=','
    for f in $files; do
        [ -f "$SRC/subprojects/$f" ] || continue
        patch -s -d "$d" -p1 <"$SRC/subprojects/$f" >>"$LOG" 2>&1 \
            || log "   ! 补丁失败：$f（继续）"
    done
    unset IFS
    touch "$d/.patches_ok"
    log "   $dir 补丁应用完成"
}

mkdir -p "$(dirname "$LOG")"
log "==== 开始 tag=$TAG 源码=$SRC ===="

# ---- 0/4 checkout 与 r2 同版本的 tag ----
cd "$SRC" || { log "源码目录不存在（先跑 r2pm -U / r2pm -s）"; exit 1; }
if [ "$(git describe --tags 2>/dev/null)" != "$TAG" ]; then
    log "== 0/4 fetch+checkout tag $TAG =="
    git fetch -q --depth=1 "$R2G_SRC_URL" "refs/tags/$TAG:refs/tags/$TAG" >>"$LOG" 2>&1 \
      || { log "tag fetch 失败"; exit 1; }
    git checkout -q "$TAG" >>"$LOG" 2>&1 || { log "checkout 失败"; exit 1; }
fi
log "当前版本：$(git describe --tags 2>/dev/null)"

# ---- 1/4 备依赖（解析各 *.mk）+ 2/4 应用其自身携带的补丁 ----
log "== 1/4 备 subprojects 依赖 =="
cd "$SRC/subprojects" || exit 1
git checkout -q -- '*.mk' 2>/dev/null || true      # 恢复被上次打桩的 mk，拿回 WRAP_* 变量
declare -A DIFFS
for mk in *.mk; do
    name="$(basename "$mk" .mk)"
    dir=$(sed -n 's/^WRAP_wrap_git_directory:=//p' "$mk")
    url=$(sed -n 's/^WRAP_wrap_git_url:=//p' "$mk")
    rev=$(sed -n 's/^WRAP_wrap_git_revision:=//p' "$mk")
    dfs=$(sed -n 's/^WRAP_wrap_git_diff_files:=//p' "$mk")
    [ -n "$dir" ] && [ -n "$url" ] && [ -n "$rev" ] || continue
    prepare_dep "$dir" "$url" "$rev" || exit 1
    [ -n "$dfs" ] && { log "== 2/4 应用 $dir 补丁 =="; apply_patches "$dir" "$dfs"; }
done

# ---- 3/4 打桩 *.mk，防构建期联网重拉 ----
log "== 3/4 打桩 subprojects/*.mk =="
for mk in *.mk; do
    name="$(basename "$mk" .mk)"
    cat >"$mk" <<EOF
# 由 build_r2ghidra.sh 打桩：依赖已用镜像备好并打好补丁，禁止构建期联网。
.PHONY: ${name}_clean ${name}_all
${name}: ;
${name}_all: ;
${name}_clean: ;
EOF
done

# ---- 4/4 configure + make + 用户级安装 ----
log "== 4/4 configure + make -j4 + user-install =="
cd "$SRC" || exit 1
{ ./preconfigure && ./configure --prefix="$(r2 -H R2_PREFIX)"; } >>"$LOG" 2>&1 \
  || { log "configure 失败"; exit 1; }
{ make -C src -j4 && make -C src user-install; } >>"$LOG" 2>&1 \
  || { log "make 失败（见本日志）"; exit 1; }

log "== 完成；插件目录：$(ls -1 "$HOME/.local/share/radare2/plugins" 2>/dev/null | tr '\n' ' ')"
