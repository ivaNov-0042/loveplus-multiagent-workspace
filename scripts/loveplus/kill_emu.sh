#!/bin/bash
# 安全终止无头模拟器（按 comm 名匹配，避免 pkill/xargs 匹配到执行它的 shell 自身）。
# 用法: bash scripts/loveplus/kill_emu.sh [信号的默认 KILL]
sig="${1:-TERM}"
pids=$(ps -eo pid=,comm= | awk '$2=="azahar_headless"{print $1}')
if [ -z "$pids" ]; then echo "no azahar_headless running"; exit 0; fi
echo "killing: $pids"
for p in $pids; do kill -"$sig" "$p" 2>/dev/null; done
sleep 2
left=$(ps -eo pid=,comm= | awk '$2=="azahar_headless"{print $1}')
if [ -n "$left" ]; then
  echo "still alive: $left -> SIGKILL"
  for p in $left; do kill -9 "$p" 2>/dev/null; done
  sleep 1
fi
ps -eo pid=,comm= | awk '$2=="azahar_headless"{print "REMAINS:", $1}'
echo "done"
