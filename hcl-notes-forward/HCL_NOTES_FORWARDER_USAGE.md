# HCL Notes 公布函自動轉寄工具使用說明

## 檔案位置

主要程式：

```text
D:\80-Opnecode\Projects\OpenCode_skill\hcl-notes-forward\scripts\hcl_notes_forwarder.py
```

Windows 啟動檔：

```text
D:\80-Opnecode\Projects\OpenCode_skill\hcl-notes-forward\scripts\run_hcl_notes_forwarder.cmd
```

打包 EXE 腳本：

```text
D:\80-Opnecode\Projects\OpenCode_skill\hcl-notes-forward\scripts\build_exe.ps1
```

## 功能

這個工具會自動處理 HCL Notes 信箱中：

- `依寄件者 ($BySender)` 視圖
- `公布函系統通知` 群組
- 紅色未讀的「公佈函已發佈」郵件

預設流程：

1. 找到紅色未讀公布函。
2. 開啟郵件。
3. 按「直接轉寄」。
4. 選取收件群組：`工三碳化矽專案組-03-全組(21)`。
5. 等待 Notes 顯示「系統已完成轉發作業」。
6. 成功後刪除原信。

如果沒有看到完成訊息，工具會停止，不會刪除原信。

## 第一次使用：先測試不寄信

先開啟 HCL Notes，確認你已登入並能正常看到信箱。

然後在 PowerShell 執行：

```powershell
cd D:\80-Opnecode\Projects\OpenCode_skill
.\hcl-notes-forward\scripts\run_hcl_notes_forwarder.cmd --dry-run --debug
```

這個模式只會偵測紅色未讀公布函，不會寄信，也不會刪信。

## 正式執行

確認 dry-run 正常後，執行：

```powershell
cd D:\80-Opnecode\Projects\OpenCode_skill
.\hcl-notes-forward\scripts\run_hcl_notes_forwarder.cmd --max-messages 30 --debug
```

預設會：

- 最多處理 30 封。
- 每成功 5 封重啟一次 Notes，避免分頁堆太多。
- 成功轉寄後刪除原信。

## 只轉寄，不刪除

如果只是測試，不想刪除原信：

```powershell
.\hcl-notes-forward\scripts\run_hcl_notes_forwarder.cmd --max-messages 3 --no-delete --debug
```

## 改收件群組

預設收件群組是：

```text
工三碳化矽專案組-03-全組(21)
```

如果要改成其他群組：

```powershell
.\hcl-notes-forward\scripts\run_hcl_notes_forwarder.cmd --recipient "群組名稱" --dry-run --debug
```

注意：目前工具的通訊錄選取座標是依本機實測畫面整理。其他電腦或其他群組第一次使用時，務必先用 `--dry-run --debug` 確認。

## 常用參數

| 參數 | 說明 |
|---|---|
| `--dry-run` | 只偵測，不寄信、不刪信 |
| `--debug` | 儲存截圖，方便校正 |
| `--max-messages 30` | 最多處理 30 封 |
| `--restart-every 5` | 每成功 5 封重啟 Notes |
| `--no-delete` | 成功轉寄後不刪除原信 |
| `--scan-start-y 220` | 從 Notes 視窗內 y=220 開始掃描紅色未讀列；若 dry-run 漏抓，可調整此值 |
| `--recipient "群組名稱"` | 指定收件群組 |
| `--notes-exe "路徑"` | 指定 Notes 執行檔路徑 |

## 打包成 EXE

可以用 PyInstaller 打包成單一執行檔。

執行：

```powershell
cd D:\80-Opnecode\Projects\OpenCode_skill
.\hcl-notes-forward\scripts\build_exe.ps1
```

打包完成後，EXE 會在：

```text
D:\80-Opnecode\Projects\OpenCode_skill\dist\hcl-notes-forwarder.exe
```

如果 `dist` 位置不同，PowerShell 會在完成時顯示實際輸出位置。

## 其他電腦使用方式

1. 安裝 HCL Notes。
2. 確認可以正常登入信箱。
3. 從 GitHub 下載或 clone：

```text
https://github.com/yd7148/OpenCode_skill
```

4. 進入 repo：

```powershell
cd OpenCode_skill
```

5. 第一次先測試：

```powershell
.\hcl-notes-forward\scripts\run_hcl_notes_forwarder.cmd --dry-run --debug
```

6. 確認畫面正確後正式執行：

```powershell
.\hcl-notes-forward\scripts\run_hcl_notes_forwarder.cmd --max-messages 30 --debug
```

## 注意事項

- 成功轉寄後會刪除原信，這是現在的預設行為。
- 直接轉寄不一定會在「已傳送」留下紀錄，所以工具以 Notes 的完成訊息作為成功判斷。
- 如果 Notes 畫面被其他視窗遮住，可能會點擊失敗。
- 如果 DPI、解析度或 Notes 版面不同，必須先 dry-run 校正。
- 若工具停下來，通常代表它沒有確認到完成訊息；這種情況下原信不會被刪除。
- 2026-09-25 補強：工具會優先抓取 HCL Notes 視窗本身，並從較上方的清單位置開始掃描，避免公布函列在 y=250 左右時漏判。
