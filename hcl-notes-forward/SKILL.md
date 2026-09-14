---
name: hcl-notes-forward
description: 自動化 HCL Notes（本機 Windows client）的「公布函系統通知」未讀郵件批次處理：將信箱依寄件者($BySender)視圖中「公布函系統通知」群組的未讀信件，逐封以「直接轉寄」寄給指定群組（如「工三碳化矽專案組-03-全組(21)」），寄完刪除原信。全程用 GDI 全螢幕截圖 + OCR（RapidOCR）+ SetCursorPos/mouse_event 螢幕絕對座標點擊。當你被要求「轉寄公布函」「批次處理 Notes 未讀通知」「直接轉寄給群組」、或收到一份 HCL Notes 公布函批次作業時使用。Use when asked to 轉發 Notes 公布函、處理未讀通知、direct-forward Notes mail to a group.
license: MIT
compatibility: opencode
metadata:
  audience: opencode agents
  workflow: hcl-notes-ui-automation
  languages: zh-TW
  os: win32
---

# hcl-notes-forward — HCL Notes 公布函直接轉寄自動化

把信箱「依寄件者」($BySender) 視圖中，`公布函系統通知` 群組的**未讀**信件，逐封用 **「直接轉寄」+ 指定群組** 寄出，寄出驗證後**刪除原信**。全程不做 JNI（伺服器路徑在互動式密碼保護下封死），全部用**畫面截圖 + OCR + 螢幕絕對座標點擊**的 UI 自動化。

## When to use

- 使用者要求把 Notes 信箱中的「公布函系統通知」未讀信，用「直接轉寄」寄給某個通訊錄群組。
- 要批次處理多封未讀公布函，並在寄出後刪除原信。
- 使用者明確表示這類公布函「直接轉寄」**不留已傳送副本**，故無法用已傳送驗證，只能靠收件群組端或使用者確認。

## 環境與解除安裝前提（已驗證固定值）

| 項目 | 值 |
|------|-----|
| Notes client | HCL Notes 9-11（本案例 11.0.1FP5），`C:\lotus\Notes\nlnotes.exe` |
| config | `C:\lotus\Notes\notes.ini`：`MailServer=CN=skms03/O=fpg`、`MailFile=mail\N000149839.nsf` |
| 使用者 | `CN=N000149839 劉士禎/OU=03/O=Fpg`，ID `D:\90-Notes ID\V035100劉士禎_N000149839-R2.id` |
| Notes 主視窗 | 例 (761,21)，尺寸 1121x839，pid 由 `Get-Process nlnotes` 取得 |
| OCR venv | `D:\80-Opnecode\workspace\_maidate_work\venv\Scripts\python.exe`（含 Pillow + rapidocr_onnxruntime） |
| 工具鏈 | `capture_win.ps1`（視窗截圖）、`ocr_screen2.py`（RapidOCR）、`crop.py`、`click2.ps1`、`zclean.ps1`、`winlist.ps1`、`rowclass.py`（逐列紅/黑分類）——位於本 skill 的 `scripts\` |

### 硬性限制（務必先知道，省得做白工）

- **JNI/伺服器路徑全死**：任何 server/DB 操作（client 關閉時）觸發互動式 `Enter password` 提示（Notes 從 OS console 讀密碼，程式餵入失敗）；`createSession("",...,pw)` 報 `not a server`；`notesUnreadInbox` 在本機複本掛死 90s。**不要嘗試 JNI。**
- Notes JVM 是 Java 8（1.8.0_312）；若需編譯 .java、要 `-source 8 -target 8 -bootclasspath C:\lotus\Notes\jvm\lib\rt.jar`。
- 「直接轉寄」寄出後**不會在「已傳送」資料夾留記錄**（刷新 F9 後仍為舊件）。**不要用已傳送驗證**。
- 目標群組是通訊錄裡的群組，例 `工三碳化矽專案組-03-全組(21)`。「名稱」欄位下**只可有該群組一組**（重複=寄兩次）。

## 前景/z-order 陷阱（必做）

Notes 常被 Word/Excel/PPT/PDF-XChange/PotPlayer/Chrome 等視窗覆蓋；若點擊無效，先跑：

```powershell
& "<skill>\scripts\zclean.ps1"   # 最小化其他頂層視窗，讓 Notes 可接收輸入
# 再設前景：
$h=(Get-Process nlnotes | Select-Object -First 1).MainWindowHandle
Add-Type 'using System;using System.Runtime.InteropServices;public class W{[DllImport("user32.dll")]public static extern bool SetForegroundWindow(IntPtr h);}'
[W]::SetForegroundWindow($h)
```

`winlist.ps1` 可列出所有頂層視窗與 z-order，確認 Notes 座標與是否被覆蓋。

注意：**OCR/點擊座標以「螢幕絕對座標」為準**。`capture_win.ps1` 抓的是 Notes 視窗內座標 → 點擊時需 **+ (視窗左上角 x, y)** 轉成螢幕絕對座標。

## 座標轉換

- 視窗內座標 `(wx, wy)` → 螢幕絕對座標 `(wx + winLeft, wy + winTop)`。例 Notes 在 (761,21)：
  - 直接轉寄按鈕：視窗 (277,120) → 螢幕 (1038, 141)。
- Notes 的**對話框（如「選取名稱」「系統已完成轉發作業」）是子視窗**，非頂層；`capture_win.ps1 nlnotes` 看不到它，需用 **GDI 全螢幕截圖**（見 scripts 範例，抓 1920x1080 desktop）再 OCR。
- 對話框按鈕座標要「現量現用」— 每次開啟對話框後重新 OCR 定位，不要死記，因視窗位置可能變。

## 工作流（逐封：開信 → 直接轉寄 → 群組 → 新增一次 → 確定 → 完成訊息 → 確定 → 離開 → 刪除原信）

### 0. 前置
1. 啟動/確認 Notes 在工作台並連線（信箱列 Inbox 數百筆正常）。
2. `zclean.ps1` + `SetForegroundWindow` 確保 Notes 在前景。

### 1. 進入「依寄件者」($BySender) 視圖並展開群組
- 在左側導覽列點 `信箱`(Inbox)，再點 `依寄件者`。
- 列表頂（Ctrl+Home）往下找 `公布函系統通知` 列；**點該列 + 按 Right 鍵展開**（雙擊不一定有效）。展開後 Ctrl+Home 回頂。
- 展開後群組下列出信件：**紅字=未讀、黑字=已讀**。用 `rowclass.py`（逐列掃 red/black 像素）可靠判讀。
  - 例：FOOTDISC 列在視窗 y324-345，掃描 red/black 得 `UNREAD`(red) 或 `READ`(black)。

### 2. 辨識「要處理的未讀信件」
- 在 `公布函系統通知` 群組中掃出所有紅字（未讀）列。
- 與使用者確認數量上限（例只處理最近 N 封），因為視圖裡未讀紅色可能比目標多。
- 逐列記錄：主旨 + 日期。已寄/已讀的（黑字）跳過。

### 3. 開信
- **單擊選列後按 Enter**（比雙擊可靠；雙擊常開不出來）。
- 開信後確認落到該 memo（title 含 `公布函...`）。

### 4. 直接轉寄 → 選群組
- 按 memo 工具列 **「直接轉寄」**（例螢幕 (1038,141)）。
- 出現「選取名稱」對話框（全螢幕截圖才看得到，約 x941-1662/ydlg 區域）。
- 在左側清單找群組（例 `工三碳化矽專案組-03-全組(21)`），**單擊選取**。
- 按 **「新增(A)」只按一次**！按兩次 = 群組進「名稱」欄兩次 = 寄兩次。
- 務必確認「名稱」欄（右側）**只有一組**該群組（OCR 檢查右側區域是否只出現一次）。
- 按 **「確定」**。
  - 若出現 `系統已完成轉發作業!` 提示 → 轉寄已送出。按其 **「確定」**。
  - 若沒出現訊息、直接落回原 memo → 轉寄可能未確認送出，需向使用者確認（無法用已傳送驗證）。
- 按 memo **「離開」** 關閉回列表。

### 5. 刪除原信（使用者允許後）
- 回到列表後，重新定位該列（重新 OCR），單擊選列，按 **Delete**。
- 若出現刪除確認對話框，OCR 定位後按 **「確定/是」**。
- 刪除後該列應從視圖消失（未讀數減少）。

### 6. 驗證
- **已傳送不可用**（直接轉寄不留副本）。只能靠：使用者於收件群組端確認，或使用者口頭確認。
- 每封寄出後可記錄完成，並在最後回報已處理清單（主旨+日期）。

## 關鍵陷阱筆記（本流程踩過的雷）

- **新增只能一次**：重複按「新增(A)」會把群組加進「名稱」欄兩次 → 同一封信寄給同一群組兩次。先按 `登錄幾次` 決定；本流程以檢查右側名稱欄只出現一次為準。
- **點擊無效常因 z-order**：先 `zclean.ps1`。
- **「選取名稱」/完成訊息對話框是子視窗**：`capture_win.ps1` 看不到，要用 GDI 全螢幕截圖。
- **讀 memo 的「離開」有時不受點擊**：若卡住無法關閉，用 `zclean` 後 `SetForegroundWindow` 再點，或用鍵盤；仍不行就**重啟 Notes client**（taskkill + relaunch）回到乾淨工作台。**重啟前先跟使用者確認**（有信箱鎖風險）。
- **開信用單擊+Enter**：雙擊常失敗。
- **視圖虛擬化**：列表是虛擬捲動，每次要重新 OCR 定位列位置，不要假設固定 y。

## scripts\ 工具簡介

| 腳本 | 用途 |
|------|------|
| `capture_win.ps1 <winName> <outPng>` | 抓指定視窗（如 nlnotes）內圖到 PNG |
| `ocr_screen2.py <png> <ocrTxt>` | RapidOCR 中文 → 每行 `[x0-x1,y0-y1] 文字`（座標為該圖像素座標） |
| `crop.py <src> <out> <x> <y> <right> <bottom> <scale>` | 裁切並放大（座標為原圖像素） |
| `click.ps1` / `click2.ps1 <wx> <wy> <winL> <winT> <kind>` | SetCursorPos+mouse_event 在螢幕絕對座標點擊 |
| `zclean.ps1` | 最小化其他頂層視窗，讓 Notes 接收輸入 |
| `winlist.ps1` | 列出頂層視窗、pid、位置、z-order |
| `rowclass.py` | （依寄件者視圖）逐列掃紅/黑像素，判未讀/已讀 |
| `focus.ps1`/`focus2.ps1`/`topmost.ps1` | 設定前景 / 置頂（輔助） |

> GDI 全螢幕截圖（對話框用）範例見本 skill 對話框段落；核心是 `GetDesktopWindow`+`GetWindowDC`+`BitBlt` 到 1920x1080 bitmap。

## 座標速查（範例機，僅參考；每次以 OCR 現量）

- 直接轉寄：螢幕 (1038,141)。
- 「選取名稱」對話框：左欄群組列 `工三碳化矽專案組-03-全組(21)` 約 (1065,374)；「新增(A)」約 (1370,365)；「確定」約 (1579,524)；「取消」約 (1662,524)。
- 完成訊息「系統已完成轉發作業!」確定：約 (982,590)。
- 已傳送視圖頂端刷新：F9。
