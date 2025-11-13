# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BettaFish (微舆) is a multi-agent public opinion analysis system that automatically crawls 30+ social media platforms and analyzes millions of comments using AI agents. The system follows a modular architecture with specialized engines for different tasks.

## Architecture

### Core Components

**Multi-Agent System (4 Specialized Agents)**:
- **InsightEngine**: Private database mining with sentiment analysis
- **MediaEngine**: Multimodal content analysis (videos, images, text)
- **QueryEngine**: Web search with domestic/international news sources
- **ReportEngine**: Multi-round report generation with templates

**MindSpider Crawler System**:
- **BroadTopicExtraction**: Daily news aggregation from 12+ sources, keyword extraction
- **DeepSentimentCrawling/MediaCrawler**: Deep crawling of 8 platforms (xhs, douyin, kuaishou, bilibili, weibo, tieba, zhihu, yahoo_finance)

**ForumEngine**: Facilitates agent collaboration through debate/discussion mechanism with LLM host

**SentimentAnalysisModel**: Collection of fine-tuned models (BERT/GPT-2, Multilingual, Qwen3, ML-based)

### Technology Stack

- **Backend**: Flask + SocketIO for main app, Streamlit for single-engine UIs
- **Database**: MySQL/PostgreSQL (configurable via `DB_DIALECT`)
- **Async Framework**: asyncio, SQLAlchemy async, httpx
- **Web Scraping**: Playwright with CDP mode, stealth.js anti-detection
- **LLM Integration**: OpenAI-compatible clients (supports Kimi, Gemini, DeepSeek, Qwen via custom BASE_URL)

## Configuration

All configuration is managed through `config.py` using pydantic-settings. Settings load from `.env` file (prioritizes CWD, then project root).

### Critical Config Variables

**Database Configuration:**
```bash
DB_DIALECT=postgresql  # or mysql
DB_HOST=127.0.0.1      # use 'db' for Docker deployment
DB_PORT=5432           # 5432 for PostgreSQL, 3306 for MySQL
DB_USER=bettafish
DB_PASSWORD=bettafish
DB_NAME=bettafish
DB_CHARSET=utf8mb4
```

**LLM API Configuration (OpenAI-compatible format):**

Each engine requires three variables: `*_API_KEY`, `*_BASE_URL`, `*_MODEL_NAME`

```bash
# InsightEngine (推荐 Kimi)
INSIGHT_ENGINE_API_KEY=sk-xxx
INSIGHT_ENGINE_BASE_URL=https://api.moonshot.cn/v1
INSIGHT_ENGINE_MODEL_NAME=kimi-k2-0711-preview

# MediaEngine (推荐 Gemini)
MEDIA_ENGINE_API_KEY=sk-xxx
MEDIA_ENGINE_BASE_URL=https://aihubmix.com/v1
MEDIA_ENGINE_MODEL_NAME=gemini-2.5-pro

# QueryEngine (推荐 DeepSeek)
QUERY_ENGINE_API_KEY=sk-xxx
QUERY_ENGINE_BASE_URL=https://api.deepseek.com
QUERY_ENGINE_MODEL_NAME=deepseek-reasoner

# ReportEngine (推荐 Gemini)
REPORT_ENGINE_API_KEY=sk-xxx
REPORT_ENGINE_BASE_URL=https://aihubmix.com/v1
REPORT_ENGINE_MODEL_NAME=gemini-2.5-pro

# ForumEngine Host (Qwen3)
FORUM_HOST_API_KEY=sk-xxx
FORUM_HOST_BASE_URL=https://api.siliconflow.cn/v1
FORUM_HOST_MODEL_NAME=Qwen/Qwen3-235B-A22B-Instruct-2507

# MindSpider (推荐 DeepSeek)
MINDSPIDER_API_KEY=sk-xxx
MINDSPIDER_BASE_URL=https://api.deepseek.com
MINDSPIDER_MODEL_NAME=deepseek-chat

# SQL Keyword Optimizer (小参数 Qwen3)
KEYWORD_OPTIMIZER_API_KEY=sk-xxx
KEYWORD_OPTIMIZER_BASE_URL=https://api.siliconflow.cn/v1
KEYWORD_OPTIMIZER_MODEL_NAME=Qwen/Qwen3-30B-A3B-Instruct-2507
```

**Search API Configuration:**
```bash
TAVILY_API_KEY=tvly-xxx  # https://www.tavily.com/
BOCHA_WEB_SEARCH_API_KEY=sk-xxx  # https://open.bochaai.com/
BOCHA_BASE_URL=https://api.bochaai.com/v1/ai-search
```

**Flask Server Configuration:**
```bash
HOST=0.0.0.0  # Allow external access
PORT=5000     # Default Flask port
```

## Common Commands

### Main Application

```bash
# Activate virtual environment
source MP-venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate  # Windows

# Run main Flask app (default port 5000)
python app.py

# Run single-engine Streamlit apps
streamlit run SingleEngineApp/insight_engine_app.py --server.port 8501
streamlit run SingleEngineApp/media_engine_app.py --server.port 8502
streamlit run SingleEngineApp/query_engine_app.py --server.port 8503
```

### MindSpider Crawler System

```bash
cd MindSpider

# Check system status
python main.py --status

# Run topic extraction only (from 12 news sources)
python main.py --broad-topic --keywords-count 5

# Run deep sentiment crawling only (uses existing keywords from daily_keywords.txt)
python main.py --deep-sentiment --platforms wb xhs

# Complete workflow (topic extraction + crawling)
python main.py --complete --platforms wb xhs bili

# Test mode (small dataset for initial testing)
python main.py --complete --test

# Specify date and limits
python main.py --complete --date 2025-11-12 --max-notes 50 --max-keywords 20
```

**MindSpider Platform Codes:**
- `xhs` - 小红书 (currently deprecated due to API issues)
- `dy` - 抖音
- `ks` - 快手
- `bili` - B站
- `wb` - 微博
- `tieba` - 百度贴吧
- `zhihu` - 知乎
- `yahoo_finance` - Yahoo Finance

**Important:** First-time use requires QR code login for each platform (except yahoo_finance). Set `HEADLESS=False` in MediaCrawler config to see browser window.

### MediaCrawler (Standalone)

```bash
cd MindSpider/DeepSentimentCrawling/MediaCrawler

# Run platform crawlers with different storage options
python main.py --platform wb --keywords "关键词" --type search --save_data_option postgresql
python main.py --platform wb --keywords "关键词" --type search --save_data_option csv
python main.py --platform wb --keywords "关键词" --type search --save_data_option json

# Yahoo Finance crawler (no login required)
python main.py --platform yahoo_finance --keywords "Apple,TSLA" --type search

# Storage options: csv, json, db, sqlite, postgresql
# Type options: search (only search mode is fully supported)
```

### Database Operations

```bash
# PostgreSQL access (Docker deployment)
PGPASSWORD=bettafish psql -h 127.0.0.1 -p 5444 -U bettafish -d bettafish

# MySQL access (adjust host/port as needed)
mysql -h 127.0.0.1 -P 3306 -u your_user -p your_db_name

# Check table data counts
PGPASSWORD=bettafish psql -h 127.0.0.1 -p 5444 -U bettafish -d bettafish -c "\
SELECT 'weibo' as platform, COUNT(*) FROM weibo_note \
UNION ALL SELECT 'yahoo_finance', COUNT(*) FROM yahoo_finance_news \
UNION ALL SELECT 'douyin', COUNT(*) FROM douyin_aweme \
UNION ALL SELECT 'bilibili', COUNT(*) FROM bilibili_video;"

# Check MindSpider topic extraction results
PGPASSWORD=bettafish psql -h 127.0.0.1 -p 5444 -U bettafish -d bettafish -c "\
SELECT date, COUNT(*) as news_count FROM daily_news GROUP BY date ORDER BY date DESC LIMIT 10;"
```

### Testing

```bash
# Test database connection
python -c "from config import settings; print(f'DB: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}')"

# Test LLM API connections
python -c "from openai import OpenAI; client = OpenAI(api_key='YOUR_KEY', base_url='YOUR_BASE_URL'); print(client.models.list())"

# Run sentiment analysis model test
cd SentimentAnalysisModel/WeiboMultilingualSentiment
python predict.py --text "这个产品很好用" --lang "zh"
```

## Key Implementation Details

### Agent Workflow Pattern

Each Agent (Insight/Media/Query) follows this structure:
```python
agent.py          # Main agent logic with LangGraph state machine
nodes/            # Processing nodes (search, summary, formatting, reflection)
tools/            # Agent-specific tool functions
llms/base.py      # OpenAI-compatible LLM client wrapper
state/state.py    # Agent state definition
prompts/prompts.py # Prompt templates
```

Agents execute in parallel, coordinated by ForumEngine, with multi-round reflection loops.

### MindSpider Workflow

1. **BroadTopicExtraction**: Fetches news from NewsNow API (`https://newsnow.busiyi.world/api/s?id={source}&latest`), extracts keywords using LLM, saves to `daily_topics` table
2. **DeepSentimentCrawling**: Reads keywords from `daily_keywords.txt`, dispatches to MediaCrawler for each platform
3. **MediaCrawler**: Uses Playwright (CDP mode preferred) with stealth.js, implements retry logic with exponential backoff for rate limits

### Database Schema

Core tables:
- `daily_news`, `daily_topics`: BroadTopicExtraction output
- `{platform}_note`, `{platform}_comment`: Platform-specific content (e.g., `weibo_note`, `xhs_note`)
- `yahoo_finance_news`: Yahoo Finance news articles

### Adding New Crawler Platform

1. Create `MindSpider/DeepSentimentCrawling/MediaCrawler/media_platform/{platform}/`:
   - `core.py`: Main crawler inheriting `AbstractCrawler`
   - `client.py`: API client with retry logic
   - `field.py`: Enums and data structures
   - `exception.py`: Custom exceptions
2. Add store implementation in `MediaCrawler/store/{platform}/`:
   - `_store_impl.py`: CSV/DB/JSON/SQLite store classes
   - `__init__.py`: Store factory and business functions
3. Add database model in `MediaCrawler/database/models.py`
4. Add SQL schema in `MediaCrawler/schema/tables.sql`
5. Register in `MediaCrawler/main.py` CrawlerFactory

### News Source Configuration

News sources for BroadTopicExtraction are configured in `MindSpider/BroadTopicExtraction/get_today_news.py`:

```python
SOURCE_NAMES = {
    "weibo": "微博热搜",
    "zhihu": "知乎热榜",
    # Add new sources here
    "source-id": "Display Name"
}
```

Source IDs come from NewsNow API - visit `https://newsnow.busiyi.world/` and inspect URL parameters.

## Important Notes

- **Rate Limiting**: MediaCrawler implements exponential backoff (max 5 retries, 2-64s delays) for HTTP 429 errors
- **Database Type Consistency**: When adding new models, ensure field types match SQL schema (e.g., note_id as varchar vs bigint)
- **CDP Mode**: Requires existing Chrome/Edge browser, falls back to standard mode on timeout. Set `ENABLE_CDP_MODE=True` in MediaCrawler config
- **Proxy Support**: Set system proxy or VPN for external API access (Yahoo Finance, etc.)
- **LLM Compatibility**: All engines use OpenAI-compatible format - can substitute any provider by changing BASE_URL
- **Forum Collaboration**: Agents read from shared ForumEngine log, avoiding homogenization through debate mechanism
- **Configuration Loading**: Settings prioritize `.env` in current working directory, then project root directory
- **Browser Data**: Playwright browser login sessions are stored in `MediaCrawler/browser_data/`. Delete to force re-login

## Troubleshooting

### Common Errors and Solutions

**1. Database Connection Errors**
```bash
# Error: Can't connect to database
# Solution: Check database is running and credentials are correct
python main.py --status  # for MindSpider
# Verify .env file exists and has correct DB_* variables
```

**2. Playwright/Browser Issues**
```bash
# Error: Browser/driver not found
# Solution: Reinstall playwright browsers
playwright install chromium

# Error: CDP connection timeout
# Solution: Disable CDP mode or install Chrome/Edge browser
# Edit MediaCrawler config: ENABLE_CDP_MODE = False
```

**3. Platform Login Failures**
```bash
# Error: QR code not showing or login timeout
# Solution: Run in non-headless mode to see browser
# Edit DeepSentimentCrawling/MediaCrawler/config/base_config.py:
# HEADLESS = False

# Clear cached login data
rm -rf MindSpider/DeepSentimentCrawling/MediaCrawler/browser_data/
```

**4. HTTP 429 Rate Limiting**
```bash
# Error: Too many requests (429)
# Solutions:
# - Increase CRAWLER_MAX_SLEEP_SEC in MediaCrawler config
# - Use proxy/VPN
# - Reduce concurrent requests
# - Wait longer between retry attempts
```

**5. LLM API Errors**
```bash
# Error: Invalid API key / Connection refused
# Solution: Verify API key and BASE_URL in .env
python -c "from config import settings; print(settings.INSIGHT_ENGINE_API_KEY, settings.INSIGHT_ENGINE_BASE_URL)"

# Test API connection
python -c "from openai import OpenAI; client = OpenAI(api_key='YOUR_KEY', base_url='YOUR_URL'); print(client.models.list())"
```

**6. Missing Dependencies**
```bash
# Error: ModuleNotFoundError
# Solution: Reinstall requirements
pip install -r requirements.txt
# Or use uv for faster installation
uv pip install -r requirements.txt
```

**7. Data Type Mismatch (SQL)**
```bash
# Error: operator does not exist: bigint = character varying
# Solution: Check database schema matches model definitions
# Common fix for existing tables:
ALTER TABLE weibo_note ALTER COLUMN note_id TYPE varchar(255);
ALTER TABLE weibo_note_comment ALTER COLUMN note_id TYPE varchar(255);
```

### Debugging Tips

1. **Enable Verbose Logging**: Check `logs/` directory for detailed error messages
2. **Test Mode First**: Always use `--test` flag when trying new platforms/features
3. **Check Browser Console**: When using non-headless mode, check browser console for JavaScript errors
4. **Database Schema**: Use `schema/tables.sql` as reference for correct column types
5. **API Rate Limits**: Yahoo Finance and search APIs have strict rate limits - implement longer delays

## Environment Setup

```bash
# Create virtual environment
python3 -m venv MP-venv
source MP-venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure .env (copy from .env.example)
cp .env.example .env
# Edit .env with your API keys and database credentials
```

## Docker Deployment

### Quick Start with Docker

```bash
# 1. Clone repository and navigate to project directory
cd /path/to/BettaFish

# 2. Copy .env.example to .env and configure
cp .env.example .env
# Edit .env with your API keys and configuration

# 3. Important: Set database host to 'db' for Docker
# In .env file:
# DB_HOST=db  # NOT localhost or 127.0.0.1
# DB_PORT=5432  # PostgreSQL default
# DB_USER=bettafish
# DB_PASSWORD=bettafish
# DB_NAME=bettafish

# 4. Start all services
docker-compose up -d

# 5. Check service status
docker-compose ps

# 6. View logs
docker-compose logs -f app
docker-compose logs -f db

# 7. Access application
# Web interface: http://localhost:5000
# Database: localhost:5444 (PostgreSQL)
```

### Docker Service Management

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes database data)
docker-compose down -v

# Restart a specific service
docker-compose restart app
docker-compose restart db

# Rebuild after code changes
docker-compose up -d --build

# Execute commands inside container
docker-compose exec app python main.py --status
docker-compose exec db psql -U bettafish -d bettafish
```

### Docker Configuration Notes

- **Database persistence**: PostgreSQL data is stored in `db_data/` directory (mapped volume)
- **Port mappings**:
  - Flask app: `5000:5000`
  - PostgreSQL: `5444:5432` (external:internal)
- **Network**: Services communicate via Docker internal network using service names
- **Environment variables**: Loaded from `.env` file in project root
- **Image sources**: Uses official nginx base images (can be changed in docker-compose.yml)

## Development Workflow

1. Configure `.env` with all required API keys
2. Initialize database: `cd MindSpider && python main.py --init-db`
3. Test topic extraction: `python main.py --broad-topic --keywords-count 3`
4. Test crawling: `python main.py --deep-sentiment --platforms wb --test`
5. Run main app: `cd .. && python app.py`

## Code Standards

### General Principles

- **Comments**: Use Chinese comments for Chinese-language projects (as per original codebase style)
- **Logging**: Use loguru for all logging with structured output
- **Async Operations**: Implement async/await for I/O operations (database queries, HTTP requests, file operations)
- **Error Handling**: Add retry logic with exponential backoff for external API calls
- **Configuration**: Store all config in `.env`, never hardcode credentials or API keys
- **Validation**: Use pydantic for settings validation and data models

### File Naming and Structure

- Agent modules: `{name}_engine/agent.py` (e.g., `InsightEngine/agent.py`)
- Database models: Use SQLAlchemy declarative base in `database/models.py`
- Store implementations: `store/{platform}/_store_impl.py` and `store/{platform}/__init__.py`
- Tool functions: Place in `tools/` directory with descriptive names
- State definitions: `state/state.py` for each agent

### Async/Database Patterns

```python
# Good: Use async context manager for database sessions
async with get_session() as session:
    result = await session.execute(stmt)
    await session.commit()

# Good: Use async for I/O operations
async def fetch_data(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# Good: Retry logic pattern
for attempt in range(max_retries):
    try:
        result = await api_call()
        break
    except RateLimitError:
        delay = (2 ** attempt) * base_delay + random.uniform(0, 1)
        await asyncio.sleep(delay)
```

### LLM Integration Pattern

All LLM calls should follow OpenAI-compatible format:

```python
from openai import OpenAI

client = OpenAI(
    api_key=settings.ENGINE_API_KEY,
    base_url=settings.ENGINE_BASE_URL
)

response = client.chat.completions.create(
    model=settings.ENGINE_MODEL_NAME,
    messages=[{"role": "user", "content": prompt}]
)
```

### Logging Best Practices

```python
from loguru import logger

# Good: Structured logging with context
logger.info(f"[Module.function] Action description: param={value}")
logger.error(f"[Module.function] Error occurred: {error}", exc_info=True)

# Good: Log important state changes
logger.info(f"[YahooFinanceCrawler.search] Fetching page {page + 1} for keyword: {keyword}")

# Avoid: Generic messages without context
logger.info("Processing...")  # Bad
```

### Adding New Crawler Platforms

When adding a new platform crawler, follow this checklist:

1. Create `media_platform/{platform}/` with: `core.py`, `client.py`, `field.py`, `exception.py`
2. Create `store/{platform}/` with: `_store_impl.py`, `__init__.py`
3. Add database model in `database/models.py`
4. Add SQL schema in `schema/tables.sql`
5. Register in `main.py` CrawlerFactory
6. Test with `--platform {platform} --test` flag first
7. Document storage options and login requirements

### Configuration Management

- All configuration uses pydantic-settings in `config.py`
- Environment variables can override `.env` file values
- Child modules inherit parent config automatically
- Use `Field()` with descriptions for all config variables
- Never commit `.env` file to version control
