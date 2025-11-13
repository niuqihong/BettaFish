#!/bin/bash
# BettaFish 本地环境激活脚本

echo "🐟 激活 BettaFish 虚拟环境..."
source MP-venv/bin/activate

echo "✅ 虚拟环境已激活"
echo "📦 Python 版本: $(python --version)"
echo "📍 当前目录: $(pwd)"
echo ""
echo "💡 使用说明："
echo "  - 运行主应用: python app.py"
echo "  - 运行 MindSpider: cd MindSpider && python main.py --status"
echo "  - 退出虚拟环境: deactivate"
echo ""
