# Yahoo Finance 爬虫

## 简介

Yahoo Finance 爬虫用于获取金融新闻、股票行情等数据,支持关键词搜索功能。

## 功能特性

- 🔍 **关键词搜索新闻**: 根据关键词搜索 Yahoo Finance 的金融新闻
- 📊 **股票行情获取**: 获取指定股票代码的概要信息
- 🔥 **热门股票**: 获取指定地区的热门股票列表
- ⏰ **时间筛选**: 支持按时间范围筛选新闻(过去一天/一周/一月)

## 配置说明

### 1. 修改平台配置

编辑 `MediaCrawler/config/base_config.py`:

```python
# 设置平台为 yahoo_finance
PLATFORM = "yahoo_finance"

# 设置搜索关键词(英文逗号分隔)
# 支持股票代码、公司名称、金融术语等
KEYWORDS = "AAPL,Tesla,Bitcoin,Federal Reserve,inflation"

# 爬取类型
CRAWLER_TYPE = "search"  # 目前只支持 search 模式

# 最大爬取数量
CRAWLER_MAX_NOTES_COUNT = 50
```

### 2. 运行爬虫

```bash
cd MindSpider/DeepSentimentCrawling/MediaCrawler
python main.py
```

## API 接口说明

### 搜索新闻

```python
await client.search_news(
    keyword="AAPL",                      # 搜索关键词
    search_type=SearchType.NEWS,         # 搜索类型
    time_range=NewsTimeRange.PAST_WEEK,  # 时间范围
    offset=0,                            # 偏移量
    count=10                             # 返回数量
)
```

### 获取股票信息

```python
await client.get_quote_summary(symbol="AAPL")
```

### 获取热门股票

```python
await client.get_trending_tickers(region="US", count=10)
```

## 数据字段

爬取的新闻数据包含以下字段:

| 字段 | 说明 | 示例 |
|------|------|------|
| note_id | 新闻唯一ID | uuid字符串 |
| title | 新闻标题 | "Apple Stock Hits New High" |
| desc | 新闻描述 | 新闻摘要内容 |
| source | 新闻来源 | "Yahoo Finance" |
| note_url | 新闻链接 | https://... |
| publish_time | 发布时间戳 | 1699999999 |
| keyword | 搜索关键词 | "AAPL" |
| platform | 平台标识 | "yahoo_finance" |

## 注意事项

1. **API限制**: Yahoo Finance API 可能有访问频率限制,建议设置合理的 `CRAWLER_MAX_SLEEP_SEC`
2. **关键词选择**:
   - 股票代码: AAPL, TSLA, MSFT 等
   - 公司名称: Apple, Tesla, Microsoft 等
   - 金融术语: inflation, interest rate, Federal Reserve 等
3. **无需登录**: Yahoo Finance 大部分接口无需登录即可访问
4. **数据存储**: 目前数据会打印到日志,可以根据需要实现自定义存储逻辑

## 扩展开发

### 添加新的搜索类型

在 `field.py` 中添加新的枚举值:

```python
class SearchType(Enum):
    NEWS = "news"
    QUOTES = "quotes"
    ALL = "all"
    YOUR_NEW_TYPE = "your_value"  # 添加新类型
```

### 自定义数据存储

在 `core.py` 的 `save_news_data` 方法中实现自定义存储逻辑:

```python
async def save_news_data(self, news_list: List[Dict]):
    # 实现你的存储逻辑
    # 可以参考 weibo 的存储实现
    pass
```

## 文件结构

```
yahoo_finance/
├── __init__.py      # 模块导出
├── client.py        # HTTP 客户端
├── core.py          # 爬虫核心逻辑
├── field.py         # 字段定义
├── exception.py     # 异常定义
└── README.md        # 本文档
```

## 常见问题

### Q1: 如何只爬取金融相关的新闻?

A: 在 KEYWORDS 中设置金融相关的关键词,例如:
```python
KEYWORDS = "股市,A股,美股,港股,上证指数,基金,理财,投资,金融,利率,通胀,美联储,央行"
```

### Q2: 数据保存在哪里?

A: 目前数据会打印到日志中。你可以:
1. 修改 `save_news_data` 方法实现数据库存储
2. 参考其他平台(如 weibo)的存储实现
3. 将数据保存为 JSON/CSV 文件

### Q3: 支持中文搜索吗?

A: Yahoo Finance 主要是英文内容,建议使用英文关键词。如果需要中文金融资讯,可以考虑添加其他平台。

## 许可声明

本代码仅供学习和研究目的使用。使用者应遵守:
1. 不得用于任何商业用途
2. 遵守 Yahoo Finance 的使用条款和 robots.txt 规则
3. 不得进行大规模爬取或对平台造成运营干扰
4. 合理控制请求频率
5. 不得用于任何非法或不当的用途
