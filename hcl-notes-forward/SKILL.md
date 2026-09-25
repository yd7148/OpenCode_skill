---
name: hcl-notes-forward
description: 自動化 HCL Notes（本機 Windows client）的「公布函系統通知」未讀郵件批次處理（直接轉寄＋刪原信）與「信箱整批匯出分析／讀取加密個人機密信件數值」（無 JNI，全程 GDI 截圖 + RapidOCR + 螢幕絕對座標點擊）。當你被要求「轉寄公布函」「批次處理 Notes 未讀通知」「直接轉寄給群組」「匯出/分析 Notes 信箱」「讀取加密信件金額」時使用。
license: MIT
metadata:
  audience: opencode agents
  workflow: hcl-notes-ui-automation
  languages: zh-TW
  os: win32
  compatibility: opencode
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
| Notes 主視窗 | 位置**不固定**（例 (761,21) 1121x839；(1000,0) 920x940），**每次 `GetWindowRect` 現量**，pid 由 `Get-Process nlnotes` 取得 |
| OCR venv | `D:\80-Opnecode\workspace\_maidate_work\venv\Scripts\python.exe`（含 Pillow + rapidocr_onnxruntime）；可執行版最少需要 Pillow，若要 OCR 驗證完成訊息需 RapidOCR |
| 工具鏈 | `hcl_notes_forwarder.py` / `run_hcl_notes_forwarder.cmd`（可直接批次轉寄＋刪原信）、`build_exe.ps1`（PyInstaller 打包）、`capture_win.ps1`（視窗截圖）、`ocr_screen2.py`（RapidOCR）、`crop.py`、`click2.ps1`、`zclean.ps1`、`winlist.ps1`、`rowclass.py`（逐列紅/黑分類）——位於本 skill 的 `scripts\` |

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

**a11y/OCR 座標一律是「視窗相對」**：`get_app_state`（Computer Use）回傳的 Frame 座標、以及 `ocr_screen2.py` 的 `[x..,y..]` 全是視窗內座標，點擊前**一律加視窗左上角**。例 2026-09-24：視窗在 (1000,0)，某「確定」按鈕 a11y 座標 (422,245) → 螢幕 (1422,245)。若直接按 (422,245) 會點到覆蓋層（OpenCode）造成誤點。

## 座標轉換

- 視窗內座標 `(wx, wy)` → 螢幕絕對座標 `(wx + winLeft, wy + winTop)`。例 Notes 在 (761,21)：
  - 直接轉寄按鈕：視窗 (277,120) → 螢幕 (1038, 141)。
- Notes 的**對話框（如「選取名稱」「系統已完成轉發作業」）是子視窗**，非頂層；`capture_win.ps1 nlnotes` 看不到它，需用 **GDI 全螢幕截圖**（見 scripts 範例，抓 1920x1080 desktop）再 OCR。
- 對話框按鈕座標要「現量現用」— 每次開啟對話框後重新 OCR 定位，不要死記，因視窗位置可能變。

## 可直接執行的批次工具

優先使用 `scripts\hcl_notes_forwarder.py` 或 `scripts\run_hcl_notes_forwarder.cmd`，這是 2026-09-25 實測流程整理出的保守執行版：

```powershell
# 偵測紅字列但不寄信/不刪信
.\hcl-notes-forward\scripts\run_hcl_notes_forwarder.cmd --dry-run --debug

# 預設：轉寄給「工三碳化矽專案組-03-全組(21)」，看到完成訊息後刪除原信
.\hcl-notes-forward\scripts\run_hcl_notes_forwarder.cmd --max-messages 30 --debug

# 只轉寄不刪除（臨時測試用）
.\hcl-notes-forward\scripts\run_hcl_notes_forwarder.cmd --max-messages 3 --no-delete
```

預設行為：

- 每封信必須看到 `系統已完成轉發作業` / 完成訊息，才會按刪除。
- 刪除只在完成訊息後執行；若未偵測到完成訊息，腳本停止且不刪原信。
- `--restart-every 5` 預設每成功 5 封重啟 Notes，避免文件分頁堆疊造成列表切換失敗。
- `--scan-start-y 220` 預設從較上方的清單區開始掃描；若 dry-run 漏抓，可用 `--scan-start-y 180` 或其他值校正。
- 其他電腦可用 `--notes-exe` 指定 Notes 路徑；若 DPI/視窗布局不同，先跑 `--dry-run --debug` 校正座標。

### 打包成 EXE

可以打包成單一 `.exe`，建議用 PyInstaller：

```powershell
.\hcl-notes-forward\scripts\build_exe.ps1
```

輸出會在目前目錄的 `dist\hcl-notes-forwarder.exe`。打包後仍需目標電腦已安裝 HCL Notes，且第一次執行前要確認 Notes 可以正常登入信箱。

## 工作流（逐封：開信 → 直接轉寄 → 群組 → 新增一次 → 確定 → 完成訊息 → 確定 → 回列表 → 刪除原信）

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

### 5. 刪除原信（成功轉寄後預設執行）
- 使用者已指定：以後成功轉寄後就刪除原信。這是 `hcl_notes_forwarder.py` 的預設行為。
- 回到列表後，重新定位該列（重新 OCR），單擊選列，按 **Delete**。
- 若出現刪除確認對話框，OCR 定位後按 **「確定/是」**。
- 刪除後該列應從視圖消失（未讀數減少）。
- 若沒有看到完成訊息，或列表定位不確定，**停止，不刪除**。

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
- **Ctrl+W 可能需按兩次**：第一次按 Ctrl+W 有時只關閉 memo 分頁但不回視圖（視窗標題仍顯示 memo 主旨）；需再按一次 Ctrl+W 才會真正回到 $BySender 視圖。若標題未變，再執行一次 Ctrl+W。
- **視圖列位置每次操作後會重排**：開信、刪除、發送完成後視圖都會捲動/重定位；**絕對不能用上次的 y 座標**，必須每次重新掃描（rowclass.py）確認位置。
- **視窗標題不可單獨作為「memo 是否開啟」的判斷依據**：標題會顯示「預覽窗格」中選列的主旨；**必須看工具列**（y116 區域）確認：
  - 信箱式工具列（新增/回覆/轉寄/移入垃圾桶）= **視圖模式**
  - memo 式工具列（轉立交辦單/直接轉寄/輸入意見後轉寄/另立新案/離開）= **memo 已開啟**
- **完成訊息对话框座標**：`rect[884,473-1052,621]`（螢幕絕對），OK 按鈕約 (982,590)。出現延遲約 2-3 秒，需等待。
- **不要按 (832,119)「關閉」書籤窗格鈕**：會導致視窗短暂 0x0 異常（winlist 回報 hwnd=0）。
- **每次 bash 工具調用是獨立 PowerShell 行程**：Add-Type 定義的 class（如 F1Dlg3、R3Dlg4、ChkDlg*）在下一次調用不存在（TypeNotFound），**每次必須重新 Define**。
- **crop.py + ocr_screen2.py 需循序執行**：平行會出 LoadImageError，用 `if ($?)` 或分開 bash 呼叫。
- **09/16 新批次公布函**：$BySender 視圖下「公布函系統通知」群組可能包含多達 10+ 封今日未讀（不只 4 封）；務必展開群組後全數掃描處理。

## 信箱匯出＋加密信件 UI 讀取（2026-09-24 實測新流程）

同一 skill 也涵蓋「**把信箱整批匯出分析**」與「**開啟加密個人機密信件讀數值**」，全程同樣無 JNI。

### A. 信箱整批匯出（Structured Text）
1. Notes 工作台 → 信箱視圖（或任一視圖）→ `File > Export`（**檔案→匯出**）選 `Structured Text (.stx or .txt)`。
2. 產物是 **Big5/STI** 文字檔（例 `C:\lotus\Notes\Data\_inbox_export.txt`，396 封郵件約 2MB）；PowerShell 讀取要指定 `Encoding:Big5`。
3. 解析主旨與寄送日期（每封郵件區塊內 `PostedDate` 欄位），產生乾淨 UTF-8 清單（例 `subj_dates.txt`）。**這是以主旨過濾/分類信件的主資料源**（不用逐封開信）。

### B. 讀取**加密**信件內容（Encrypt: 1 信件，匯出檔不含欄位值）
- 加密信件在匯出檔中只有表單設計＋郵件封包，**無欄位數值**（例「2025年度主管獎勵金所得明細單」$Fields 存在但無值）。要拿數值只能**在 Notes UI 開啟信件**＋OCR。
- 開信方式：**先單擊該列**（確認列已選取），再 **dblclick 或按 Enter**。實測直接 dblclick 有時會誤開相鄰列（預覽窗格標題魚目混珠）；誤開時看「標題列」確認落在哪封。
- 開信後**內容數值區用 OCR 讀**：數字欄位（金額/稅額）OCR 可靠；中文欄位名因字小常認錯字，**比對邏輯為主、欄位名為輔**（例：18,000=所得稅、5,327=健保補充保費、336,673=合計實發，驗算 360,000−18,000−5,327=336,673 吻合）。
- 讀完要回視圖：**點上方 workspace 分頁列**的「信箱」分頁（視窗內 y≈86-105），或 memo 標題分頁右上 X；不要用 Ctrl+W（詳下雷區）。

### C. 本次新雷區（2026-09-24 踩到）
- **Ctrl+W / Escape 有時會彈「文件已刪除」對話框**（鍵盤導覽在錯誤焦點時觸發刪除）：實測按 Esc/Ctrl+W 想關 memo 卻跳出 `文件已刪除` 警告 → 可能真的刪掉一封信。處理：看到對話框先**重新 OCR 定位「確定」再點**（勿用 a11y 原始座標直接點），並在關閉後**回視圖確認目標列仍在**（未被誤刪）。
- **誤點相鄰列**：dblclick 前務必「先單擊→截圖→確認反白列正確」再按 dblclick，避免開錯信。
- **切回信箱視圖後捲動位置會變**：每次操作後列 y 全變，**一律重新 OCR 現量目標列**，不可沿用上次 y。
- **小字 OCR 誤認上限**：約 <28px 高的中文字 OCR 幾乎必錯（酬→凳、傳→傅/送、獎→樊、勵→金/勤、單→軍/細、細→细）。改善：`crop.py <src> <out> <x> <y> <r> <b> 4`（LANCZOS 4x）放大後再 OCR，字高≥40px 較可靠；仍錯就用數字/匯出檔交叉驗證。
- **a11y 座標陷阱**：Computer Use `get_app_state` 的 Frame 座標是視窗相對座標，轉螢幕要加視窗左上角；直接拿 a11y 座標當螢幕座標點 = 點到 OpenCode 終端機。

### D. 本 skill 新增/確認可用腳本
- `focus.ps1 <name>`：設定前景並回報 `target=<hwnd> fg=<hwnd> fgTitle='..' match=True/False`（比 winlist.ps1+手動 SetForegroundWindow 快）。
- `click.ps1 <screenX> <screenY> click|dblclick`：螢幕絕對座標單擊/雙擊。**不含前景設定** → 使用模式：`focus.ps1；sleep；click.ps1` 同一命令串。
- `cap_hwnd.ps1` / `capture_fullscreen.ps1`：視窗/全螢幕截圖備援。

## scripts\ 工具簡介

| 腳本 | 用途 |
|------|------|
| `hcl_notes_forwarder.py` | 可直接執行的批次工具：找紅字未讀公布函、直接轉寄、驗證完成訊息、刪除原信 |
| `run_hcl_notes_forwarder.cmd` | Windows 雙擊/命令列啟動器，優先使用本機 Python 3.13 |
| `build_exe.ps1` | 用 PyInstaller 打包 `hcl_notes_forwarder.py` 為單一 exe |
| `capture_win.ps1 <winName> <outPng>` | 抓指定視窗（如 nlnotes）內圖到 PNG |
| `ocr_screen2.py <png> <ocrTxt>` | RapidOCR 中文 → 每行 `[x0-x1,y0-y1] 文字`（座標為該圖像素座標） |
| `crop.py <src> <out> <x> <y> <right> <bottom> <scale>` | 裁切並放大（座標為原圖像素） |
| `click.ps1` / `click2.ps1 <wx> <wy> <winL> <winT> <kind>` | SetCursorPos+mouse_event 在螢幕絕對座標點擊（`click.ps1 <sx> <sy> click\|dblclick`；不含前景設定） |
| `zclean.ps1` | 最小化其他頂層視窗，讓 Notes 接收輸入 |
| `winlist.ps1` | 列出頂層視窗、pid、位置、z-order |
| `rowclass.py` | （依寄件者視圖）逐列掃紅/黑像素，判未讀/已讀 |
| `focus.ps1`/`focus2.ps1`/`topmost.ps1` | 設定前景 / 置頂（輔助） |
| `cap_hwnd.ps1` / `capture_fullscreen.ps1` | 以 HWND／GDI 全螢幕截圖備援 |

> GDI 全螢幕截圖（對話框用）範例見本 skill 對話框段落；核心是 `GetDesktopWindow`+`GetWindowDC`+`BitBlt` 到 1920x1080 bitmap。

## 座標速查（範例機，僅參考；每次以 OCR 現量）

- 直接轉寄：螢幕 (1038,141)。
- 「選取名稱」對話框：左欄群組列 `工三碳化矽專案組-03-全組(21)` 約 (1065,374)；「新增(A)」約 (1370,365)；「確定」約 (1579,524)；「取消」約 (1662,524)。
- 完成訊息「系統已完成轉發作業!」確定：約 (982,590)。
- 已傳送視圖頂端刷新：F9。

## 本機實測筆記（2026-09-15，FGES 公布函直接轉寄，全程驗證通過）

本機環境四壁：Notes 前有「OpenCode 終端機 + Edge(Oracle Fusion)」兩個不受 zclean 控制的覆蓋源，將 Notes 移右側一勞永逸。

- **OpenCode 終端機會搶焦點**：每次 bash 工具執行後 TUI 回到前景，會覆蓋螢幕左側（實測 `x0-733`、全高），點擊若落在該區=點錯。
- **zclean 無效案例**：ignore 清單含 `OpenCode`/`chrome`/`msedge`，Edge(Oracle Fusion 表單)會留在原位遮住 Notes；光 zclean 不夠。
- **對策＝把 Notes 整個移到右側**：`SetWindowPos(nlnotes, TOPMOST, 780,0,1140,1035, 0x0040)` + `SetForegroundWindow`，與終端機 x0-733 完全不重疊；對話框是 Notes 子視窗也跟著右移，全部點擊都在安全區。
- **每次點擊前同命令重述**：在同一個 PowerShell 命令內 `SetWindowPos(TOPMOST)+SetForegroundWindow+sleep+click`，不要跨工具呼叫依賴前景狀態。
- **Notes 視窗位置會漂移**：本流程實測 winlist 依序回報 (640,0)→(470,21)→(953,0)→(780,0)；❌ 死記座標，✅ 每次 `GetWindowRect` 現量，或先把視窗固定到右側後再算（winX、winY 直接加視窗左上角）。
- **存檔目錄要先建立**：`capture_win.ps1` / GDI 全螢幕存 PNG 前，輸出目錄若不存在，`$bmp.Save()` 會報「在 GDI+ 中發生泛型錯誤」且存不出檔。
- **開信後視圖會變**：開過信後返回列表，新信可能插到頂、未讀數變動、列位重排；刪除前先 Ctrl+Home 回頂並重新 OCR 定位（本例 FGES 列從第 1 列變第 2 列）。
- **雙重確認列身分**：OCR 中文常錯字，判斷列以「主旨關鍵字（如 FGES-T-SSF42）」+「日期時間（2026/09/15 11:07）」雙重比對，避免刪錯信。
- **「離開」未必能點**：轉寄後 memo 工具列小字 OCR 認不到，點定位不准；改用 memo 分頁右上角 **X**（視窗內 ~(548,94)）或鍵盤 Escape 關閉 memo。
- **完成訊息實測**：「系統已完成轉發作業!」確定 (982,590) 與速查一致；出現此訊息即代表轉寄已送出。
- **刪除原信**：完成訊息出現後才回列表刪除；重新 OCR 定位列 → 單擊選列 → Delete；實測 Notes 11 未彈確認對話框即消失；刪後再 OCR 確認目標列消失、鄰近新信仍在（未誤刪）。
- **2026-09-25 實測補強**：大量處理時 Notes 文件分頁會堆疊，可能切不回 `$BySender`；改用每批 4-5 封重啟 Notes，再從工作區開信箱回 `$BySender`，穩定完成剩餘紅字。成功寄出後刪除原信，信箱未讀數會下降。
- **2026-09-25 y 起點補強**：公布函系統通知群組若剛好在清單頂部，第一封未讀可能落在視窗 y≈250；舊版從 y=350 掃描會漏判。新版 `hcl_notes_forwarder.py` 預設 `--scan-start-y 220`，且優先用 `capture_win.ps1` 抓 Notes 視窗本身。

## 實測例：主管獎勵金統整（2026-09-24，信箱匯出＋加密信件讀取兌現）

真實任務全流程範例，證明上述流程可行：

1. **匯出信箱**：File→Export Structured Text → `_inbox_export.txt`（Big5，2MB）。解析 396 封主旨+日期至 UTF-8 清單 → 以主旨過濾出「主管獎勵金」5 封（2020/2021/2022/2023/2025 年度），金額（RdlAmt）由匯出檔欄位直接取得。**2024 年度無此信；2025 年度 Encrypt:1 匯出無值**。
2. **開加密信**：信箱視圖 OCR 定位該列（日期 2026/05/19 對），先單擊確認反白再 dblclick → 標題「主管獎勵金所得明細單」＝成功開信。OCR 讀出**獎勵金額 360,000／所得稅 18,000／健保補充保費 5,327／合計實發 336,673**，驗算 360,000−18,000−5,327=336,673 ✓。
3. **回視圖**：點上方 workspace「信箱」分頁（視窗內 y≈86-105）。
4. **絆腳石**：曾誤開相鄰「提示文件」列（dblclick 太急）、鍵盤 Esc/Ctrl+W 觸發「文件已刪除」對話框（小心處理並事後回視圖確認原列仍在）、小字 OCR 認錯中文字（靠數字+匯出檔交叉驗證）。
5. 產出 `主管獎勵金mail統整報告.md`：年度分類表＋基期比例分析＋2025 明細。
