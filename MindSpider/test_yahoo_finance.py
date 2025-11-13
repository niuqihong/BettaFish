#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Yahoo Finance 爬虫测试脚本
"""

import sys
import os

# 添加 MediaCrawler 到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "DeepSentimentCrawling", "MediaCrawler"))

# 测试导入
try:
    from media_platform.yahoo_finance import YahooFinanceCrawler
    print("✅ Yahoo Finance 爬虫导入成功!")
    print(f"✅ 爬虫类: {YahooFinanceCrawler}")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("Yahoo Finance 爬虫已成功集成到 MediaCrawler!")
print("="*60)
print("\n使用方法:")
print("1. 修改 MediaCrawler/config/base_config.py:")
print('   PLATFORM = "yahoo_finance"')
print('   KEYWORDS = "AAPL,TSLA,Bitcoin"  # 搜索关键词')
print("\n2. 运行爬虫:")
print("   cd MindSpider/DeepSentimentCrawling/MediaCrawler")
print("   python main.py")
print("="*60)
