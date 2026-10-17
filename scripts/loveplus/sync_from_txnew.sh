#!/usr/bin/env bash
# sync_from_txnew.sh —— 从远端仓库主机同步整个仓库到本机（增量、可断点续传）
#
# 为什么需要：远端 tx-new（Ubuntu 24.04）与本机（Ubuntu 26.04 / WSL）SONAME 不同
# （libFLAC.so.12 vs .14、pulse 16 vs 17），远端编出来的二进制在本机跑不起来，
# 但源码/数据/脚本/文档必须两边一致，故定期拉取。
#
# 用法：
#   bash scripts/loveplus/sync_from_txnew.sh --dry-run   # 只看差异，不传
#   bash scripts/loveplus/sync_from_txnew.sh             # 传，失败自动重试
#
# 长任务后台化（见 skill `loveplus-emu-ops`「后台任务按寿命选挂法」）：数小时、可能跨会话重启，
# 必须 setsid 脱离会话，否则会话重启时整组被 SIGTERM（2026-10-17 吃过一次）：
#   setsid nohup bash scripts/loveplus/sync_from_txnew.sh \
#       >/tmp/opencode/sync.out 2>&1 </dev/null &
#
# 可覆盖的环境变量（默认为空则由 .env / 本机推断）：
#   LOVEPLUS_REPO        本机仓库路径     默认 .env
#   LOVEPLUS_REMOTE      远端 ssh 主机    默认 tx-new
#   LOVEPLUS_REMOTE_REPO 远端仓库路径     默认与本机相同（两台机路径一致）
#   SYNC_LOG             日志文件         默认 /tmp/opencode/rsync-full.log
#   SYNC_ATTEMPTS        最大尝试次数     默认 200
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"          # scripts/loveplus -> 项目根

# 本地路径一律来自项目根 .env（禁止在脚本内硬编码机器目录）
if [ -f "$ROOT/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  . "$ROOT/.env"
  set +a
fi

REPO="${LOVEPLUS_REPO:-$ROOT}"
REMOTE="${LOVEPLUS_REMOTE:-tx-new}"
REMOTE_REPO="${LOVEPLUS_REMOTE_REPO:-$REPO}"
LOG="${SYNC_LOG:-/tmp/opencode/rsync-full.log}"
ATTEMPTS="${SYNC_ATTEMPTS:-200}"

DRY=()
[ "${1:-}" = "--dry-run" ] && DRY=(--dry-run)

# 排除项：只放「本机重新生成的构建产物」。
# 2026-10-17：本机把 azahar/ 与 3dstool/ 移进了 tools/（用户决定；远端 tx-new 仍是旧布局），
# 故两套路径都要排除：/azahar/、/3dstool/ 用来挡住远端那份把根目录目录树重新拉回来。
# 例外说明：源码与 vendored externals 一律同步，但 tools/azahar/ 与 tools/3dstool/ 除外
# （它们的源码更新改由各自 .git 自行 fetch）。
# 注意 tools/azahar/externals/*/build* 是上游源码目录而非产物，绝不可排除。
EXCLUDES=(
  --exclude=/azahar/
  --exclude=/3dstool/
  --exclude=/tools/azahar/build_headless/
  --exclude=/tools/azahar/build_qt/
  --exclude=/tools/3dstool/build/
  --exclude=/tools/3dstool/bin/Release/
  --exclude=/.venv/
)

# --update：不覆盖本机较新的文件，保护本机新写的脚本/笔记（两边都改的文件以本机为准）
SSH_OPTS="ssh -o BatchMode=yes -o ConnectTimeout=20 -o ServerAliveInterval=20 -o ServerAliveCountMax=6"

echo "[sync] $REMOTE:$REMOTE_REPO/  ->  $REPO/   (日志 $LOG)"
for i in $(seq 1 "$ATTEMPTS"); do
  echo "=== sync attempt $i start $(date '+%F %T') ==="
  rsync -a --partial --partial-dir=.rsync-partial --timeout=120 \
        --info=progress2 --update "${DRY[@]}" "${EXCLUDES[@]}" \
        -e "$SSH_OPTS" "$REMOTE:$REMOTE_REPO/" "$REPO/" 2>&1 | tee -a "$LOG"
  rc=${PIPESTATUS[0]}
  echo "=== sync attempt $i exit=$rc at $(date '+%F %T') ==="
  if [ "$rc" -eq 0 ]; then
    echo "=== SYNC COMPLETE $(date '+%F %T') ==="
    exit 0
  fi
  sleep 20
done
echo "=== SYNC GAVE UP $(date '+%F %T') ==="
exit 1
