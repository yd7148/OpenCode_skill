---
name: web-tools
description: 紀錄本機 web 工具環境（Crawl4AI 爬蟲、Webwright 瀏覽器 agent）的安裝路徑與使用方式。Crawl4AI 位於 ~/web-tools/crawl4ai/.venv（Python 3.12，抓網頁轉 markdown），Webwright 位於 ~/web-tools/Webwright 且其 skill 已整合於本 skills 目錄（用 Python playwright 開 Firefox）。Use when asked to "抓網頁", "爬蟲", "crawl", "用 Crawl4AI", "網頁轉 markdown", "Webwright", "瀏覽器自動化", "web scraping", or to locate the local web tools environments.
license: MIT
compatibility: opencode
metadata:
  audience: opencode agents
  workflow: local-web-tools
  languages: zh-TW
---

# web-tools — 本機網頁工具環境

本 skill 說明本機已安裝的兩個網頁相關工具環境與使用方式，供 agent 在需要爬蟲或瀏覽器自動化時引用對應的 venv 路徑。

## 工具一：Crawl4AI（網頁爬蟲 → Markdown）

- **定位**：Python 套件，抓取網頁並轉成乾淨的 markdown，適合 LLM 處理。
- **Python 環境**：`~/web-tools/crawl4ai/.venv/bin/python`（Python 3.12.14）
- **瀏覽器**：Playwright Chromium（位於 `~/Library/Caches/ms-playwright/`）

**基本用法（async）：**
```bash
~/web-tools/crawl4ai/.venv/bin/python /tmp/xxx.py
```
```python
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
async def main():
    async with AsyncWebCrawler(config=BrowserConfig(headless=True)) as cr:
        r = await cr.arun(url="https://example.com",
                          config=CrawlerRunConfig())
        print(r.markdown)   # 乾淨 markdown
asyncio.run(main())
```
也可用 SyncWebCrawler 做同步。可設定 `word_count_threshold`、`extraction_strategy`（LLM/JSON）等。

## 工具二：Webwright（瀏覽器 agent，code-as-action）

- **定位**：Microsoft 開源的 SWE-style 瀏覽器 agent 框架——agent 寫 Python/Playwright script，透過 bash 逐次執行操作瀏覽器，留下可重跑的 `final_script.py`。
- **repo 位置**：`~/web-tools/Webwright`
- **Python 環境**：`~/web-tools/webwright-python/.venv/bin/python`
- **瀏覽器**：Firefox（`~/Library/Caches/ms-playwright/firefox-1538`）
- **skill**：`~/config/opencode/skills/webwright/`（含 reference 檔案）
- **無需 API key**：借用 opencode 的 host model，「no API keys needed」。

**執行環境變數**：playwright 瀏覽器在 macOS 實際下載到 `~/Library/Caches/ms-playwright`，若找不到瀏覽器，設：
```bash
export PLAYWRIGHT_BROWSERS_PATH=/Users/4pins/Library/Caches/ms-playwright
```
身份：Firefox 為首選引擎（某些網站用 Chromium 會 `ERR_HTTP2_PROTOCOL_ERROR`）。
