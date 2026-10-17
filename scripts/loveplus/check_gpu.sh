#!/bin/bash
# 用途：检查 WSL 的 D3D12/Vulkan 直通是否健康。
#   azahar 的 GUI（Vulkan）与 vkcube 走同一条路径（/dev/dxg → dzn → Windows 侧 Intel Arc 驱动），
#   所以用 vkcube 能否连跑 SECS 秒作为判据，比"azahar 卡不卡"更早、更确定。
# 用法：bash scripts/loveplus/check_gpu.sh [秒数，默认 8]
# 退出码：0 健康；1 需要处理（一般是在 Windows 里执行 wsl --shutdown）
set -u
SECS="${1:-8}"
fail=0
say_ok()   { echo "  OK    $1"; }
say_bad()  { echo "  失败  $1"; fail=1; }

echo "[1/3] /dev/dxg（WSL GPU 直通设备节点）"
if [ -c /dev/dxg ]; then say_ok "/dev/dxg 存在"; else say_bad "/dev/dxg 缺失"; fi

echo "[2/3] Vulkan 设备枚举"
if ! command -v vulkaninfo >/dev/null; then
    echo "  跳过（未安装 vulkan-tools）"
else
    summary=$(timeout 30 vulkaninfo --summary 2>/dev/null || true)
    if echo "$summary" | grep -q "Direct3D12"; then
        echo "$summary" | grep -E "deviceName|driverName" | sed 's/^[[:space:]]*/    /'
    else
        say_bad "未枚举到 Microsoft Direct3D12 设备"
    fi
fi

echo "[3/3] vkcube 实跑 ${SECS}s（真实呈现路径）"
if ! command -v vkcube >/dev/null; then
    echo "  跳过（未安装 vkcube）"
else
    out=$( { timeout "$SECS" vkcube 2>&1; echo "exit=$?"; } || true )
    if echo "$out" | grep -qE "Removing Device|Assertion"; then
        say_bad "设备被移除（D3D12 device lost）"
        echo "$out" | grep -E "Removing Device|Assertion" | sed 's/^[[:space:]]*/    /'
    elif echo "$out" | grep -q "exit=124"; then
        say_ok "跑满 ${SECS}s 未出错"
    else
        say_bad "提前退出"
        echo "$out" | tail -3 | sed 's/^[[:space:]]*/    /'
    fi
fi

echo
if [ "$fail" -eq 0 ]; then
    echo "结论：GPU 直通健康 —— azahar 的 Vulkan 渲染器可用。"
else
    echo "结论：GPU 直通不可用。处置顺序："
    echo "  1) Windows 侧按 Win+Ctrl+Shift+B 重置显卡驱动（轻量，先试）"
    echo "  2) Windows 的 PowerShell/CMD 里执行 wsl --shutdown，等 10 秒重开 WSL（可靠；会杀掉 WSL 里所有进程）"
    echo "  3) 仍不行：wsl --update 后重复 2)；并更新 Windows 的 Intel Arc 驱动（dzn 实际用的就是它）"
    echo "  注意：wsl --terminate <发行版> 不够——GPU 属于 WSL 虚拟机，必须整机重启。"
fi
exit "$fail"
