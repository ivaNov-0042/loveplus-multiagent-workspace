#!/usr/bin/env python3
"""项目路径集中管理：从项目根 .env 载入本地路径，避免任何硬编码机器目录。

其他脚本顶部加：
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from common_paths import *   # 提供 REPO/HEADLESS/ROM/CODE_BIN/CODE_UNPACKED 等

.env 缺失时退回到相对本仓库的默认路径，保证在任意机器上可运行。
"""
import os
import sys
from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))          # scripts/loveplus
REPO = os.path.dirname(os.path.dirname(HERE))              # 项目根

# 优先从项目根 .env 载入（内含机器相关绝对路径），否则用相对默认
load_dotenv(os.path.join(REPO, ".env"))

REPO = os.environ.get("LOVEPLUS_REPO", REPO)
AZAHAR_HEADLESS = os.environ.get(
    "AZAHAR_HEADLESS",
    os.path.join(REPO, "tools", "azahar", "build_headless", "bin", "Release", "azahar_headless"))
NLP_PLUS_ROM = os.environ.get(
    "NLP_PLUS_ROM",
    os.path.join(REPO, "data", "loveplus", "roms_patched", "NLP_plus_patched.3ds"))
NLP_CODE_BIN = os.environ.get(
    "NLP_CODE_BIN",
    os.path.join(REPO, "data", "loveplus", "nlp_plus", "code.bin"))
NLP_CODE_UNPACKED = os.environ.get(
    "NLP_CODE_UNPACKED",
    os.path.join(REPO, "data", "loveplus", "nlp_plus", "code_text_unpacked.bin"))

# 兼容性别名（部分旧脚本用 HEADLESS / ROM / CODE 等单字母变量）
HEADLESS = AZAHAR_HEADLESS
ROM = NLP_PLUS_ROM
CODE = NLP_CODE_UNPACKED
CODE_BIN = NLP_CODE_BIN
CODE_UNPACKED = NLP_CODE_UNPACKED

EMU_LIVE_PORT = int(os.environ.get("EMU_LIVE_PORT", "24777"))
EMU_GDB_PORT = int(os.environ.get("EMU_GDB_PORT", "24689"))
EMU_DUMP_PREFIX = os.environ.get("EMU_DUMP_PREFIX", "/tmp/az")
