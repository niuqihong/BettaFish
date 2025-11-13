#!/bin/bash
# 爬取所有支持的平台
# 用法: ./crawl_all_platforms.sh "AAPL,Tesla,Bitcoin"

KEYWORDS=${1:-"股市,A股,投资"}  # 默认关键词
MAX_NOTES=${2:-50}              # 每个关键词最多爬取数量

echo "🚀 开始爬取所有平台..."
echo "关键词: $KEYWORDS"
echo "每个关键词最多爬取: $MAX_NOTES 条"
echo ""

# 激活虚拟环境
source ../MP-venv/bin/activate

cd DeepSentimentCrawling/MediaCrawler

# 定义所有支持的平台
PLATFORMS=("wb" "xhs" "dy" "ks" "bili" "tieba" "zhihu" "yahoo_finance")

# 遍历每个平台
for platform in "${PLATFORMS[@]}"; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📍 平台: $platform"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # 根据平台设置是否爬评论
    if [ "$platform" = "yahoo_finance" ]; then
        GET_COMMENT="false"
    else
        GET_COMMENT="true"
    fi

    # 执行爬取
    python main.py \
        --platform "$platform" \
        --keywords "$KEYWORDS" \
        --type search \
        --get_comment "$GET_COMMENT" \
        --save_data_option postgresql \
        2>&1 | tee -a "../../logs/crawl_${platform}_$(date +%Y%m%d_%H%M%S).log"

    # 检查返回码
    if [ $? -eq 0 ]; then
        echo "✅ $platform 爬取完成"
    else
        echo "❌ $platform 爬取失败"
    fi

    echo ""
    echo "⏳ 等待 5 秒后继续下一个平台..."
    sleep 5
done

echo ""
echo "🎉 所有平台爬取任务完成!"
echo "查看日志: ls -l ../logs/"
