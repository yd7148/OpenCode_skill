---
name: image-to-pdf
description: 將一個資料夾內的圖片（PNG/JPG 等）合併成單一 PDF，每一頁一張圖片、依檔名順序排列，使用 Pillow 離線產生。Use when asked to "圖片轉 PDF", "圖片合併成 PDF", "每一頁一個圖片", "image to pdf", "把圖片轉成一個 PDF 檔案", or to merge screenshot/image files into a single PDF in filename order.
license: MIT
compatibility: opencode
metadata:
  audience: opencode agents
  workflow: images-to-pdf
  languages: zh-TW
---

# image-to-pdf — 圖片 → 單一 PDF（每頁一張，依檔名排序）

把一個資料夾內的圖片（`.png` / `.jpg` 等）合併成**單一 PDF**：
**每一頁一張圖片、依照檔案名稱順序排列**。用 Pillow 離線產生，不需網路。

## When to use

- User 要求「圖片轉 PDF」、「每一頁一個圖片」、「批次截圖合成一個 PDF」
- 資料夾有一堆截圖/照片（檔名帶編號前綴如前導 `01`、`02`…），要依序排成一頁一頁的 PDF
- 環境只需 Python 3 + Pillow（免安裝 wkhtmltopdf / LibreOffice / img2pdf）

## 前置需求

| 工具 | 安裝 | 說明 |
|------|------|------|
| Python 3 | 系統 python（本機 `C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe`） | 需含 Pillow |
| Pillow | `pip install Pillow` | 圖像處理與 PDF 輸出核心 |

```powershell
pip install Pillow
python -c "import PIL; print(PIL.__version__)"
```

## 核心做法（已驗證）

### 1. 先列出資料夾內的圖片並確認順序

用 Glob 或排序後的檔案清單確認「檔名順序」=「PDF 頁面順序」。
若檔名有編號前綴（`01-...`、`02-...`），`sorted(glob.glob('*.png'))` 即可照順序排。

### 2. 執行合併（核心一行）

```python
from PIL import Image
import glob

files = sorted(glob.glob('*.png'))                 # 依檔名排序
images = [Image.open(f).convert('RGB') for f in files]   # 統一轉 RGB（PNG 可能有 alpha）
images[0].save('images.pdf', save_all=True,
               append_images=images[1:], resolution=150.0)
```

- **`save_all=True` + `append_images=images[1:]`**：把後續圖片逐張追加成多頁。
- **`resolution=150.0`**：產出較高解析度的 PDF（不指定時解析度較低）。
- 第一張作為底，其餘全部放進 `append_images`，頁數 = 圖片數。

### 3. 驗證

```powershell
Get-Item images.pdf | Select-Object Name, Length   # 應有合理大小（>0 KB）
```

用 pdf-reader skill 或直接開檔確認頁數 = 圖片數、順序正確。

## 注意事項

| 問題 | 原因 | 解法 |
|------|------|------|
| `cannot identify image file` | 檔名被 glob 抓到但根本不是圖片 | 過濾副檔名 `*.png`/`*.jpg`/`*.jpeg`；或用 `Image.verify()` 檢查 |
| 多餘頁面/順序錯 | glob 混入非圖片檔或排序基準不對 | 只對圖片副檔名排序；檔名加前導零 `01`/`02` 較保險 |
| Pillow 無法讀入（色彩模式罕見） | 顏色數超過 256 或特殊模式 | `convert('RGB')` 統一模式（第 2 步已含） |
| 空白/全黑頁 | 透明 PNG（alpha）未轉 RGB | 一定先 `.convert('RGB')` 壓掉 alpha |

## Deliverables checklist

- [ ] 單一 PDF（`.pdf`）| 每頁一張圖片 | 依檔名順序
- [ ] 頁數 = 圖片張數（`Get-Item` 確認 >0 KB；或開檔點頁數）