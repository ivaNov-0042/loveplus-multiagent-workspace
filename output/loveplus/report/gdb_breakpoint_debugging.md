# Love Plus+ 无头模拟器断点调试指南

> 面向本仓库的无头 azahar（Citra fork）环境，说明如何在**不依赖 ptrace / gdb** 的前提下
> 对 New Love Plus+ 的 ARM11 游戏代码下断点、观察与命中断点。

## 0. 关键前提：code.bin 是 LZSS 压缩的（"偏移量"问题的根因）

**踩坑记录**：直接对磁盘上的 `code.bin` 反汇编会**全是乱码**，即使地址、模式都对。
原因：ExeFS 的 `code` 段是 **3DS 特有的 LZSS 压缩**（加载日志 `Code compressed: yes`），
citra/azahar 在加载时解压到 `0x00100000`。所以：

- 磁盘 `code.bin`（4.4 MB）≠ 运行时代码；
- 必须解压后才能静态反汇编，解压产物大小 `0x7C0000`（8.1 MB）。
- 解压算法照搬 `tools/azahar/src/core/file_sys/ncch_container.cpp` 的
  `LZSS_GetDecompressedSize()` / `LZSS_Decompress()`（**从尾部向前**解码，
  footer 在文件末尾 8 字节）。
- 本仓库脚本：`scripts/loveplus/decompress_code.py`
  ```bash
  .venv/bin/python scripts/loveplus/decompress_code.py \
      data/loveplus/nlp_plus/code.bin data/loveplus/nlp_plus/code_text_unpacked.bin
  ```
- 验证：解压后 `0x105b44`、`0x122a50` 等地址与**运行时 guest 内存逐字节一致**
  （见 `scripts/loveplus/compare_text.py`）。

## 0b. 权威段基址（来自 ExHeader，与 Ghidra/IDA 3DS 插件一致）

3DS 各段基址不是"猜"的，而是写在 **ExHeader 的 CodeSetInfo** 里。
Ghidra 插件（如 `Martmists-GH/ghidra-ctr-loader`）与 IDA 3DS loader 都读这份信息。
本仓库脚本 `scripts/loveplus/parse_exheader.py` 直接解析 ROM 得到：

| 段 | 地址 | 大小 | 说明 |
| --- | --- | --- | --- |
| .text | `0x00100000` | `0x68f7fc` | 代码，反汇编基址 |
| .ro | `0x00790000` | `0x0f81a8` | 只读数据（字符串/常量） |
| .data | `0x00889000` | `0x036bbc` | 可写数据 |
| .bss | — | `0x1bb824` | 零初始化 |
| stack | — | `0x40000` | 主线程栈 |

ExHeader 位置：NCSD 分区0 起始 `0x4000` + NCCH 头偏移 `0x200`。
解析字段（azahar `ExHeader_CodeSetInfo`）：`name[8] + flags[8] + text{addr,pages,size} + ...`。

> 结论：`.text` 反汇编一律以 **base = `0x00100000`**、源文件 = **解压后的 `code_text_unpacked.bin`**。
> 字符串/常量在 `.ro`（`0x00790000` 起），此前在 `code.bin` 找字符串之所以对不上，
> 就是因为它压缩了、且字符串在 `.ro` 段（需单独解压 `ro` 或从 guest 内存取）。

## 1. 为什么不能用普通调试器

本机 `kernel.yama.ptrace_scope = 2`，且无法 `unshare` 用户命名空间，因此：

- `gdb --args ./azahar_headless ...` 报 `warning: ptrace: Operation not permitted`，无法 trace 宿主进程。
- `addr2line/objdump` 只对 x86 宿主有效，3DS 目标是 ARM11。

解决办法：azahar 自带 **GDB stub**，它是一个 **TCP 服务器**，调试器作为**客户端**连接，
不触发宿主的 ptrace 限制。

## 2. 断点的实现原理（azahar GDB stub）

关键源码：`tools/azahar/src/core/gdbstub/gdbstub.cpp`

- **断点是"内存打桩"**（software breakpoint），不是硬件断点，也不依赖 ptrace：
  `CommitBreakpoint()` 读取目标地址原指令缓存到 `breakpoint.inst`，然后写入：
  - ARM：`0xE1200070`（`BKPT` 指令，字节序 `70 00 20 E1`）
  - Thumb：`0xBE00`（`BKPT`，字节序 `00 BE`）
  写入后清指令缓存。
- 命中时 CPU 触发 `BKPT` 异常，stub 在下一个 `HandlePackets` 回调里发 `T05...` / `S05` 停止应答。
- `RemoveBreakpoint()` 把原指令写回。
- 支持类型（RSP `Z`/`z` 包的第一个数字）：
  | 数字 | 类型 | RSP 包 |
  | --- | --- | --- |
  | 0/1 | 执行断点 | `Z0,<addr>,<len>` |
  | 2 | 写 watchpoint | `Z2,...` |
  | 3 | 读 watchpoint | `Z3,...` |
  | 4 | 读写 watchpoint | `Z4,...` |
- `len`：ARM 传 4，Thumb 传 2（传 3 会被自动改为 2）。

> 因此本环境下**断点对 ARM 与 Thumb 都可用**，且可在运行时任意增删而无需重编译。

## 3. 运行无头模拟器并开启 stub

```bash
cd <repo>
SDL_AUDIODRIVER=dummy AZAHAR_LOG="*:Error" \
tools/azahar/build_headless/bin/Release/azahar_headless \
  "data/loveplus/roms_patched/NLP_plus_patched.3ds" \
  --gdb --port 24689 --frames 300000
```

- `--gdb --port N`：在 `System::Load` 后由 core 的 `ApplySettings()` 启动 TCP stub。
- 连接即**挂起**（进程被 `UnscheduleMode::GDB` 挂起），断开后自动恢复并重启监听。

## 4. 连接调试的两种方式

### 4.1 用 gdb-multiarch（交互式）

```bash
tools/bin/gdb-multiarch
(gdb) set architecture arm
(gdb) target remote 127.0.0.1:24689
(gdb) info registers            # 读全部寄存器
(gdb) break *0x00122a50         # 下执行断点
(gdb) continue
(gdb) x/16i $pc                 # 反汇编
(gdb) x/16wx 0x08000000         # 读内存
(gdb) detach
```

> 注意：本机 ptrace 被禁，所以 **gdb 只能做 `target remote` 客户端**，不能用 `run`/`attach`。

### 4.2 用自研 RSP 客户端（脚本化、可自动化）

`scripts/loveplus/rsp_client.py` 提供 `GDBClient`：

```python
from rsp_client import GDBClient
c = GDBClient(port=24689)        # 自动发 qSupported + '?' 选取主进程/线程
c.read_registers()               # {'r0':..,'pc':..}
c.set_break(0x00122a50)          # Z0
c.continue_()                    # c，返回停止应答
c.read_mem(0x08000000, 64)       # m
c.step()                         # s
c.close()
```

要点：
- 连接后必须发 `?`（非扩展模式）才会选取主进程/主线程，否则读寄存器返回 `E01`。
- RSP 的 `p`/`g` 寄存器是**小端 hex**：`0x00105b44` 会显示成 `445b1000`。
- 多线程：`H g<tid>` 选线程，`qXfer:threads:read::0,4000` 取线程表。

## 5. 定位"要断在哪里"

结合本仓库已验证的信息：

1. **code.bin 加载基址 = `0x00100000`**，file offset `X` ↔ VA `0x00100000 + X`。
   静态反汇编时用 `capstone`（`CS_ARCH_ARM` / `CS_MODE_THUMB` 需按 CPSR 的 T 位选择）。
2. 先**采样热地址**：用 `scripts/loveplus/rsp_bp_hit.py` 采样各线程 PC，
   挑一个落在 `0x00100000..0x00800000`（.text）的高频地址下断点验证。
3. 要抓 **Siren14 语音读取/解码**：
   - 语音数据在 RomFS 的 `Plus/Sound/Siren14Voice.spp`（656 MB）。
   - 可断在 **文件读取服务**（`fs:USER` OpenFile/ReadFile）或 SelfNCCH RomFS 读取路径，
     再回溯调用者（栈上的 `lr`）定位加载函数。
   - 或在 `code.bin` 里定位处理 46 字节帧的循环，断在帧处理入口。

## 6. 用「はじめから」推进到主流程

启动序列：KONAMI logo → LOVEPLUS PRODUCTION → NEW ラブプラス+ 标题 → **存档引继菜单**。
须在菜单点「はじめから」（从零开始）进入主流程。

- 触摸注入：`--input-script "start:dur:buttons[:tx:ty];..."`
  - `start`：起始帧；`dur`：持续帧数；`buttons`：按键位掩码（`1<<A` 等）；
    `tx,ty`：归一化触摸坐标（0..1，原生 320×240 空间）。
- 菜单按钮「はじめから」在归一化坐标 **(0.428, 0.496)**。
  注意：azahar 软渲染的 bottom 缓冲是 240×320 竖屏（旋转后显示），
  坐标映射要用**原生 320×240** 的归一化值，不要直接用竖屏像素坐标，
  否则会点到「ラブプラス、ラブプラス+から引継ぎ」分支而报"找不到引继存档"。
- 实测脚本（随后用于打断点）：

```bash
SDL_AUDIODRIVER=dummy AZAHAR_LOG="*:Error" \
tools/azahar/build_headless/bin/Release/azahar_headless \
  "data/loveplus/roms_patched/NLP_plus_patched.3ds" --gdb --port 24689 --frames 400000 \
  --input-script "112000:12:0:0.428:0.496;124000:12:0:0.428:0.496;137000:12:0:0.713:0.714"
# 末项 (0.713,0.714) 是弹出「追加データ作成？」确认框的「はい」按钮
```

> 注意：脚本化 `--input-script` 是**写死时间轴**的，调试时反复调试帧号很痛苦。
> 更优方案见下一节——把模拟器作为常驻后台服务，用 MCP 工具**实时**下发触摸/按键并取屏。

## 6b. 交互式控制：把模拟器当"可遥控的游戏机"（MCP）

把 `azahar_headless` 作为后台常驻进程，新增一个 **TCP 控制通道**（`headless_main.cpp`
里的 `ControlServerLoop`，监听 127.0.0.1:24777）。每条命令实时覆盖全局原子变量，
主循环每帧 `ApplyLiveInput` 叠加到脚本计划之上。这样无需重启即可任意时刻摸屏、看屏。

配套 MCP 服务 `scripts/loveplus/loveplus_mcp.py`（stdio 传输，已 pin `mcp==1.30.0`
以保留 `FastMCP` API），暴露的工具：

| 工具 | 作用 |
| --- | --- |
| `start_emulator` / `stop_emulator` / `is_running` | 启停/查询后台模拟器 |
| `tap(x,y,frames)` | 点一下并自动松开 |
| `touch(x,y)` / `release()` | 按住 / 松开（可配合 `move` 拖拽） |
| `move(x,y)` | **保持按下状态不变**，把触摸点移到新位置（拖拽核心） |
| `drag_path(points, hold_frames, move_frames, release_at_end)` | **任意长度路径点序列拖拽**；每个点的"移动时长"`move_frames` 与"到达后停留时长"`hold_frames` 可逐点指定（标量=全部相同，列表=逐点），用于滚屏/滑块/列表滑动/键盘擦写 |
| `swipe(...)` | `drag_path` 的两点特例 |
| `buttons(hex)` / `buttons_off()` | 额外按住/松开按键位掩码 |
| `screenshot(which)` | 立即抓屏并返回 PNG（bottom/top_left/top_right/all） |
| `frame()` / `status()` / `pause()` / `resume()` | 帧号/状态/暂停主循环（便于 GDB 附着）/继续 |

`drag_path` 示例：画一个方框并最后松开

```python
await session.call_tool("drag_path", {
  "points": [[0.3,0.3],[0.7,0.3],[0.7,0.7],[0.3,0.7]],
  "hold_frames": [6,4,4,6],     # 各点停留帧数（含首点按下、末点结束）
  "move_frames": [10,6,10],      # 相邻点间移动帧数
  "release_at_end": True})
```

底层客户端 `scripts/loveplus/emulator_ctl.py`（`EmuControl`）可脱离 MCP 单独使用：
`c.tap(0.428,0.496); c.frame(); c.dump(); c.screenshot...`。

启动方式（后台常驻，模拟器 PID 写入 `/tmp/emu.pid`）：

```bash
setsid bash scripts/loveplus/run_emu.sh > /tmp/emu_live.log 2>&1 < /dev/null &
```

## 7. 典型工作流

```text
启动(带 --gdb) ──► 连接 stub ──► 采样PC找热点 ──► 下断点 ──► continue
      ▲                                                       │
      └──────── 命中：读寄存器/栈/内存 ──► 分析 ──► 继续 ◄──────┘
```

完整可复用脚本见 `scripts/loveplus/`：
`rsp_client.py`（库）、`rsp_bp_hit.py`（断点命中验证）、
`pc_evolve.py`（多线程 PC 采样）、`threads_dump.py`（线程反汇编）、
`debug_siren.py`（本报告实践：断点 + 内存 dump）。

## 8. 已知约束与坑

- 游戏需 **NCCH `no_crypto` 补丁副本**才能被 citra 接受（见 `headless_azahar.md`）。
- 无声卡环境需 `SDL_AUDIODRIVER=dummy`。
- stub 为**单客户端**：一个客户端断开后 server 重启，重连前有一个短暂窗口。
- `Z0` 的 `len`：ARM=4、Thumb=2，传错会返回 `E02`。
- 读内存 `m` 单次上限约 0x400 字节（客户端已自动分块）。
- **GPU 显存/未映射区**不可读，断点地址必须在可执行段。
