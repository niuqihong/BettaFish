# BettaFish（微舆）系统架构说明书

> 版本：1.0  
> 生成日期：2025-11-12  
> 系统名称：BettaFish（微舆） - 多智能体公共舆情分析系统

---

## 一、系统概述

### 1.1 系统简介

BettaFish（微舆）是一个基于多智能体协作的公共舆情分析系统，能够自动爬取30+社交媒体平台数据，并使用AI智能体进行百万级评论分析。系统采用模块化架构，通过专业化引擎（Engine）实现不同维度的数据处理和分析任务。

### 1.2 核心特性

- **多平台爬虫**：支持小红书、抖音、快手、B站、微博、贴吧、知乎、Yahoo Finance等8大平台
- **多智能体协作**：4个专业化智能体（InsightEngine、MediaEngine、QueryEngine、ReportEngine）协同工作
- **论坛式交互**：ForumEngine实现智能体间的辩论讨论机制，避免结果同质化
- **多模态分析**：支持视频、图片、文本的综合分析
- **情感分析**：集成5种情感分析模型，支持22种语言
- **灵活配置**：支持OpenAI兼容的所有LLM API（Kimi、Gemini、DeepSeek、Qwen等）

### 1.3 技术栈

| 层级 | 技术选型 |
|------|---------|
| **Web框架** | Flask + SocketIO（主应用）、Streamlit（单引擎UI） |
| **数据库** | MySQL / PostgreSQL（可配置切换） |
| **异步框架** | asyncio、SQLAlchemy Async、httpx |
| **爬虫技术** | Playwright（CDP模式）、stealth.js反检测 |
| **LLM集成** | OpenAI-compatible API（支持多厂商） |
| **机器学习** | PyTorch、Transformers、XGBoost |
| **编程语言** | Python 3.8+ |

---

## 二、系统架构设计

### 2.1 整体架构

系统采用分层架构设计：

1. **Web应用层**：Flask主应用 + Streamlit单引擎UI
2. **多智能体协作层**：ForumEngine + 4个专业引擎
3. **数据采集层**：MindSpider爬虫系统
4. **数据持久层**：MySQL/PostgreSQL数据库

### 2.2 核心组件

#### 2.2.1 Web应用层（app.py）

**主要职责**：
- 统一管理三个Streamlit单引擎应用（端口8501-8503）
- 提供实时日志流转（通过SocketIO）
- 配置管理API（读写.env配置文件）
- 系统启动编排（初始化数据库、启动ForumEngine）

**关键API路由**：
- `/` - 主控制台页面
- `/api/status` - 获取所有应用状态
- `/api/start/<app>` - 启动指定Engine
- `/api/stop/<app>` - 停止指定Engine
- `/api/config` - 读取/更新配置
- `/api/system/start` - 一键启动完整系统
- `/api/forum/log` - 获取论坛日志

---

## 三、多智能体系统

### 3.1 智能体架构模式

所有智能体遵循统一的LangGraph状态机架构：

**标准目录结构**：
```
{Engine}/
├── agent.py              # 主Agent类，状态机编排
├── nodes/                # 处理节点
│   ├── search_node.py
│   ├── summary_node.py
│   ├── formatting_node.py
│   └── reflection_node.py
├── tools/                # 工具函数
│   ├── search.py
│   ├── keyword_optimizer.py
│   └── sentiment_analyzer.py
├── llms/base.py          # LLM客户端
├── state/state.py        # Agent状态定义
└── prompts/prompts.py    # Prompt模板
```

### 3.2 InsightEngine（数据库挖掘引擎）

**核心能力**：
- 私有数据库查询（5种查询模式）
- SQL关键词优化（使用小参数Qwen模型）
- 多语言情感分析（支持22种语言）
- 多轮反思优化（最多3轮）

**数据源工具集**：
- `get_hot_content()` - 获取热榜内容
- `search_topic_globally()` - 全局话题搜索
- `search_topic_by_date()` - 按日期搜索
- `get_comments_for_topic()` - 获取话题评论
- `search_topic_on_platform()` - 单平台搜索

**推荐模型**：Kimi k2（长上下文处理能力强）

### 3.3 MediaEngine（多模态分析引擎）

**核心能力**：
- 视频内容分析
- 图片内容识别
- 文本综合理解
- 跨模态关联分析

**数据源**：
- Tavily Search API（国际搜索）
- Bocha Web Search API（国内搜索）
- 数据库媒体URL

**推荐模型**：Gemini 2.5 Pro（多模态能力最强）

### 3.4 QueryEngine（网络搜索引擎）

**核心能力**：
- 国内外网络搜索
- 实时新闻聚合
- 事实验证
- 趋势分析

**推荐模型**：DeepSeek Reasoner（推理能力强，成本低）

### 3.5 ReportEngine（报告生成引擎）

**核心能力**：
- 多轮对话式报告生成
- 模板化输出
- 整合三个Engine的分析结果

**推荐模型**：Gemini 2.5 Pro（长文本生成质量高）

---

## 四、ForumEngine（论坛协作机制）

### 4.1 设计理念

ForumEngine是系统的核心创新点，通过模拟"AI论坛讨论"机制，解决多智能体协作中的同质化问题。

**核心思路**：
- 传统方法：各Agent独立运行，缺乏交互
- BettaFish方案：引入"主持人"角色协调讨论

### 4.2 工作原理

**监控流程**：
1. 监控三个log文件（insight.log/media.log/query.log）
2. 检测到FirstSummaryNode输出 → 触发会话开始
3. 清空forum.log，写入会话开始标记
4. 持续捕获SummaryNode输出（JSON格式）
5. 每收集5条Agent发言 → 触发Host生成
6. 各Agent读取forum.log，根据HOST指令调整策略
7. 检测到log文件缩短 → 写入结束标记

### 4.3 关键技术

**日志解析**：
- 支持旧格式和loguru格式
- ERROR块过滤（避免错误内容混入）
- JSON多行捕获
- 线程安全写入

**Host主持人**：
- 使用Qwen3-235B模型
- 分析三个Agent的观点
- 提出新问题或指出分析盲点
- 避免简单总结，要有启发性

---

## 五、MindSpider爬虫系统

### 5.1 两阶段爬取策略

**第一阶段：BroadTopicExtraction（话题提取）**
- 从12+新闻源抓取每日热点
- LLM提取关键词
- 存入daily_topics表

**第二阶段：DeepSentimentCrawling（深度爬取）**
- 读取daily_topics关键词
- 调用MediaCrawler在8个平台搜索
- 存入平台专属表

### 5.2 支持的平台

- weibo（微博）
- xhs（小红书）- 目前已弃用
- douyin（抖音）
- bilibili（B站）
- kuaishou（快手）
- tieba（百度贴吧）
- zhihu（知乎）
- yahoo_finance（Yahoo Finance）

### 5.3 MediaCrawler技术特点

**反检测策略**：
- stealth.js注入
- 随机延迟
- CDP模式
- Cookie管理

**限流处理**：
- 指数退避重试（最多5次）
- 基础延迟2秒，最大64秒
- 随机抖动避免规律性

---

## 六、数据库设计

### 6.1 数据库支持

- MySQL（默认）
- PostgreSQL（推荐用于生产环境）

配置方式：通过.env文件的`DB_DIALECT`参数切换

### 6.2 核心表结构

**话题管理**：
- `daily_news` - 每日新闻
- `daily_topics` - 关键词

**平台内容**（以微博为例）：
- `weibo_note` - 微博笔记
- `weibo_note_comment` - 微博评论

**表命名规范**：
- 内容表：`{platform}_note` 或 `{platform}_video`
- 评论表：`{platform}_note_comment`

---

## 七、配置管理

### 7.1 配置方式

使用pydantic-settings管理，支持：
- 环境变量（优先级最高）
- .env文件（当前目录 > 项目根目录）
- 代码默认值

### 7.2 LLM配置

每个Engine需要三个配置项：
- `{ENGINE}_API_KEY` - API密钥
- `{ENGINE}_BASE_URL` - API端点
- `{ENGINE}_MODEL_NAME` - 模型名称

**推荐配置**：
```bash
# InsightEngine - Kimi
INSIGHT_ENGINE_API_KEY=sk-xxx
INSIGHT_ENGINE_BASE_URL=https://api.moonshot.cn/v1
INSIGHT_ENGINE_MODEL_NAME=kimi-k2-0711-preview

# MediaEngine - Gemini
MEDIA_ENGINE_API_KEY=sk-xxx
MEDIA_ENGINE_BASE_URL=https://aihubmix.com/v1
MEDIA_ENGINE_MODEL_NAME=gemini-2.5-pro

# QueryEngine - DeepSeek
QUERY_ENGINE_API_KEY=sk-xxx
QUERY_ENGINE_BASE_URL=https://api.deepseek.com
QUERY_ENGINE_MODEL_NAME=deepseek-reasoner

# ReportEngine - Gemini
REPORT_ENGINE_API_KEY=sk-xxx
REPORT_ENGINE_BASE_URL=https://aihubmix.com/v1
REPORT_ENGINE_MODEL_NAME=gemini-2.5-pro

# ForumEngine Host - Qwen3
FORUM_HOST_API_KEY=sk-xxx
FORUM_HOST_BASE_URL=https://api.siliconflow.cn/v1
FORUM_HOST_MODEL_NAME=Qwen/Qwen3-235B-A22B-Instruct-2507
```

---

## 八、部署指南

### 8.1 本地开发部署

```bash
# 1. 环境准备
git clone <repo>
cd BettaFish
python3 -m venv MP-venv
source MP-venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt
playwright install chromium

# 3. 配置
cp .env.example .env
# 编辑.env填写配置

# 4. 初始化数据库
cd MindSpider
python main.py --init-db

# 5. 启动应用
cd ..
python app.py
```

访问：http://localhost:5000

### 8.2 Docker部署

```bash
# 启动
docker compose -f b.yml up -d

# 查看日志
docker compose logs -f app

# 停止
docker compose down
```

**重要配置**：
- `DB_HOST=db`（Docker内部服务名）
- 外部访问：localhost:5444
- 容器内部：db:5432

---

## 九、常见问题

### 9.1 数据库连接失败

**解决方案**：
- 检查.env配置
- 确认数据库服务已启动
- Docker部署确认DB_HOST=db

### 9.2 平台登录失败

**解决方案**：
- 启用有头模式（HEADLESS=False）
- 清除browser_data/目录
- 手动扫码登录

### 9.3 HTTP 429限流

**解决方案**：
- 增加CRAWLER_MAX_SLEEP_SEC
- 使用代理/VPN
- 系统已内置重试机制

### 9.4 forum.log无内容

**解决方案**：
- 确认Engine已启动
- 检查是否有SummaryNode输出
- 查看ForumEngine监控状态

---

## 十、扩展开发

### 10.1 添加新爬虫平台

步骤：
1. 创建目录结构
2. 实现AbstractCrawler接口
3. 实现数据存储层
4. 定义数据模型
5. 添加SQL建表语句
6. 注册到CrawlerFactory

### 10.2 添加新智能体

步骤：
1. 创建Engine目录
2. 复制现有Engine模板
3. 实现专业化节点
4. 配置LLM
5. 注册到主应用

---

## 十一、性能优化建议

### 11.1 数据库优化

- 添加索引（create_time、note_id等）
- 使用EXPLAIN分析慢查询
- 调整连接池参数

### 11.2 爬虫优化

- 使用asyncio.Semaphore控制并发
- 批量写入数据库
- 实现增量爬取

### 11.3 LLM优化

- 缓存重复查询
- 使用流式输出
- Prompt压缩减少token

---

## 十二、术语表

| 术语 | 说明 |
|------|------|
| Engine | 智能体引擎 |
| Forum | 论坛协作机制 |
| Host | ForumEngine中的主持人 |
| Agent | 智能体程序 |
| Node | LangGraph处理节点 |
| Crawler | 爬虫程序 |
| CDP | Chrome DevTools Protocol |
| LLM | 大语言模型 |

---

## 附录

### A. 项目目录结构

```
BettaFish/
├── app.py                      # Flask主应用
├── config.py                   # 配置管理
├── requirements.txt            # 依赖列表
├── .env                        # 环境配置
├── InsightEngine/              # 数据库挖掘引擎
├── MediaEngine/                # 多模态分析引擎
├── QueryEngine/                # 网络搜索引擎
├── ReportEngine/               # 报告生成引擎
├── ForumEngine/                # 论坛协作引擎
├── MindSpider/                 # 爬虫系统
│   ├── BroadTopicExtraction/  # 话题提取
│   └── DeepSentimentCrawling/ # 深度爬取
│       └── MediaCrawler/      # 爬虫核心
├── SentimentAnalysisModel/     # 情感分析模型
├── SingleEngineApp/            # Streamlit单引擎UI
├── logs/                       # 日志目录
└── db_data/                    # Docker数据库数据
```

### B. 命令速查

```bash
# MindSpider命令
python main.py --status                    # 查看状态
python main.py --init-db                   # 初始化数据库
python main.py --broad-topic               # 话题提取
python main.py --deep-sentiment            # 深度爬取
python main.py --complete                  # 完整流程

# Docker命令
docker compose -f b.yml up -d              # 启动
docker compose logs -f app                 # 查看日志
docker compose down                        # 停止

# 数据库查询
PGPASSWORD=xxx psql -h 127.0.0.1 -p 5444 -U bettafish -d bettafish
```

---

**文档信息**：
- 生成时间：2025-11-12
- 版本：1.0
- 维护者：BettaFish开发团队
- 联系方式：670939375@qq.com
