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
# @Desc    : Yahoo Finance 爬虫主流程代码

import asyncio
import random
from typing import Dict, List, Optional

from playwright.async_api import (
    BrowserContext,
    BrowserType,
    Page,
    async_playwright,
)

import config
from base.base_crawler import AbstractCrawler
from proxy.proxy_ip_pool import IpInfoModel, create_ip_pool
from store import yahoo_finance as yahoo_finance_store
from tools import utils
from tools.cdp_browser import CDPBrowserManager
from var import crawler_type_var, source_keyword_var

from .client import YahooFinanceClient
from .exception import DataFetchError
from .field import NewsTimeRange, SearchType


class YahooFinanceCrawler(AbstractCrawler):
    """Yahoo Finance 爬虫"""

    context_page: Page
    yf_client: YahooFinanceClient
    browser_context: BrowserContext
    cdp_manager: Optional[CDPBrowserManager]

    def __init__(self):
        self.index_url = "https://finance.yahoo.com"
        self.user_agent = utils.get_user_agent()
        self.cdp_manager = None

    async def start(self):
        """启动爬虫"""
        playwright_proxy_format, httpx_proxy_format = None, None
        if config.ENABLE_IP_PROXY:
            ip_proxy_pool = await create_ip_pool(
                config.IP_PROXY_POOL_COUNT, enable_validate_ip=True
            )
            ip_proxy_info: IpInfoModel = await ip_proxy_pool.get_proxy()
            playwright_proxy_format, httpx_proxy_format = utils.format_proxy_info(
                ip_proxy_info
            )

        async with async_playwright() as playwright:
            # 根据配置选择启动模式
            if config.ENABLE_CDP_MODE:
                utils.logger.info("[YahooFinanceCrawler] 使用CDP模式启动浏览器")
                self.browser_context = await self.launch_browser_with_cdp(
                    playwright,
                    playwright_proxy_format,
                    self.user_agent,
                    headless=config.CDP_HEADLESS,
                )
            else:
                utils.logger.info("[YahooFinanceCrawler] 使用标准模式启动浏览器")
                chromium = playwright.chromium
                self.browser_context = await self.launch_browser(
                    chromium, None, self.user_agent, headless=config.HEADLESS
                )

                # stealth.min.js 防止网站检测爬虫
                await self.browser_context.add_init_script(path="libs/stealth.min.js")

            self.context_page = await self.browser_context.new_page()
            await self.context_page.goto(self.index_url)

            # 创建客户端
            self.yf_client = await self.create_yahoo_finance_client(
                httpx_proxy_format
            )
            if not await self.yf_client.pong():
                utils.logger.error(
                    "[YahooFinanceCrawler.start] Yahoo Finance connection failed"
                )
                return

            crawler_type_var.set(config.CRAWLER_TYPE)
            if config.CRAWLER_TYPE == "search":
                # 搜索新闻
                await self.search()
            else:
                utils.logger.info(
                    f"[YahooFinanceCrawler.start] Unsupported crawler type: {config.CRAWLER_TYPE}"
                )

            utils.logger.info("[YahooFinanceCrawler.start] Yahoo Finance Crawler finished...")

    async def search(self):
        """搜索新闻"""
        utils.logger.info("[YahooFinanceCrawler.search] Begin search Yahoo Finance news")

        for keyword in config.KEYWORDS.split(","):
            source_keyword_var.set(keyword)
            utils.logger.info(
                f"[YahooFinanceCrawler.search] Current search keyword: {keyword}"
            )

            page = 0
            max_note_len = config.CRAWLER_MAX_NOTES_COUNT

            page_size = 5

            while page * page_size < max_note_len:
                try:
                    utils.logger.info(
                        f"[YahooFinanceCrawler.search] Fetching page {page + 1} for keyword: {keyword}"
                    )

                    # 搜索新闻
                    result = await self.yf_client.search_news(
                        keyword=keyword,
                        search_type=SearchType.NEWS,
                        time_range=NewsTimeRange.ANY_TIME,
                        offset=page * page_size,
                        count=page_size,
                    )

                    # 解析新闻数据
                    news_list = self.parse_search_result(result, keyword)

                    if not news_list:
                        utils.logger.info(
                            f"[YahooFinanceCrawler.search] No more news for keyword: {keyword}"
                        )
                        break

                    # 保存新闻数据
                    await self.save_news_data(news_list)

                    utils.logger.info(
                        f"[YahooFinanceCrawler.search] Saved {len(news_list)} news items"
                    )

                    page += 1
                    sleep_time = config.CRAWLER_MAX_SLEEP_SEC + random.uniform(1, 3)
                    utils.logger.info(
                        f"[YahooFinanceCrawler.search] Sleeping {sleep_time:.2f}s before next page to avoid rate limits"
                    )
                    await asyncio.sleep(sleep_time)

                except DataFetchError as e:
                    if "429" in str(e):
                        backoff = 60
                        utils.logger.warning(
                            f"[YahooFinanceCrawler.search] Hit Yahoo Finance rate limit, backing off {backoff}s (page {page + 1}, keyword: {keyword})"
                        )
                        await asyncio.sleep(backoff)
                        continue
                    utils.logger.error(
                        f"[YahooFinanceCrawler.search] Fetch page {page + 1} failed: {e}"
                    )
                    break
                except Exception as e:
                    utils.logger.error(
                        f"[YahooFinanceCrawler.search] Unexpected error: {e}"
                    )
                    break

    def parse_search_result(self, result: Dict, keyword: str) -> List[Dict]:
        """
        解析搜索结果

        Args:
            result: API返回结果
            keyword: 搜索关键词

        Returns:
            新闻列表
        """
        news_list = []

        try:
            # Yahoo Finance API 返回的数据结构
            quotes = result.get("quotes", [])

            for item in quotes:
                # 只处理新闻类型的数据
                if item.get("quoteType") != "NEWS":
                    continue

                news_item = {
                    "note_id": item.get("uuid", ""),
                    "title": item.get("title", ""),
                    "desc": item.get("description", ""),
                    "source": item.get("publisher", "Yahoo Finance"),
                    "note_url": item.get("link", ""),
                    "publish_time": item.get("providerPublishTime", 0),
                    "keyword": keyword,
                    "platform": "yahoo_finance",
                }

                news_list.append(news_item)

        except Exception as e:
            utils.logger.error(
                f"[YahooFinanceCrawler.parse_search_result] Parse result failed: {e}"
            )

        return news_list

    async def save_news_data(self, news_list: List[Dict]):
        """
        保存新闻数据

        Args:
            news_list: 新闻列表
        """
        if not news_list:
            return

        utils.logger.info(
            f"[YahooFinanceCrawler.save_news_data] Saving {len(news_list)} news items"
        )

        # 批量保存新闻数据
        await yahoo_finance_store.batch_update_yahoo_finance_news(news_list)

    async def create_yahoo_finance_client(self, httpx_proxy: Optional[str]) -> YahooFinanceClient:
        """
        创建 Yahoo Finance 客户端

        Args:
            httpx_proxy: 代理地址

        Returns:
            YahooFinanceClient 实例
        """
        utils.logger.info("[YahooFinanceCrawler.create_yahoo_finance_client] Creating client...")

        cookie_str, cookie_dict = utils.convert_cookies(
            await self.browser_context.cookies()
        )

        yf_client = YahooFinanceClient(
            timeout=60,
            proxy=httpx_proxy,
            headers={
                "User-Agent": self.user_agent,
                "Cookie": cookie_str,
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9",
            },
            playwright_page=self.context_page,
            cookie_dict=cookie_dict,
        )

        return yf_client

    async def launch_browser(
        self,
        chromium: BrowserType,
        playwright_proxy: Optional[Dict],
        user_agent: Optional[str],
        headless: bool = True,
    ) -> BrowserContext:
        """
        启动浏览器

        Args:
            chromium: Chromium浏览器类型
            playwright_proxy: 代理配置
            user_agent: 用户代理
            headless: 是否无头模式

        Returns:
            浏览器上下文
        """
        utils.logger.info("[YahooFinanceCrawler.launch_browser] Begin create browser context...")

        browser_context = await chromium.launch(
            headless=headless,
            proxy=playwright_proxy,
        )

        # 创建新的上下文
        context = await browser_context.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=user_agent,
        )

        return context
