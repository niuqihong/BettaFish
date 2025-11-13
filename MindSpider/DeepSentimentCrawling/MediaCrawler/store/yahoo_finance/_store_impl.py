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
# @Desc    : Yahoo Finance 存储实现类

from typing import Dict

from sqlalchemy import select

import config
from base.base_crawler import AbstractStore
from database.models import YahooFinanceNews
from tools import utils
from tools.async_file_writer import AsyncFileWriter
from database.db_session import get_session
from var import crawler_type_var


class YahooFinanceCsvStoreImplement(AbstractStore):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.writer = AsyncFileWriter(platform="yahoo_finance", crawler_type=crawler_type_var.get())

    async def store_content(self, content_item: Dict):
        """
        Yahoo Finance news CSV storage implementation
        Args:
            content_item: news item dict

        Returns:

        """
        await self.writer.write_to_csv(item_type="contents", item=content_item)

    async def store_comment(self, comment_item: Dict):
        """
        Yahoo Finance comment CSV storage implementation
        Args:
            comment_item: comment item dict

        Returns:

        """
        await self.writer.write_to_csv(item_type="comments", item=comment_item)

    async def store_creator(self, creator: Dict):
        """
        Yahoo Finance creator CSV storage implementation
        Args:
            creator:

        Returns:

        """
        await self.writer.write_to_csv(item_type="creators", item=creator)


class YahooFinanceDbStoreImplement(AbstractStore):

    async def store_content(self, content_item: Dict):
        """
        Yahoo Finance news DB storage implementation
        Args:
            content_item: news item dict

        Returns:

        """
        note_id = content_item.get("note_id")
        async with get_session() as session:
            stmt = select(YahooFinanceNews).where(YahooFinanceNews.note_id == note_id)
            res = await session.execute(stmt)
            db_news = res.scalar_one_or_none()
            if db_news:
                db_news.last_modify_ts = utils.get_current_timestamp()
                for key, value in content_item.items():
                    if hasattr(db_news, key):
                        setattr(db_news, key, value)
            else:
                content_item["add_ts"] = utils.get_current_timestamp()
                content_item["last_modify_ts"] = utils.get_current_timestamp()
                db_news = YahooFinanceNews(**content_item)
                session.add(db_news)
            await session.commit()

    async def store_comment(self, comment_item: Dict):
        """
        Yahoo Finance comment DB storage implementation
        Args:
            comment_item: comment item dict

        Returns:

        """
        # Yahoo Finance 暂不支持评论存储
        pass

    async def store_creator(self, creator: Dict):
        """
        Yahoo Finance creator DB storage implementation
        Args:
            creator:

        Returns:

        """
        # Yahoo Finance 暂不支持创作者存储
        pass


class YahooFinanceJsonStoreImplement(AbstractStore):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.writer = AsyncFileWriter(platform="yahoo_finance", crawler_type=crawler_type_var.get())

    async def store_content(self, content_item: Dict):
        """
        News JSON storage implementation
        Args:
            content_item:

        Returns:

        """
        await self.writer.write_single_item_to_json(item_type="contents", item=content_item)

    async def store_comment(self, comment_item: Dict):
        """
        Comment JSON storage implementation
        Args:
            comment_item:

        Returns:

        """
        await self.writer.write_single_item_to_json(item_type="comments", item=comment_item)

    async def store_creator(self, creator: Dict):
        """
        Creator JSON storage implementation
        Args:
            creator:

        Returns:

        """
        await self.writer.write_single_item_to_json(item_type="creators", item=creator)


class YahooFinanceSqliteStoreImplement(YahooFinanceDbStoreImplement):
    """
    Yahoo Finance news SQLite storage implementation
    """
    pass
