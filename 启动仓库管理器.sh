#!/bin/bash

# GitHub仓库管理器启动脚本

echo "🚀 启动GitHub仓库管理器..."
echo "📁 仓库路径: $(pwd)/Awesome-Stake-Guide"
echo "🔗 仓库地址: https://github.com/cheng-os/Awesome-Stake-Guide"
echo ""

# 检查Python3是否可用
if command -v python3 &> /dev/null; then
    python3 "仓库管理脚本.py"
else
    echo "❌ 错误: 未找到python3命令"
    echo "请确保已安装Python 3"
    exit 1
fi
