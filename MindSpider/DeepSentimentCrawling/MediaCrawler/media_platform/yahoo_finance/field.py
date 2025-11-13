# 声明:本代码仅供学习和研究目的使用。使用者应遵守以下原则:
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率,避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。

# -*- coding: utf-8 -*-
# @Desc    : Yahoo Finance 字段定义

from enum import Enum


class SearchType(Enum):
    """搜索类型"""
    # 新闻
    NEWS = "news"

    # 股票报价
    QUOTES = "quotes"

    # 全部
    ALL = "all"


class NewsTimeRange(Enum):
    """新闻时间范围"""
    # 任何时间
    ANY_TIME = ""

    # 过去一天
    PAST_DAY = "1d"

    # 过去一周
    PAST_WEEK = "1w"

    # 过去一个月
    PAST_MONTH = "1m"
