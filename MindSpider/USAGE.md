# MindSpider 使用指南

## 📋 目录

1. [系统架构](#系统架构)
2. [基础命令](#基础命令)
3. [工作模式](#工作模式)
4. [Yahoo Finance 集成使用](#yahoo-finance-集成使用)
5. [完整示例](#完整示例)

---

## 系统架构

MindSpider 包含两个核心模块:

```
MindSpider/
├── main.py                          # 主入口 (统一调度器)
├── config.py                        # 全局配置 (数据库、LLM API)
├── BroadTopicExtraction/            # 模块1: 话题提取
│   └── main.py                      # 从13个平台提取热点话题
└── DeepSentimentCrawling/           # 模块2: 深度爬取
    └── MediaCrawler/                # 社交媒体爬虫
        ├── main.py                  # MediaCrawler 入口
        ├── config/
        │   └── base_config.py       # 爬虫配置 (平台、关键词)
        └── media_platform/
            ├── weibo/               # 微博爬虫
            ├── xhs/                 # 小红书爬虫
            ├── zhihu/               # 知乎爬虫
            └── yahoo_finance/       # Yahoo Finance 爬虫 (新增)
```

---

## 基础命令

### 1. 查看项目状态

```bash
cd /Users/niuqh/Desktop/github/niuqh/BettaFish/MindSpider
source ../MP-venv/bin/activate
python main.py --status
```

**输出信息:**
- ✅ 配置状态 (数据库、API密钥)
- ✅ 数据库连接状态
- ✅ 数据库表状态
- ✅ Python依赖状态
- ✅ 各模块存在性

---

### 2. 项目初始化

首次使用或重置项目时运行:

```bash
python main.py --setup
```

**执行步骤:**
1. 检查配置文件 (.env)
2. 检查 Python 依赖包
3. 测试数据库连接
4. 创建必要的数据库表

---

### 3. 数据库初始化

如果数据库表损坏或需要重建:

```bash
python main.py --init-db
```

---

## 工作模式

MindSpider 有 3 种运行模式:

### 模式 1: 话题提取 (Broad Topic Extraction)

**功能:** 从13个热点平台爬取今日新闻,使用 AI 提取金融相关关键词

**命令:**
```bash
python main.py --broad-topic --keywords-count 100
```

**参数说明:**
- `--keywords-count N`: 提取最多 N 个关键词 (默认 100)

**数据流向:**
```
13个热点平台 → AI分析 → 提取关键词 → 存入 daily_topics 表
```

**输出:**
- 数据库表: `daily_topics`
- 字段: `id`, `date`, `keywords`, `summary`

---

### 模式 2: 深度爬取 (Deep Sentiment Crawling)

**功能:** 根据已有关键词,在社交媒体平台爬取相关内容和评论

**命令:**
```bash
python main.py --deep-sentiment \
    --platforms wb xhs zhihu \
    --max-keywords 50 \
    --max-notes 50
```

**参数说明:**
- `--platforms`: 指定平台 (可选: xhs, dy, ks, bili, wb, tieba, zhihu)
- `--max-keywords N`: 每个平台最多使用 N 个关键词
- `--max-notes N`: 每个关键词最多爬取 N 条内容
- `--test`: 测试模式 (少量数据)

**数据流向:**
```
daily_topics 关键词 → MediaCrawler → 爬取内容+评论 → 存入各平台表
```

**输出:**
- 数据库表: `weibo_notes`, `xhs_notes`, `zhihu_notes` 等
- 包含内容和评论数据

---

### 模式 3: 完整工作流 (Complete Workflow)

**功能:** 自动运行"话题提取 + 深度爬取"完整流程

**命令:**
```bash
python main.py --complete \
    --keywords-count 100 \
    --max-keywords 50 \
    --max-notes 50
```

**执行流程:**
```
第一步: 话题提取
  ↓
第二步: 深度爬取 (使用提取的关键词)
  ↓
完成
```

---

## Yahoo Finance 集成使用

### 方式 1: 通过 MindSpider 主程序 (推荐)

**步骤 1: 修改 MediaCrawler 配置**

编辑 `DeepSentimentCrawling/MediaCrawler/config/base_config.py`:

```python
# 选择 Yahoo Finance 平台
PLATFORM = "yahoo_finance"

# 设置金融关键词
KEYWORDS = "AAPL,Tesla,Bitcoin,Federal Reserve,inflation,interest rate"

# 爬取类型
CRAWLER_TYPE = "search"

# 控制爬取数量
CRAWLER_MAX_NOTES_COUNT = 50  # 每个关键词爬 50 条新闻

# 请求间隔 (避免被封)
CRAWLER_MAX_SLEEP_SEC = 3

# 数据存储方式
SAVE_DATA_OPTION = "postgresql"  # 或 csv, json, sqlite

# 不爬评论 (Yahoo Finance 没有评论)
ENABLE_GET_COMMENTS = False
```

**步骤 2: 运行 MindSpider**

```bash
cd /Users/niuqh/Desktop/github/niuqh/BettaFish/MindSpider
source ../MP-venv/bin/activate

# 只运行深度爬取 (使用 Yahoo Finance)
python main.py --deep-sentiment --max-notes 50
```

---

### 方式 2: 直接运行 MediaCrawler

如果你只想测试 Yahoo Finance 爬虫:

**步骤 1: 修改配置**

同上,修改 `base_config.py`

**步骤 2: 直接运行**

```bash
cd /Users/niuqh/Desktop/github/niuqh/BettaFish/MindSpider/DeepSentimentCrawling/MediaCrawler
source ../../../MP-venv/bin/activate
python main.py
```

---

## 完整示例

### 示例 1: 金融舆情分析完整流程

**场景:** 分析今日金融热点,并在社交媒体爬取相关讨论

```bash
cd /Users/niuqh/Desktop/github/niuqh/BettaFish/MindSpider
source ../MP-venv/bin/activate

# 运行完整流程
python main.py --complete \
    --keywords-count 100 \
    --platforms wb xhs zhihu \
    --max-keywords 50 \
    --max-notes 50
```

**执行过程:**

1. **话题提取阶段** (5-10分钟)
   - 爬取 13 个热点平台的今日新闻
   - AI 分析提取 100 个金融关键词
   - 存入 `daily_topics` 表

2. **深度爬取阶段** (30-60分钟)
   - 从 `daily_topics` 读取关键词
   - 在微博、小红书、知乎搜索关键词
   - 爬取每个关键词的 50 条内容和评论
   - 存入各平台数据表

---

### 示例 2: 只爬取 Yahoo Finance 财经新闻

**场景:** 获取特定金融事件的新闻报道

**步骤 1: 修改配置**

```bash
cd /Users/niuqh/Desktop/github/niuqh/BettaFish/MindSpider/DeepSentimentCrawling/MediaCrawler
nano config/base_config.py
```

修改以下内容:
```python
PLATFORM = "yahoo_finance"
KEYWORDS = "Apple earnings,Tesla stock,Bitcoin crash,Fed rate decision"
CRAWLER_MAX_NOTES_COUNT = 100
CRAWLER_MAX_SLEEP_SEC = 3
ENABLE_GET_COMMENTS = False
```

**步骤 2: 运行爬虫**

```bash
cd /Users/niuqh/Desktop/github/niuqh/BettaFish/MindSpider/DeepSentimentCrawling/MediaCrawler
source ../../../MP-venv/bin/activate
python main.py
```

**预期输出:**
```
[YahooFinanceCrawler] Begin search Yahoo Finance news
[YahooFinanceCrawler] Current search keyword: Apple earnings
[YahooFinanceCrawler] Fetching page 1 for keyword: Apple earnings
[YahooFinanceCrawler] Saved 10 news items
[YahooFinanceCrawler] News: Apple Q4 Earnings Beat Expectations - https://...
...
```

---

### 示例 3: 测试模式 (快速验证)

**场景:** 快速测试系统是否正常运行

```bash
python main.py --complete --test
```

测试模式特点:
- 只提取 10 个关键词
- 每个关键词只爬 5 条内容
- 不爬取评论
- 总耗时约 5-10 分钟

---

### 示例 4: 指定日期和平台

**场景:** 补爬某一天的数据

```bash
python main.py --deep-sentiment \
    --date 2025-01-10 \
    --platforms wb xhs \
    --max-keywords 30 \
    --max-notes 50
```

---

## 参数速查表

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `--status` | 显示项目状态 | - | `--status` |
| `--setup` | 初始化项目 | - | `--setup` |
| `--init-db` | 初始化数据库 | - | `--init-db` |
| `--broad-topic` | 只运行话题提取 | - | `--broad-topic` |
| `--deep-sentiment` | 只运行深度爬取 | - | `--deep-sentiment` |
| `--complete` | 运行完整流程 | - | `--complete` |
| `--date` | 指定日期 | 今天 | `--date 2025-01-10` |
| `--platforms` | 指定平台 | 全部 | `--platforms wb xhs` |
| `--keywords-count` | 话题提取关键词数 | 100 | `--keywords-count 50` |
| `--max-keywords` | 每平台最大关键词 | 50 | `--max-keywords 30` |
| `--max-notes` | 每关键词最大内容数 | 50 | `--max-notes 100` |
| `--test` | 测试模式 | False | `--test` |

---

## 常见问题

### Q1: Yahoo Finance 数据保存在哪里?

A: 目前数据会打印到日志。你需要实现自定义存储逻辑:

1. 修改 `yahoo_finance/core.py` 的 `save_news_data` 方法
2. 参考其他平台 (如 `weibo`) 的存储实现
3. 将数据保存到数据库或文件

### Q2: 如何只关注金融话题?

A: 修改 `BroadTopicExtraction/topic_extractor.py` 的提示词,添加金融过滤:

```python
**重要:本次分析仅关注金融、经济、投资相关的话题**
```

### Q3: 如何同时使用多个平台?

A: 需要分别运行:

```bash
# 第一次: 爬 Yahoo Finance
修改 base_config.py: PLATFORM = "yahoo_finance"
python MediaCrawler/main.py

# 第二次: 爬微博
修改 base_config.py: PLATFORM = "wb"
python MediaCrawler/main.py
```

或者使用 MindSpider 的 `--platforms` 参数 (不支持 yahoo_finance,需要单独运行)

---

## 技术支持

- 项目路径: `/Users/niuqh/Desktop/github/niuqh/BettaFish/MindSpider`
- 虚拟环境: `../MP-venv`
- 数据库: PostgreSQL (端口 5444)
- Python 版本: 3.11.12
