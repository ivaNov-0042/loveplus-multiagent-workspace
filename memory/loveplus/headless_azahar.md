<!-- 生成物，勿手改：真源 `multiagents/state/memory/loveplus/headless_azahar.json`；改动走 `python3 multiagents/agentctl.py memory …`，本文件由 `memory export --write` 重渲染。 -->

# 无头 azahar（Citra fork）动态调试环境

> **路径布局（2026-10-17 起）**：azahar 与 3dstool 已从仓库根移入 `tools/`，本文所有路径
> 按新布局书写（`tools/azahar/…`）。远端 tx-new 仍是旧布局（根目录 `azahar/`），同步脚本
> 已排除两边这两棵子树；本机 `tools/azahar/build_headless` **只剩 `bin/`**（构建树已清），
> 要重编需重新 configure（配方见下节）。

## 为什么需要自建无头前端

- azahar 的 `citra_meta` 只实现了压缩 CLI；实际模拟必须走 Qt 前端（`LaunchQtFrontend`）。
- 本机 **无 sudo**，装不了 Qt/SDL/Vulkan。故新增 `src/citra_headless/`：
  最小前端，仅实现 `Frontend::EmuWindow`（`PollEvents` 空实现 + 软件渲染器），
  链接 `citra_common/citra_core/video_core/audio_core`。

## 关键代码改动（相对上游 master）

| 文件 | 改动 |
| --- | --- |
| `src/citra_headless/headless_main.cpp` | 新增：解析参数、`System::Load`、`ApplySettings`、`RunLoop` 主循环、崩溃 backtrace |
| `src/citra_headless/CMakeLists.txt` | 新增目标 `citra_headless`（输出 `azahar_headless`） |
| `src/CMakeLists.txt` | `add_subdirectory(citra_headless)`（不受 `ENABLE_QT` 限制） |

## 两个必须的绕过（否则加载失败/崩溃）

1. **NCCH `no_crypto` 标志**：解密版 ROM 的 NCCH 头 flag(`no_crypto`, offset 0x18F)未置位，
   citra 会以 `ErrorEncrypted` 拒绝。做法：复制 ROM 到
   `data/loveplus/roms_patched/NLP_plus_patched.3ds`，把偏移 **0x418F** 的字节 `|= 0x04`
   （0x418F = NCSD 分区0 起始 0x4000 + NCCH flag 偏移 0x18F）。**归档 ROM 保持原样**。
2. **`lle_modules` 映射**：`Service::Init` 会 `Settings::values.lle_modules.at(name)`，
   Qt 前端从配置文件填充该 map；无头前端需在 `Load` 前对 `Service::service_module_map`
   全部 `emplace(name, false)`（默认走 HLE），否则抛 `std::out_of_range`。

## 构建

```bash
cd tools/azahar && mkdir build_headless && cd build_headless
cmake .. -DCMAKE_BUILD_TYPE=Release \
  -DENABLE_QT=OFF -DENABLE_SDL2=ON -DUSE_SYSTEM_SDL2=ON \
  -DENABLE_VULKAN=OFF -DENABLE_OPENGL=OFF \
  -DENABLE_SOFTWARE_RENDERER=ON -DENABLE_WEB_SERVICE=OFF -DENABLE_SCRIPTING=OFF \
  -DENABLE_GDBSTUB=ON -DENABLE_CUBEB=OFF -DENABLE_OPENAL=OFF -DENABLE_LIBUSB=OFF \
  -DENABLE_ROOM=OFF -DENABLE_ROOM_STANDALONE=OFF -DENABLE_TESTS=OFF \
  -DENABLE_DISCORD_RPC=OFF -DENABLE_FFMPEG=OFF \
  -DCITRA_WARNINGS_AS_ERRORS=OFF -DCITRA_USE_PRECOMPILED_HEADERS=OFF -DENABLE_LTO=OFF
make -j4 citra_headless
# 产物: build_headless/bin/Release/azahar_headless
```
> 说明：系统装有 SDL2 2.30.0，开启 `ENABLE_SDL2` 是为了让音频 sink 走 SDL
> （否则无声卡环境仍可运行，但日志会有 SDL 打开失败）。运行时用
> `SDL_AUDIODRIVER=dummy` 即可静默初始化。

## 运行

```bash
azahar_headless <rom.3ds> [--gdb] [--port N] [--frames N]
                         [--dump-every N] [--dump-prefix P]
                         [--input-script "start:dur:buttons[:tx:ty];..."]
# 环境变量: AZAHAR_LOG="*:Info"(默认) / "*:Error" 控日志;
#           SDL_AUDIODRIVER=dummy 让 SDL 音频 sink 在无声卡环境初始化成功
```
- `--frames N`：主循环迭代上限（一次迭代≈一帧渲染）。
- `--dump-every N --dump-prefix P`：每 N 帧把三个软渲染屏导出为
  `P_<frame>_{top_left,top_right,bottom}.ppm`（P6）。
  **注意**：SwRenderer 缓冲是列主序 `(x*height+y)*4` 且 y 轴需反向；
  `bottom` 屏原始缓冲是 240(w)×320(h) 的竖屏（游戏渲染方向）。
- `--input-script`：脚本化输入。每项 `帧:持续帧数:按键位掩码[:触摸x:触摸y]`，
  多项用 `;` 分隔。触摸坐标为归一化 0..1（会乘到 320×240）。
  例：`115000:10:0:0.569:0.5` 在第 115000 帧起按住触摸点 (0.569,0.5) 10 帧。
  脚本工厂 `headless` 注册到 Button/Touch 工厂，改写 `current_input_profile`。

## 实际运行截图（真实模拟器输出，见 `output/loveplus/img/`）

游戏可完整走过启动序列（emu 时间可达 50s+），已截到：
| 阶段 | 顶部屏 | 底部屏 |
| --- | --- | --- |
| KONAMI logo | 红字 KONAMI | — |
| LOVEPLUS PRODUCTION | — | 蓝色心形方块 logo |
| NEW ラブプラス+ 标题 | 标题+日文说明 | — |
| 存档引继菜单 | 标题画面 | 4 个竖排按钮（NEWラブプラスから引継ぎ / ラブプラス、ラブプラス+から引継ぎ / **はじめから** / ラブプラス、ラブプラス+用 セーブデータ引継ぎツール） |

汇总图：`output/loveplus/img/nlpp_boot_montage.png`。
触摸坐标映射：raw(240×320) 竖屏缓冲 → 原生(320×240) 触摸坐标需旋转
（`native=(raw_y, 240-1-raw_x)` 类映射），"はじめから" 约在归一化 (0.569, 0.50)。
实测点击会改变按钮高亮，确认触摸注入生效。

## 已知 Bug 修复：SaveDataArchive::DeleteFile 死循环（追加数据创建卡死）

**现象**：NLP+ 创建追加数据（「SDカードに追加データを作成しています」）时进度条卡死，
日志每秒多次狂刷 `savedata_archive.cpp:DeleteFile:112 Path not found .../00000F4E/user/LP_PHOTO_MAIL/NLPPARC_02_13_01`，
extdata 只生成 `icon`/`metadata`（32K），永远建不完。

**根因**：`core/file_sys/savedata_archive.cpp` 的 `DeleteFile` 对"路径/文件不存在"
返回 `ResultPathNotFound` / `ResultFileNotFound`（错误）。真实 3DS 上删除不存在的东西是
**成功（无操作）**；游戏据此无限重试清理旧文件 → 死循环。

**修复**：把 `PathNotFound` / `NotFound` / `FileInPath` / `DirectoryFound` 四个分支
改为 `return ResultSuccess`（Warning 级别日志）。`InvalidMountPoint` 仍保留错误返回。

```cpp
case PathParser::PathNotFound:
    LOG_WARNING(Service_FS, "DeleteFile on missing path {} -> treating as success", full_path);
    return ResultSuccess;
// FileInPath / DirectoryFound / NotFound 同理
```

**重新编译**（注意 target 名是 `citra_headless`，不是 `azahar_headless`）。
注意：本机 `tools/azahar/build_headless/` 里**没有** Makefile/CMakeCache（只剩 `bin/`），
下面这条只适用于**还有构建树**的副本（如远端 tx-new）；本机要重编得先按上节重新 configure：
```bash
cd tools/azahar/build_headless && make citra_headless -j4
strings bin/Release/azahar_headless | grep "treating as success"   # 校验
```

**验证**：日志 `Path not found` 归零，改为一次性 `treating as success`，创建流程推进。
完整记录见 `output/loveplus/report/azahar_deletefile_fix.md`。

## 已知阻塞

- ROM 的 NCCH `no_crypto` 未置位 → 需用补丁副本（见上）。
- SDL 音频在无声卡环境默认打开失败，需 `SDL_AUDIODRIVER=dummy`。
- 游戏启动到"存档引继菜单"后，若未选择"はじめから"会停留；选后应进入主流程。
- 创建追加数据前必须清掉半成品 extdata（`~/.local/share/azahar-emu/sdmc/.../00000F4E`），
  否则带着损坏状态仍可能卡在清理阶段。

## 调试：本机 ptrace 被禁 → 走 GDB stub(TCP)

- `ptrace_scope=2` 且无法 `unshare`，**本地 gdb 无法 trace 进程**。
  因此用 azahar 自带 **GDB stub**（TCP server，客户端是 gdb，不触发 ptrace 限制）。
- gdb 客户端：`tools/bin/gdb-multiarch`（GNU GDB 18.1，支持 ARM/ARMv7）。
  来源：无 sudo，从 aliyun 镜像取 `gdb-multiarch` .deb 解包，并自建 `libipt.so.2` 桩。
- 自研 RSP 客户端 `scripts/loveplus/rsp_client.py`：不依赖 gdb，
  可枚举线程(`qXfer:threads:read`)、选线程(`Hg`)、读寄存器(`g`/`p`)、读内存(`m`)、
  断点(`Z0`)、continue(`c`)、单步(`s`)。
  - 注意：RSP `p`/`g` 寄存器为**小端 hex**；`0x00105b44` 显示为 `445b1000`。
  - 新连接需先发 `?`（非扩展模式）以选取主进程与主线程，否则 `E01`。

## 验证结论（已跑通）

- 游戏以无头模式启动：名称 `nlpp`，TitleID `00040000000F4E00`，入口 `0x00100000`。
- 持续运行不崩（可跑数万帧）；GDB stub 连接即挂起，`c`/`s`/断点均生效。
- **断点实测命中**：`0x00122a50`（thread a），见 `scripts/loveplus/rsp_bp_hit.py` 输出
  `[bp] hit pc=0x00122a50 match=True`。

## 相关脚本

| 脚本 | 作用 |
| --- | --- |
| `scripts/loveplus/rsp_client.py` | RSP 客户端库 |
| `scripts/loveplus/rsp_probe.py` | 连接并单步/断点探测 |
| `scripts/loveplus/rsp_sample.py` | 采样 PC |
| `scripts/loveplus/rsp_bp_hit.py` | 断点命中验证 |
| `scripts/loveplus/rsp_verify.py` | 端到端验证 |
| `scripts/loveplus/fetch_submodules.sh` 等 | 子模块断点续传/检出修复 |

## 交互式控制通道（2026-10-15 新增）

- `headless_main.cpp` 加了 TCP 控制通道 `ControlServerLoop`（127.0.0.1:24777，独立线程）。
  每条命令实时覆盖全局原子变量，主循环 `ApplyLiveInput` 每帧叠加到脚本计划之上。
- 命令：tap/touch/move/release/buttons/buttons_off/dump/frame/status/pause/resume/ping。
  - **move(x,y)** 保持当前按下状态不变地移动触摸点 → 实现拖拽。
  - tap 内部用 `g_live_release_at` 在 N 帧后自动松开。
- 配套 MCP 服务 `scripts/loveplus/loveplus_mcp.py`（stdio，`mcp==1.30.0` 以保 FastMCP）。
  工具：start/stop/is_running/tap/touch/move/release/drag_path/swipe/buttons/buttons_off/
  screenshot(which)/frame/status/pause/resume。
  - `drag_path(points, hold_frames, move_frames, release_at_end)`：任意长度路径点序列；
    每点移动时长 move_frames、到达后停留时长 hold_frames 可标量或列表逐点指定。
- 底层客户端 `scripts/loveplus/emulator_ctl.py`（`EmuControl`）可脱离 MCP 单用。
- **（2026-10-15）NLP+ 文本输入双屏机制**：上屏(u/top,240x400)显示已提交的已完成文本，
  下屏(b/bottom,240x320)是键盘/手写输入区。每一步输入**必须同时 dump u+b 两张图**，
  靠脚本 `shot_ub.py` 先 dump 现态、按键后再存 u+b 并用 read 看图确认输入结果。
  命名严格 `N_u_描述.jpg`/`N_b_描述.jpg`。
- 启动（后台常驻）：`setsid bash scripts/loveplus/run_emu.sh > /tmp/emu_live.log 2>&1 < /dev/null &`
  （PID 写入 /tmp/emu.pid；**不要用 pkill -f azahar_headless，会误杀含该字符串的 shell 自身**）。
- 坐标：命令用原生 320×240 归一化 (x,y)；dump 竖屏图 240×320。实测映射
  **touch_x = 1 − dump_y/320，touch_y = dump_x/240**（即 y 轴镜像）。
  已验证坐标（dump→touch 换算后）：
  - 主菜单「はじめから」= (0.431, 0.5)
  - 确认框「はい」= (0.266, 0.742)（窗口右）；「いいえ」= (0.266, 0.25)（窗口左）
  - 按钮4「引継ツール」= (0.631, 0.5)；按钮2「引継ぎ」= (0.569, 0.5)
  - 旧记录 (0.713,0.714) 为误判（短按+缩略图比例换算错误）。
- **NLP+ 菜单/对话框必须长按 ≥1 秒**：`tap`（12-14 帧≈0.2s）对菜单/对话框无效，
  需用 `touch`+sleep(1.2~1.5s)+`release`。早期多轮"点错分支"根源在此。
- **画面判定用多模态而非 CV**：`dump → 1:1 存 /tmp/img_preview/ → read`；按钮命中
  判定 = `touch 按下 → 立即 dump → read（按钮按下会变色）→ release`。背景动画噪声
  (~27000/6s) 会淹没像素 diff，不可靠。
- **（2026-10-15）文字输入必须 u/b 成对截图（2026-10-15 用户指明）**：输入界面
  **上屏显示"你输入了什么"，下屏是键盘/手写板**——只看下屏无法确认输入结果。
  每次输入操作后用 `scripts/loveplus/shot_ub.py --step <步骤> --desc <词>`
  同时落盘 `N_u_描述.jpg` + `N_b_描述.jpg`（id 自动续号；`--touch X Y` 可先长按再截，
  `--also-release` 自动补一张 release 后的图做双相验证）。
  键位输字用 `scripts/loveplus/type_uib.py`（按 dump 坐标 → 自动换算 touch → press 相 +
  rel 相 u/b 各成对落盘；支持 --seq 连续多键），文字输入时上屏显示输入结果、下屏是键盘，
  **u/b 必须同看才能确认输入是否成功**。
- dump 文件：`/tmp/az_live_*_bottom.ppm`（240×320）；MCP `screenshot(which, out_dir, filename,
  fmt="jpg", quality=80)` 转存到 `/tmp/loveplus_shots/`。
  **（2026-10-15）默认改存 JPEG**（质量 80）以降低数据量；需无损时用 `fmt="png"`。
- **（2026-10-16）磁盘/日志清理规约**：40G 盘长期 89-96% 占用，必须主动防写满——
  - **MCP `screenshot` 截图前自动 `_cleanup_disk()`**：`/` 占用 ≥90% 时删 `/tmp/az_live_*.ppm`
    残留 + 按 mtime 删最旧 `/tmp/loveplus_shots/` 步骤目录，直到降到阈值下。
  - **MCP `screenshot` 转 jpg/png 后删除源 ppm**（避免堆积）。
  - **定时清理 azahar(citra) 日志**：`scripts/loveplus/cleanup_logs.py` 每天 03:17 经 crontab 跑，
    删 `/tmp/emu_live.log`、`~/.local/share|config/azahar/**/*.log`、残留 ppm、超 7 天截图；
    磁盘超 90% 时强制清最旧 shots 目录到阈值下。`--dry` 只打印不删。
  - emulator 运行期 stdout 经 `run_emu.sh > /tmp/emu_live.log 2>&1` 持续写入，勿删正在持有的 fd；
    清理脚本按 7 天年龄删、超阈强制清目录。
- **（2026-10-15）长按用 `drag_path` 实现**：`drag_path(points=[[x,y]], hold_frames=[N],
  release_at_end=True)` 即可"按住 N 帧后松开"（N=90≈1.5s），等价于 touch+sleep+release，
  且走 MCP 调用无需脚本。菜单/对话框均需 ≥1s 才注册。
- **（2026-10-15）MCP 服务重启方法**：opencode 界面里按**空格**即可重启 MCP 服务
  （重新拉起 stdio 进程并刷新工具目录）。修改 `loveplus_mcp.py` 后需重启服务才生效；
  杀掉进程后若工具目录未恢复，用界面空格重启。
  另：`opencode mcp list` 显示 failed 不代表真失败——它是发完请求即关 stdin 的快速
  探测，会用 `Connection closed` 误报；验证服务是否正常用 stdio 手动 initialize +
  tools/list（保持 stdin 打开）。
- **（2026-10-15）MCP screenshot 曾报 `Image has no attribute open`**：进程内 `Image`
  名字被遮蔽/污染所致，已在 `screenshot()` 内改用 `from PIL import Image as _PILImage`
  防御；如再遇到先怀疑模块名遮蔽。

## 本机（WSL）UI 版构建（2026-10-17）

远端 tx-new（Ubuntu 24.04）与本机（WSL / Ubuntu 26.04）SONAME 不同，远端编出的二进制在本机
无法运行，故本机需自行编译。记录全文见 `memory/others/diary/2026-10-17_02_static-re.md`（apt 依赖清单、
Qt 6.10.3 预下载的镜像坑、`ENABLE_CUBEB=OFF` 的由来、WSLg/dzn 结论）。

脚本（路径均经项目根 `.env`，无硬编码机器目录）：

- `scripts/loveplus/sync_from_txnew.sh` —— 从远端拉仓库；小时级任务，须
  `setsid nohup … </dev/null &`（见 skill `loveplus-emu-ops`「后台任务按寿命选挂法」）。
- `scripts/loveplus/fetch_qt.sh` + `aqt_mirror.ini` —— 预下载 Qt 到
  `tools/azahar/build_qt/externals/qt/6.10.3/gcc_64`。
- `scripts/loveplus/build_azahar_qt.sh` —— configure 与编译 UI 版，产物
  `tools/azahar/build_qt/bin/Release/azahar`。

**注意：UI 版没有 MCP 控制通道。** `--live-port` / `ControlServerLoop` 只存在于
`src/citra_headless/headless_main.cpp`，MCP 自动化（触摸/按键/截图）仍只能用无头版
`azahar_headless`；UI 版用于肉眼看画面与手动操作，GDB 调试两边都可用。
