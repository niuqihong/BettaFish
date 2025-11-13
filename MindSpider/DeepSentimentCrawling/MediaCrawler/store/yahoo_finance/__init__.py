# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。

# -*- coding: utf-8 -*-
# @Desc    : Yahoo Finance 存储工厂和业务函数

from typing import Dict, List

import config
from base.base_crawler import AbstractStore
from tools import utils

from ._store_impl import *


class YahooFinanceStoreFactory:
    STORES = {
        "csv": YahooFinanceCsvStoreImplement,
        "db": YahooFinanceDbStoreImplement,
        "json": YahooFinanceJsonStoreImplement,
        "sqlite": YahooFinanceSqliteStoreImplement,
        "postgresql": YahooFinanceDbStoreImplement,
    }

    @staticmethod
    def create_store() -> AbstractStore:
        store_class = YahooFinanceStoreFactory.STORES.get(config.SAVE_DATA_OPTION)
        if not store_class:
            raise ValueError(
                "[YahooFinanceStoreFactory.create_store] Invalid save option only supported csv or db or json or sqlite or postgresql ..."
            )
        return store_class()


async def batch_update_yahoo_finance_news(news_list: List[Dict]):
    """
    批量更新 Yahoo Finance 新闻
    Args:
        news_list: 新闻列表

    Returns:

    """
    if not news_list:
        return
    for news_item in news_list:
        await update_yahoo_finance_news(news_item)


async def update_yahoo_finance_news(news_item: Dict):
    """
    更新单条 Yahoo Finance 新闻
    Args:
        news_item: 新闻数据字典

    Returns:

    """
    if not news_item:
        return

    note_id = news_item.get("note_id")
    save_content_item = {
        "note_id": note_id,
        "title": news_item.get("title", ""),
        "desc": news_item.get("desc", ""),
        "source": news_item.get("source", "Yahoo Finance"),
        "note_url": news_item.get("note_url", ""),
        "publish_time": news_item.get("publish_time", 0),
        "keyword": news_item.get("keyword", ""),
        "platform": news_item.get("platform", "yahoo_finance"),
        "last_modify_ts": utils.get_current_timestamp(),
    }

    utils.logger.info(
        f"[store.yahoo_finance.update_yahoo_finance_news] Yahoo Finance news id: {note_id}, title: {save_content_item.get('title', '')[:50]} ..."
    )
    await YahooFinanceStoreFactory.create_store().store_content(content_item=save_content_item)
