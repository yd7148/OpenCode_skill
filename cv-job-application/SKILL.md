---
name: cv-job-application
description: Use when 投遞或填寫 中華電信/台積電 線上履歷、要操作 rmis.cht.com.tw 報名表（自動填表、附件上傳、狀態檢核）、要沿用已保存的 Chrome 登入資訊（.pw-profile）登入、需要把台積電人事資料表 PDF 去識別化改成中華電信版、或要整理 E:\01-Project\2026-09-CV 履歷專案（01-原始資料 / 02-TSMC / 03-中華電信）。Covers Playwright CDP 持久化登入、圖形驗證碼 OCR + Outlook OTP、欄位 Big5 byte 上限、附件格式限制、掃描頁影像去識別化。
license: MIT
compatibility: opencode
metadata:
  audience: opencode agents
  workflow: cv-job-application
  languages: zh-TW
---

# cv-job-application — 履歷投遞（中華電信 / 台積電）

在 Windows 上用 Playwright + CDP 自動化操作**中華電信人才招募網**（`https://rmis.cht.com.tw/portal/jobs/`）填寫報名表與上傳附件，
並處理台積電人事資料表（去識別化、簡報改字轉 PDF）。

## 專案位置與資料夾結構

專案根目錄：`E:\01-Project\2026-09-CV\`（**三個資料夾，勿再新增同層檔案**）

| 資料夾 | 用途 | 內容 |
|--------|------|------|
| `01-原始資料/` | **主要資料** — 所有履歷原始檔 | 7 個原始附件（保留系統檔頭檔名 `736180_<hash>_0601-劉士禎-NN-...`），**只讀不改** |
| `02-TSMC/` | **台積電使用** — 上傳／下載檔 + Markdown 說明 | 同批附件改乾淨檔名（`0601-劉士禎-NN-...`）+ `TSMC_Career_Profile.md` |
| `03-中華電信/` | **中華電信使用** — 自動化程式與產出 | `.pw-profile/`（登入資訊）、`out/`（產出）、`dumps/`、`*.py`、`中華電信履歷填寫紀錄.md`、`README.md` |

資料流：`01-原始資料` →（複製改檔名）→ `02-TSMC` →（去 TSMC 化／轉檔）→ `03-中華電信/out/` → 上傳。

檔案命名：`0601` = 投遞批次代號，`NN` = 附件序號（01 履歷表、02 最高學歷成績單、03 次高學歷成績單、04 語言檢定、05 證照、06 其他附件、07 其他附件-R2 簡報）。

## 執行環境

| 項目 | 值 |
|------|-----|
| Python | `C:\Users\4pins\AppData\Local\Programs\Python\Python312\python.exe`（Playwright、ddddocr、easyocr、pymupdf、PIL、fpdf2、python-pptx） |
| Chromium | `C:\Users\4pins\AppData\Local\ms-playwright\chromium-1234\chrome-win64\chrome.exe` |
| 中文字型 | `C:\Windows\Fonts\kaiu.ttf`（標楷體，PDF 用）、`msjh.ttc` |
| Shell | Windows PowerShell 5.1（**沒有** `rsync`） |

---

## 一、登入資訊（最重要：持久化 Chromium 設定檔）

登入狀態保存在 `E:\01-Project\2026-09-CV\03-中華電信\.pw-profile\`，內含：

- 中華電信帳號 `M1221******`（完整帳號只存於本機專案 `03-中華電信`，不進公開 repo），**密碼已由瀏覽器記憶**（`login.jsp` 會自動帶入）
- Outlook `yd7148@hotmail.com.tw` 的登入 session → 中華電信的 **Email 動態密碼（OTP）** 會寄到這裡，可自動讀取
- 圖形驗證碼不保存，每次登入用 `captcha_ocr.py`（ddddocr）辨識

> 不要把密碼寫入任何檔案或 commit。憑證只存在 `.pw-profile/`。

### 啟動瀏覽器（固定用這個指令，帶 remote debugging）

```powershell
$chrome = "C:\Users\4pins\AppData\Local\ms-playwright\chromium-1234\chrome-win64\chrome.exe"
$prof   = "E:\01-Project\2026-09-CV\03-中華電信\.pw-profile"
$args = "--remote-debugging-port=9223 --remote-allow-origins=* --disable-extensions " +
        "--disable-component-extensions-with-background-pages --user-data-dir=`"$prof`" " +
        "https://rmis.cht.com.tw/portal/jobs/login.jsp"
Start-Process -FilePath $chrome -ArgumentList $args
```

Python 端**只連線、不 launch**：

```python
import sys; sys.path.insert(0, r"E:\01-Project\2026-09-CV\03-中華電信")
from cht_cdp import connect, is_logged_in, BASE
b, ctx = connect(p)                      # p.chromium.connect_over_cdp("http://127.0.0.1:9223")
cht = [x for x in ctx.pages if ".cht.com.tw" in x.url][0]
```

### 鐵則

- **絕不呼叫 `browser.close()`** — 會關掉使用者的瀏覽器（使用者明確抱怨過）。Playwright 經 CDP 的 `browser.close()` 只斷線；要關請用 `taskkill /PID <主行程>`（送 WM_CLOSE，Chromium 會優雅寫回 profile）。
- **絕不刪除 `.pw-profile/`**（刪掉就要重新登入 + 重新收 OTP）。
- 要搬移／重新命名 `03-中華電信/` 前，必須先優雅關閉 Chromium（profile 被鎖住會搬不動）；搬完用新路徑重啟，登入狀態仍保留（Outlook session 實測可存活，CHT 約 30 分鐘閒置會逾時，重新登入即可）。
- 網站約**閒置 30 分鐘**自動登出（頁面有倒數）。

### 登入流程

`do_login.py`：開 `login.jsp` → 抓驗證碼圖 `captcha.png` → `captcha_ocr.py` 辨識填 `#idLoginAuthCode` → 送出 → OTP 由 `outlook_check.py` 到 Outlook 取信填 `#idoptpw`。
驗證碼最多試 2 次，失敗就走 OTP，不要卡在 OCR。

---

## 二、報名表結構與儲存端點

| 頁面 | 表單 | 儲存頁 | 關鍵欄位 |
|------|------|--------|---------|
| `biographical.jsp` | — | — | 姓名、生日、婚姻、兵役 |
| `mtel.jsp` | — | — | 郵遞區號（333001）、地址、行動、住電 |
| `degree.jsp` | — | — | 學歷最多 3 筆 + 論文題目 |
| `exper.jsp` | `myform4` | `exper_save.jsp` | 由最近一份工作填起；`#idnoexp_flg` 無經驗 |
| `license.jsp` | `myform5` | `license_save.jsp` | `#idprofessional` / `#idlicense` / `#idlang_license` |
| `biog_data.jsp` | `myform` | `biog_data_save.jsp` | `#idbiogdata`（`save_data()`） |
| `scope.jsp` | `myform` | `scope_save.jsp` | `A1~A10`=大一~大五上下、`B1~B6`=研一~研三上下 |
| `relation.jsp` | `myform4` | `relation_save.jsp` | `#idrelation`（`relation_flg=N`） |
| `userfile.jsp` | `myfileform` | `send_file.jsp` | 上傳 `#filedata` / `#file_type` / `#idfiledesc` / `#send_bt` |
| | `myform` | `del_file.jsp` | 刪除：勾 `input[name=do_batch][value=<伺服器檔名>]` → `do_del_file()` |
| `viewbiog.jsp` | — | — | **完成度檢核表（驗收用）** |
| `attention.jsp` | — | — | 純告知，無欄位 |

對應腳本：`fill_degree*.py`、`fill_exper.py`、`fill_license.py`、`fill_biog.py`、`fill_scope.py`、`fill_relation.py`、`upload_files*.py`、`replace_resume.py`（刪舊+重傳）。

---

## 三、附件處理

1. **個人照片**：從 `01-履歷表.pdf` 內嵌圖擷取（xref 32，402×501）→ `out/0601-劉士禎-個人照片.jpg`。
2. **自我介紹簡報**：網站不吃 pptx → 先 `modify_pptx.py` 把 TSMC 字樣改為中華電信（含 `slide1.xml`、`docProps/app.xml`、`core.xml` creator），再用 `build_deck_pdf.py`（fpdf2 + 標楷體）轉 7 頁橫式 A4 PDF。
3. **履歷表去識別化**（`redact_resume.py` + `redact_resume_p3.py`）：
   - 文字頁：pymupdf `search_for` 找 `TSMC`/`Taiwan Semiconductor`/`台積` → `add_redact_annot` 白底 → 以 `fitz.Font("cjk")` + `TextWriter` 重寫整行。
   - **掃描頁（親簽頁）**：render 300 DPI → EasyOCR bbox → PIL 填白 + `ImageFont.truetype(kaiu.ttf)` 重繪 → 換掉該頁影像。
   - 驗收：新檔全文檢索 `TSMC`/`tsmc`/`Semiconductor`/`台積` = 0，且新文字未超出頁寬。
   - 上傳用 `replace_resume.py`（先刪舊檔再上傳新檔）。

---

## 四、踩雷紀錄

1. **欄位有 Big5 byte 上限**（中文 1 字 = 2 bytes，HTML `maxlength` 即 byte 上限；超過會被**後端無聲截斷**，存檔後務必重載確認）：
   公司 30 bytes = 15 中文字、職務 20 bytes = 10 中文字、工作內容 40 bytes = 20 中文字。
2. **姓名用字**：禎 = `U+798E`（`U+7A4E` 是「穎」）。用 pymupdf 抽字比對，不要看主控台。
3. **主控台中文亂碼** → 結果一律寫入 `dumps/*.json`（UTF-8）再用 Read 檢視。**不要**用 PowerShell `>` 導向（會變 UTF-16 無法讀）。
4. **PowerShell here-string 不解析 `\uXXXX`** → 含中文路徑的 Python 要寫成 `.py` 檔再執行，勿用 `python -c`。
5. **EasyOCR / cv2 不能讀非 ASCII 檔名** → 先複製成 ASCII 檔名再 OCR。
6. **附件只接受** `pdf / jpg / png`，單檔 ≤ 10 MB。
7. 成績單 PDF 為**掃描影像無文字層**，需 OCR 才能取數字。

---

## 五、驗收

```python
cht.goto(BASE + "viewbiog.jsp"); time.sleep(3)
# 檢核表：基本資料/聯絡資料/學歷/個人自傳/個人照片/任職公司親屬/工作經驗 = 完成
#        畢業證書、工作證明文件 = 尚未完成（需人工提供檔案）
```

完整填寫內容與待辦見 `E:\01-Project\2026-09-CV\03-中華電信\中華電信履歷填寫紀錄.md`。
