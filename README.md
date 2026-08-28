# OpenCode_skill

OpenCode 本機 Skills 收藏庫。所有 skill 皆為 MIT 授權，適用於 opencode agents。

## 目錄

| Skill | 用途 |
|-------|------|
| `comsol-analyzer` | 分析 COMSOL Multiphysics .mph 模型檔案 |
| `dwg-to-dxf` | 將 DWG 轉成 DXF 並進行幾何/圖層分析 |
| `md-to-pdf` | 將繁體中文 Markdown 渲染成排版精美的 A4 PDF |
| `v2t-report-summary` | 彙總影片分析報告（OCR × Whisper × GitHub）成繁體中文摘要 |
| `video-2x-speed` | 倍速影片處理（時間軸慣例） |
| `video2text` | 分析錄影影片 → 雙語 Markdown 報告 + 關鍵幀 PDF |
| `yt-batch-download` | 批次下載 YouTube 影片（1080p） |
| `yt-upload` | 透過 Playwright 上傳並公開發布 YouTube 影片 |

## 安裝

將任一 skill 資料夾複製到 `~/.config/opencode/skills/<skill-name>/`（或 `.opencode/skills/<skill-name>/`）即可使用。
