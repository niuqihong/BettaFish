# Yahoo Finance 集成完成 ✅

## 🎉 已完成的工作

Yahoo Finance 爬虫已经完全集成到 MindSpider 系统中！

### 1️⃣ 已添加的文件

```
MindSpider/
└── DeepSentimentCrawling/
    └── MediaCrawler/
        ├── media_platform/
        │   └── yahoo_finance/              ← 新增
        │       ├── __init__.py
        │       ├── client.py              # HTTP 客户端
        │       ├── core.py                # 爬虫核心逻辑
        │       ├── field.py               # 字段定义
        │       ├── exception.py           # 异常处理
        │       └── README.md              # 使用文档
        ├── main.py                        ← 已注册 yahoo_finance
        └── cmd_arg/
            └── arg.py                     ← 已添加 YAHOO_FINANCE 枚举
```

### 2️⃣ 已修改的配置

#### ✅ MediaCrawler 主程序
- **文件**: `DeepSentimentCrawling/MediaCrawler/main.py`
- **修改**: 添加 `YahooFinanceCrawler` 到爬虫工厂

```python
class CrawlerFactory:
    CRAWLERS = {
        "xhs": XiaoHongShuCrawler,
        "dy": DouYinCrawler,
        "ks": KuaishouCrawler,
        "bili": BilibiliCrawler,
        "wb": WeiboCrawler,
        "tieba": TieBaCrawler,
        "zhihu": ZhihuCrawler,
        "yahoo_finance": YahooFinanceCrawler,  # ← 新增
    }
```

#### ✅ 命令行参数支持
- **文件**: `DeepSentimentCrawling/MediaCrawler/cmd_arg/arg.py`
- **修改**: 添加 Yahoo Finance 到平台枚举

```python
class PlatformEnum(str, Enum):
    XHS = "xhs"
    DOUYIN = "dy"
    KUAISHOU = "ks"
    BILIBILI = "bili"
    WEIBO = "wb"
    TIEBA = "tieba"
    ZHIHU = "zhihu"
    YAHOO_FINANCE = "yahoo_finance"  # ← 新增
```

#### ✅ MindSpider 主程序
- **文件**: `MindSpider/main.py`
- **修改**: 添加 yahoo_finance 到支持的平台列表

```python
parser.add_argument("--platforms", type=str, nargs='+',
                   choices=['xhs', 'dy', 'ks', 'bili', 'wb', 'tieba', 'zhihu', 'yahoo_finance'],
                   help="指定爬取平台")
```

#### ✅ DeepSentimentCrawling 模块
- **文件**: `DeepSentimentCrawling/main.py`
- **修改**: 添加 yahoo_finance 到支持的平台

```python
self.supported_platforms = ['xhs', 'dy', 'ks', 'bili', 'wb', 'tieba', 'zhihu', 'yahoo_finance']
```

---

## 🚀 使用方法

### 方式 1: 通过 MindSpider 主程序 (推荐)

#### 爬取单个平台

```bash
cd /Users/niuqh/Desktop/github/niuqh/BettaFish/MindSpider
source ../MP-venv/bin/activate

# 只爬 Yahoo Finance
python main.py --deep-sentiment --platforms yahoo_finance --max-notes 50
```

#### 爬取多个平台 (包括 Yahoo Finance)

```bash
# 爬取微博、小红书和 Yahoo Finance
python main.py --deep-sentiment \
    --platforms wb xhs yahoo_finance \
    --max-keywords 30 \
    --max-notes 50
```

#### 爬取所有平台 (包括 Yahoo Finance)

```bash
# 不指定 --platforms，现在会爬取全部 8 个平台
python main.py --complete --max-notes 50
```

---

### 方式 2: 通过 MediaCrawler 直接调用

```bash
cd /Users/niuqh/Desktop/github/niuqh/BettaFish/MindSpider/DeepSentimentCrawling/MediaCrawler
source ../../../MP-venv/bin/activate

# 使用命令行参数
python main.py \
    --platform yahoo_finance \
    --keywords "AAPL,Tesla,Bitcoin,Federal Reserve" \
    --type search \
    --get_comment false \
    --save_data_option postgresql
```

---

### 方式 3: 使用自动化脚本

```bash
cd /Users/niuqh/Desktop/github/niuqh/BettaFish/MindSpider

# 爬取所有 8 个平台 (包括 Yahoo Finance)
./crawl_all_platforms.sh "AAPL,Tesla,Bitcoin"

# 使用默认金融关键词
./crawl_all_platforms.sh
```

---

## 📊 支持的平台列表

| 平台代码 | 平台名称 | 需要登录 | 支持评论 | 数据类型 |
|---------|---------|---------|---------|---------|
| `xhs` | 小红书 | ✅ | ✅ | 社交媒体 |
| `dy` | 抖音 | ✅ | ✅ | 短视频 |
| `ks` | 快手 | ✅ | ✅ | 短视频 |
| `bili` | 哔哩哔哩 | ✅ | ✅ | 视频 |
| `wb` | 微博 | ✅ | ✅ | 社交媒体 |
| `tieba` | 百度贴吧 | ✅ | ✅ | 论坛 |
| `zhihu` | 知乎 | ✅ | ✅ | 问答社区 |
| `yahoo_finance` | 雅虎财经 | ❌ | ❌ | 财经新闻 |

---

## 🔍 常用命令示例

### 示例 1: 金融新闻专项爬取

```bash
# 只爬 Yahoo Finance 的财经新闻
python main.py --deep-sentiment \
    --platforms yahoo_finance \
    --max-keywords 50 \
    --max-notes 100
```

### 示例 2: 社交媒体 + 财经新闻组合

```bash
# 爬取微博舆情 + Yahoo Finance 新闻
python main.py --deep-sentiment \
    --platforms wb yahoo_finance \
    --max-keywords 30 \
    --max-notes 50
```

### 示例 3: 完整舆情分析流程

```bash
# 1. 话题提取 + 2. 所有平台爬取 (包括 Yahoo Finance)
python main.py --complete \
    --keywords-count 100 \
    --max-keywords 50 \
    --max-notes 50
```

### 示例 4: 测试模式

```bash
# 快速测试 Yahoo Finance 是否正常工作
cd DeepSentimentCrawling/MediaCrawler
python main.py \
    --platform yahoo_finance \
    --keywords "Apple" \
    --type search
```

---

## 💡 使用建议

### 1. 关键词选择

**Yahoo Finance 适合的关键词:**
```
# 股票代码
AAPL, TSLA, MSFT, GOOGL, AMZN

# 公司名称
Apple, Tesla, Microsoft, Google, Amazon

# 金融术语
Federal Reserve, interest rate, inflation, stock market, Bitcoin, cryptocurrency

# 经济指标
GDP, unemployment rate, CPI, PPI, NFP
```

**中文平台适合的关键词:**
```
股市, A股, 美股, 港股, 上证指数, 沪深300
基金, 理财, 投资, 金融
利率, 通胀, 美联储, 央行
```

### 2. 数据量控制

```bash
# 快速测试 (每个关键词 10 条)
--max-notes 10

# 常规使用 (每个关键词 50 条)
--max-notes 50

# 深度爬取 (每个关键词 100 条)
--max-notes 100
```

### 3. 组合策略

**场景 1: 只需要财经新闻**
```bash
python main.py --deep-sentiment --platforms yahoo_finance
```

**场景 2: 需要舆情分析**
```bash
python main.py --deep-sentiment --platforms wb xhs zhihu
```

**场景 3: 完整分析 (新闻 + 舆情)**
```bash
python main.py --deep-sentiment --platforms wb xhs yahoo_finance
```

---

## ⚙️ 配置文件说明

### 默认关键词配置

如果不想每次都传 `--keywords`，可以修改配置文件：

**文件**: `DeepSentimentCrawling/MediaCrawler/config/base_config.py`

```python
# 修改默认关键词为金融相关
KEYWORDS = "AAPL,Tesla,Bitcoin,Federal Reserve,inflation,stock market,GDP"

# 修改默认平台
PLATFORM = "yahoo_finance"

# 关闭评论爬取 (Yahoo Finance 没有评论)
ENABLE_GET_COMMENTS = False
```

然后可以直接运行:
```bash
cd DeepSentimentCrawling/MediaCrawler
python main.py  # 使用默认配置
```

---

## 🐛 故障排查

### 问题 1: ModuleNotFoundError

```bash
ModuleNotFoundError: No module named 'yahoo_finance'
```

**解决方案:**
```bash
# 确认虚拟环境已激活
source ../MP-venv/bin/activate

# 确认在正确的目录
cd /Users/niuqh/Desktop/github/niuqh/BettaFish/MindSpider
```

### 问题 2: 平台不在支持列表

```bash
error: argument --platforms: invalid choice: 'yahoo_finance'
```

**解决方案:**
- 确认已更新 `main.py` 的平台列表
- 使用最新代码

### 问题 3: 没有数据返回

```bash
[YahooFinanceCrawler] No more news for keyword: xxx
```

**可能原因:**
1. 关键词拼写错误
2. Yahoo Finance API 限制
3. 网络连接问题

**解决方案:**
- 使用常见的英文关键词 (如 "Apple", "Tesla")
- 增加请求间隔时间 (修改 `CRAWLER_MAX_SLEEP_SEC`)

---

## 📝 数据存储

### 数据保存位置

Yahoo Finance 爬取的数据会存储到:

**数据库表** (如果使用 postgresql):
- 需要创建对应的表结构 (参考其他平台)

**日志文件**:
- 当前数据会打印到日志中
- 可以在 `save_news_data` 方法中实现自定义存储

### 自定义存储

编辑 `media_platform/yahoo_finance/core.py`:

```python
async def save_news_data(self, news_list: List[Dict]):
    """保存新闻数据"""
    # 方案 1: 保存到数据库
    # await db.insert_yahoo_finance_news(news_list)

    # 方案 2: 保存到 JSON 文件
    # with open('yahoo_finance_data.json', 'a') as f:
    #     json.dump(news_list, f, indent=2)

    # 方案 3: 保存到 CSV
    # import pandas as pd
    # df = pd.DataFrame(news_list)
    # df.to_csv('yahoo_finance_data.csv', mode='a')
```

---

## 🎯 下一步

1. **测试运行**: 运行一次测试，验证所有功能正常
2. **数据存储**: 根据需求实现数据库存储逻辑
3. **定时任务**: 设置定时任务，每日自动爬取

---

## ✅ 验证清单

- [x] Yahoo Finance 爬虫代码已创建
- [x] 已注册到 MediaCrawler 主程序
- [x] 已添加到命令行参数支持
- [x] 已集成到 MindSpider 主程序
- [x] 已更新 DeepSentimentCrawling 模块
- [x] 创建了自动化脚本
- [x] 编写了完整使用文档

---

## 📞 支持

如有问题，请查看:
- Yahoo Finance 爬虫文档: `media_platform/yahoo_finance/README.md`
- MindSpider 使用指南: `USAGE.md`
- 测试脚本: `test_yahoo_finance.py`
