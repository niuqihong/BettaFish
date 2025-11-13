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
# @Desc    : Yahoo Finance 爬虫 API 请求 client

import asyncio
from typing import Dict, List, Optional
from urllib.parse import urlencode

import httpx
from playwright.async_api import BrowserContext, Page

import config
from tools import utils

from .exception import DataFetchError
from .field import NewsTimeRange, SearchType


class YahooFinanceClient:
    """Yahoo Finance 客户端"""

    def __init__(
        self,
        timeout=60,
        proxy=None,
        *,
        headers: Dict[str, str],
        playwright_page: Page,
        cookie_dict: Dict[str, str],
    ):
        self.proxy = proxy
        self.timeout = timeout
        self.headers = headers
        self._host = "https://finance.yahoo.com"
        self._api_host = "https://query2.finance.yahoo.com"
        self.playwright_page = playwright_page
        self.cookie_dict = cookie_dict

    async def request(self, method: str, url: str, **kwargs) -> Dict:
        """发送HTTP请求,支持重试和指数退避"""
        import random

        max_retries = 5  # 最大重试次数
        base_delay = 2  # 基础延迟(秒)

        for attempt in range(max_retries):
            try:
                # 在每次请求前添加随机延迟,避免请求过于频繁
                if attempt > 0:
                    # 指数退避: 2^attempt * base_delay + 随机抖动
                    delay = (2 ** attempt) * base_delay + random.uniform(0, 1)
                    utils.logger.info(
                        f"[YahooFinanceClient.request] Retry {attempt}/{max_retries}, waiting {delay:.2f}s"
                    )
                    await asyncio.sleep(delay)
                else:
                    # 首次请求也添加小延迟
                    await asyncio.sleep(random.uniform(1, 2))

                async with httpx.AsyncClient(proxy=self.proxy) as client:
                    response = await client.request(
                        method, url, timeout=self.timeout, **kwargs
                    )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # 速率限制,需要重试
                    utils.logger.warning(
                        f"[YahooFinanceClient.request] Rate limited (429) on attempt {attempt + 1}/{max_retries}"
                    )
                    if attempt == max_retries - 1:
                        raise DataFetchError(f"HTTP 429 - Rate limit exceeded after {max_retries} retries")
                    continue
                else:
                    # 其他错误状态码
                    utils.logger.error(
                        f"[YahooFinanceClient.request] request {method}:{url} failed, status:{response.status_code}"
                    )
                    raise DataFetchError(f"HTTP {response.status_code}")

            except httpx.TimeoutException as e:
                utils.logger.warning(
                    f"[YahooFinanceClient.request] Timeout on attempt {attempt + 1}/{max_retries}: {e}"
                )
                if attempt == max_retries - 1:
                    raise DataFetchError(f"Request timeout after {max_retries} retries")
                continue
            except httpx.RequestError as e:
                utils.logger.warning(
                    f"[YahooFinanceClient.request] Request error on attempt {attempt + 1}/{max_retries}: {e}"
                )
                if attempt == max_retries - 1:
                    raise DataFetchError(f"Request failed after {max_retries} retries: {e}")
                continue

        raise DataFetchError(f"Request failed after {max_retries} retries")

    async def get(self, uri: str, params=None, headers=None) -> Dict:
        """GET 请求"""
        final_uri = uri
        if isinstance(params, dict):
            final_uri = f"{uri}?{urlencode(params)}"

        if headers is None:
            headers = self.headers

        return await self.request(
            method="GET", url=f"{self._api_host}{final_uri}", headers=headers
        )

    async def pong(self) -> bool:
        """检查连接状态"""
        utils.logger.info("[YahooFinanceClient.pong] Begin pong Yahoo Finance...")
        try:
            # Yahoo Finance 不需要登录,直接返回 True
            return True
        except Exception as e:
            utils.logger.error(f"[YahooFinanceClient.pong] Pong failed: {e}")
            return False

    async def update_cookies(self, browser_context: BrowserContext):
        """更新 cookies"""
        cookie_str, cookie_dict = utils.convert_cookies(
            await browser_context.cookies()
        )
        self.headers["Cookie"] = cookie_str
        self.cookie_dict = cookie_dict

    async def search_news(
        self,
        keyword: str,
        search_type: SearchType = SearchType.NEWS,
        time_range: NewsTimeRange = NewsTimeRange.ANY_TIME,
        offset: int = 0,
        count: int = 10,
    ) -> Dict:
        """
        搜索新闻

        Args:
            keyword: 搜索关键词
            search_type: 搜索类型
            time_range: 时间范围
            offset: 偏移量
            count: 返回数量

        Returns:
            搜索结果
        """
        utils.logger.info(
            f"[YahooFinanceClient.search_news] Searching news for keyword: {keyword}"
        )

        params = {
            "q": keyword,
            "type": search_type.value,
            "offset": offset,
            "count": count,
        }

        if time_range.value:
            params["freshness"] = time_range.value

        try:
            uri = "/v1/finance/search"
            result = await self.get(uri, params=params)
            return result
        except Exception as e:
            utils.logger.error(
                f"[YahooFinanceClient.search_news] Search failed: {e}"
            )
            raise DataFetchError(f"Search news failed: {e}")

    async def get_quote_summary(self, symbol: str) -> Dict:
        """
        获取股票概要信息

        Args:
            symbol: 股票代码 (如 AAPL, MSFT)

        Returns:
            股票概要信息
        """
        utils.logger.info(
            f"[YahooFinanceClient.get_quote_summary] Getting quote for: {symbol}"
        )

        params = {
            "symbols": symbol,
            "modules": "assetProfile,summaryProfile,summaryDetail,esgScores,"
            "price,incomeStatementHistory,incomeStatementHistoryQuarterly,"
            "balanceSheetHistory,balanceSheetHistoryQuarterly,"
            "cashflowStatementHistory,cashflowStatementHistoryQuarterly,"
            "defaultKeyStatistics,financialData,calendarEvents,"
            "secFilings,recommendationTrend,upgradeDowngradeHistory,"
            "institutionOwnership,fundOwnership,majorDirectHolders,"
            "majorHoldersBreakdown,insiderTransactions,insiderHolders,"
            "netSharePurchaseActivity,earnings,earningsHistory,earningsTrend,"
            "industryTrend,indexTrend,sectorTrend",
        }

        try:
            uri = "/v10/finance/quoteSummary/" + symbol
            result = await self.get(uri, params=params)
            return result
        except Exception as e:
            utils.logger.error(
                f"[YahooFinanceClient.get_quote_summary] Get quote failed: {e}"
            )
            raise DataFetchError(f"Get quote summary failed: {e}")

    async def get_trending_tickers(self, region: str = "US", count: int = 10) -> Dict:
        """
        获取热门股票

        Args:
            region: 地区代码 (US, CN, HK等)
            count: 返回数量

        Returns:
            热门股票列表
        """
        utils.logger.info(
            f"[YahooFinanceClient.get_trending_tickers] Getting trending tickers for region: {region}"
        )

        params = {"region": region, "count": count}

        try:
            uri = "/v1/finance/trending/" + region
            result = await self.get(uri, params=params)
            return result
        except Exception as e:
            utils.logger.error(
                f"[YahooFinanceClient.get_trending_tickers] Get trending tickers failed: {e}"
            )
            raise DataFetchError(f"Get trending tickers failed: {e}")
