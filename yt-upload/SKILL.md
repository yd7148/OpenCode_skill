---
name: yt-upload
description: 透過 Playwright 操作 YouTube Studio，將本機影片上傳並公開發布為 YouTube 影片。支援填寫詳細的標題、說明、標籤、主題標籤，設定目標觀眾（非兒童專屬）、瀏覽權限（公開/不公開/私人），並擷取發布後的影片連結。Use when asked to "上傳YouTube", "上傳影片", "upload to YouTube", "把影片上傳公開", "發布影片", or to upload a local .mp4 to YouTube as a public video.
license: MIT
compatibility: opencode
metadata:
  audience: opencode agents
  workflow: youtube-upload
  languages: zh-TW
---

# yt-upload — YouTube 影片上傳並公開發布

透過 Playwright 操作 YouTube Studio (`studio.youtube.com`)，將本機影片（.mp4）上傳、填寫詳細資訊、設定為公開並擷取發布連結。

## When to use
- User 要求把本機影片上傳到 YouTube 並公開給大家觀看
- 需要填寫影片標題、說明、標籤等詳細資訊
- 需要設定影片為「公開 / 不公開 / 私人」瀏覽權限
- 需要取得發布後的影片連結（`https://youtu.be/VIDEO_ID`）

## 前置需求

| 工具 | 說明 |
|------|------|
| Playwright 瀏覽器（chrome） | 操控 YouTube Studio |
| 已登入的 YouTube/Google 帳戶 | 瀏覽器 session 需已登入（首次會跳 Google 登入頁） |
| 本機 .mp4 影片檔 | 待上傳檔案，需知道完整路徑 |

> 以 `playwright_browser_*` 工具操作瀏覽器。若尚未登入，會先進入 Google 登入頁面，需引導使用者登入後再繼續。

## 上傳流程（Playwright 操作步驟）

### 1. 開啟 YouTube Studio
```js
await page.goto('https://studio.youtube.com');
```
- 若跳轉到 `accounts.google.com/.../signin` 表示未登入 → 停下來引導使用者登入
- 已登入會停在 `studio.youtube.com/channel/...` 頻道資訊主頁

### 2. 開啟上傳對話框
- 點擊「上傳影片」按鈕（頻道資訊主頁右上角）
- 出現「上傳影片」dialog，含「選取檔案」按鈕

### 3. 上傳影片檔案
- 點擊「選取檔案」觸發 file chooser（modal state）
- 用 `browser_file_upload` 提供本機 .mp4 完整路徑
- 等待上傳完成與處理（dialog 標題會顯示檔名，出現「影片連結」與「下一步」按鈕）

### 4. 填寫詳細資訊（「詳細資訊」tab）
- **標題**：會預先帶入檔名，需改為吸引人的標題
- **說明**：填寫完整說明，含書名/作者/重點/主題標籤（`#tag1 #tag2`）
- **目標觀眾**：必填。選「否，這不是兒童專屬的影片」
- **進階設定**：
  - **標記（Tags）**：以英文逗號分隔的關鍵字
  - **影片語言**：中文（繁體）
  - 類別：教育
- 填寫後可點「下一步」跳過 影片元素 / 檢查項目 步驟

### 5. 設定瀏覽權限（「瀏覽權限」tab）
- 依需求選擇：
  - **公開**：所有人都能觀看（public）
  - **不公開**：知道連結的人能觀看（unlisted）
  - **私人**：僅自己與選定對象觀看（private）
- 點擊「發布」按鈕完成

### 6. 擷取影片連結
- 發布後出現「影片已發布」dialog，顯示連結 `https://youtu.be/VIDEO_ID`
- 可直接存取 `https://www.youtube.com/watch?v=VIDEO_ID` 驗證公開可看

## 建議的標題/說明/標籤模板

### 標題（< 100 字）
```
<講者/主題>《<書名/專題名>》<內容性質>｜<副標焦點>
```
範例：
```
程世嘉《智慧通膨下的新商機》重點精華｜AI 時代重新定義自己的位置
```

### 說明（含主題標籤）
```
<書名/專題> <內容性質>（<時長>版）

📘 書名：《...》
👤 作者：...
📅 出版：...

【影片摘要】
<3-5 句重點描述>

⭐ 核心重點
1️⃣ ...
2️⃣ ...

【活動資訊】
<時間、地點、對談嘉賓>

<#tag1 #tag2 #tag3 ...>
```

### 標記（Tags，以逗號分隔）
```
主題關鍵字, 講者, 組織, AI, 相關領域, ...
```

## 驗證
- 上傳完成後開啟公開 URL，確認：
  - 標題、說明、主題標籤正確顯示
  - 影片可播放（duration 正確）
  - 頻道與發布日期正確

## Deliverables checklist
- [ ] 影片已上傳並處理完成
- [ ] 標題、說明、標籤、主題標籤皆詳細填寫
- [ ] 目標觀眾設為「非兒童專屬」
- [ ] 瀏覽權限設定正確（預設公開）
- [ ] 取得發布後的影片連結
- [ ] 於專案資料夾放置 Markdown 說明檔記錄發布資訊
