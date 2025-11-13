# Repository Guidelines

## Project Structure & Module Organization
`main.py` orchestrates runs across two core modules: `BroadTopicExtraction/` (topic discovery, AI summarization, DB writes) and `DeepSentimentCrawling/` (Playwright-based crawlers plus `MediaCrawler/` platform adapters). Database helpers live under `schema/`, while environment templates sit in `config.py.example` alongside the active `config.py`. Asset references (e.g., diagrams) are stored in `img/`, and integration notes such as `YAHOO_FINANCE_INTEGRATION.md` complement `README.md` and `USAGE.md`. Keep experimental notebooks or datasets outside the repo to avoid polluting automation scripts that assume this layout.

## Build, Test, and Development Commands
- `pip install -r requirements.txt` (or `uv pip install -r requirements.txt`): install runtime dependencies.
- `playwright install`: fetch browser drivers required by `DeepSentimentCrawling`.
- `python main.py --status`: sanity-check DB connectivity and config.
- `python main.py --broad-topic [--date YYYY-MM-DD]`: collect daily news, extract topics, and persist keywords.
- `python main.py --deep-sentiment --platforms xhs dy --test`: launch selective crawls; drop `--test` for production runs.
- `python main.py --complete --test`: execute the full pipeline end-to-end in dry-run mode.
- `python test_yahoo_finance.py`: verify the Yahoo Finance crawler import path before enabling it in `MediaCrawler`.

## Coding Style & Naming Conventions
Code is Python ≥3.9 and follows standard PEP 8 (4-space indents, snake_case for functions/modules, CapWords for classes). Keep configuration constants uppercase (`DB_HOST`, `MINDSPIDER_API_KEY`) and store secrets in `.env`, never in git. CLI flags should mirror the existing `--broad-topic`, `--deep-sentiment`, and `--complete` patterns. When touching Playwright or asyncio routines, add concise comments describing non-obvious waits, throttling, or concurrency guards.

## Testing Guidelines
Lightweight smoke tests currently live at repo root (`test_yahoo_finance.py`) and should be executed with `python -m pytest` or direct invocation. New crawler or extractor tests belong alongside the module they cover (e.g., `BroadTopicExtraction/tests/`). Name tests after the feature under check (`test_weibo_hot_topics_fetches_rank`). Aim to preserve scraping stability: mock external APIs when feasible and gate long-running end-to-end tests behind an explicit flag such as `--test`.

## Commit & Pull Request Guidelines
Recent history uses Conventional Commits (`docs:`, `Hotfix:`, `feat:`). Match that style so changelog tooling stays consistent, and keep subject lines under ~72 characters. Each pull request should include: concise summary of module-level impact, reproduction or validation steps (commands run, logs clipped if relevant), updated screenshots when UI assets in `img/` change, and links to the tracked issue or discussion. Mention database migrations or config changes explicitly so deployment scripts can be sequenced safely.

## Security & Configuration Tips
Duplicate `config.py.example` into a private `config.py` or `.env` and guard API keys with your secret manager; never upload filled templates. For Playwright logins, store session cookies in the expected `DeepSentimentCrawling/MediaCrawler/cache/` subfolders and rotate them regularly. Limit database accounts used here to least-privilege (SELECT/INSERT/UPDATE on `mindspider` schema) to reduce blast radius if crawler hosts are compromised.
