# azahar `DeleteFile` 死循环修复（NLP+ 追加数据创建卡死）

> 根因 / 修复 / 编译 / 验证 记录。配套 `scripts/loveplus/run_emu.sh` 无头启动流程见
> `memory/loveplus/headless_azahar.md`。

## 0. 现象

在无头 azahar 里跑 New Love Plus+，从存档引继菜单点「はじめから」→「はい」→「はい」，
进入 **「SDカードに追加データを作成しています」**（向 SD 卡创建追加数据）。

预期：进度条走完 → 进入新游戏流程。
实际：**进度条长时间不动**，模拟器日志以每秒多次的频率狂刷：

```
Service.FS <Error> core/file_sys/savedata_archive.cpp:DeleteFile:112:
  Path not found <repo>/.local/share/azahar-emu/sdmc/.../extdata/00000000/00000F4E/user/LP_PHOTO_MAIL/NLPPARC_02_13_01
```

`extdata/00000000/00000F4E/` 目录只生成了 `icon` / `metadata`（32K），没有任何创建中的文件。
进程 CPU 占满（~370%）、帧率正常，但**存档从未创建完成**。

## 1. 根因

`tools/azahar/src/core/file_sys/savedata_archive.cpp` 的 `SaveDataArchive::DeleteFile`：

```cpp
switch (path_parser.GetHostStatus(mount_point)) {
case PathParser::PathNotFound:
    LOG_ERROR(Service_FS, "Path not found {}", full_path);
    return ResultPathNotFound;          // ← 问题
case PathParser::FileInPath:
case PathParser::DirectoryFound:
case PathParser::NotFound:
    LOG_ERROR(Service_FS, "File not found {}", full_path);
    return ResultFileNotFound;          // ← 问题
case PathParser::FileFound:
    break; // Expected 'success' case
}
```

NLP+ 在创建追加数据时，会先对一批（预期的）旧文件/路径调用 `DeleteFile` 做清理。
这些路径在全新存档里**根本不存在**。

- 真实 3DS 上，删除一个不存在的路径/文件，FS 返回的是 `ErrorSummary_Nothing`
  （即**成功 / 无操作**）——游戏据此认为"清理完成"，继续下一步。
- azahar 这里却返回 `ResultPathNotFound` / `ResultFileNotFound`（错误）。
- 游戏的清理逻辑把"删除失败"当成需要重试的临时状态，**无限循环**地重新
  `DeleteFile` 同一个不存在的路径（`NLPPARC_02_13_01` 等），extdata 创建流程永远走不到"写文件"那一步。

注意 `InvalidMountPoint`（真正异常）仍保留为错误返回，本修复**不**改变它。

## 2. 修复

`savedata_archive.cpp` 中「路径/文件不存在」的两个分支改为返回 `ResultSuccess`
（无操作成功，与硬件行为一致），日志降级为 Warning：

```cpp
case PathParser::PathNotFound:
    // 真实 3DS 上删除一个不存在的路径/文件是 Success（无操作）。
    // 原 azahar 返回 ResultPathNotFound，导致某些游戏在创建 extdata 时
    // 反复重试清理不存在的旧文件而陷入死循环（如 NLP+ 追加数据创建卡死）。
    LOG_WARNING(Service_FS, "DeleteFile on missing path {} -> treating as success",
                full_path);
    return ResultSuccess;
case PathParser::FileInPath:
case PathParser::DirectoryFound:
case PathParser::NotFound:
    // 同上：删除不存在的文件按成功处理，与硬件行为一致。
    LOG_WARNING(Service_FS, "DeleteFile on missing file {} -> treating as success",
                full_path);
    return ResultSuccess;
```

改动规模：`+10 / -4`（仅替换两个错误返回分支，不影响 `FileFound` 的正常删除路径）。

## 3. 重新编译

azahar 的 CMake 生成器是 **Unix Makefiles**，`--target` 名是 **`citra_headless`**
（最终输出二进制叫 `azahar_headless`）：

```bash
cd tools/azahar/build_headless
make citra_headless -j4        # 只改到 savedata_archive.cpp，增量编译很快
# 校验新二进制已含修复：
strings bin/Release/azahar_headless | grep "treating as success"
```

编译输出：

```
[ 83%] Building CXX object src/core/CMakeFiles/citra_core.dir/file_sys/savedata_archive.cpp.o
[ 83%] Linking CXX static library libcitra_core.a
[100%] Built target citra_core
[100%] Linking CXX executable ../../bin/Release/azahar_headless
[100%] Built target citra_headless
```

> 提示：`cmake --build . --target azahar_headless` 会报
> `No rule to make target 'azahar_headless'` —— 正确 target 名是 `citra_headless`。

## 4. 验证

1. 清掉半成品 extdata（否则会带着损坏状态）：
   ```bash
   rm -rf ~/.local/share/azahar-emu/sdmc/Nintendo\ 3DS/*/*/extdata/00000000/00000F4E
   ```
2. 用修复后的二进制重启无头模拟器（无限运行，见 `run_emu.sh`）。
3. 重走创建流程：引继菜单「はじめから」→ 确认「はい」→ AC 适配器确认「はい」。
4. 进入「SDカードに追加データを作成しています」。

**修复前后日志对比：**

| 指标 | 修复前 | 修复后 |
| --- | --- | --- |
| `DeleteFile: Path not found` 错误 | 每秒多次、无限刷 | `0` 条 |
| `treating as success` 警告 | 无 | 对每个不存在路径一次性出现后不再重试 |
| extdata 创建 | 卡死（仅 icon/metadata，32K） | 继续推进（见监控 `monitor_create_text.py`） |

修复后游戏不再陷入删除重试死循环，追加数据创建流程正常推进。

## 5. 后续

存档创建真正完成（文字「SDカードに追加データを作成しています」消失）后，再继续推进主线
（见 `TODO.md`）：进入新游戏流程，并在「创建玩家信息」画面停下来向用户确认，之后转入
Siren14 语音 `.spp` 的断点调试（`scripts/loveplus/debug_siren.py`）。
