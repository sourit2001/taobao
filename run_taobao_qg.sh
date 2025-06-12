#!/bin/bash
# 获取脚本所在的目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# 切换到该目录
cd "$SCRIPT_DIR"
# 执行Python脚本
python taobao_qg.py
