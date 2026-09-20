---
name: comsol-linsolver-benchmark
description: A/B benchmark a COMSOL Multiphysics model's linear solver (MUMPS CPU vs cuDSS GPU vs PARDISO) by directly patching the solver node inside the .mph package's embedded dmodel.xml, then running comsolbatch with a fixed time budget while sampling nvidia-smi. Covers the root cause of "cuDSS never actually used" (solver set on a DISABLED node vs the ACTIVE node referenced by the Fully Coupled solver), the verified patch procedure, the 20-minute benchmark protocol, GPU-utilization monitoring, and the measured FCFC Coil results (cuDSS = 2.5x simulation-time progress). Use when asked to "比較 MUMPS 與 cuDSS", "cuDSS GPU 求解", "GPU 求解器基準測試", "改 mph 內嵌求解器", "linsolver patch", or to benchmark/verify which linear solver a COMSOL model really uses.
license: MIT
compatibility: opencode
metadata:
  audience: opencode agents
  workflow: comsol-linsolver-benchmark
  languages: zh-TW
---

# comsol-linsolver-benchmark — COMSOL 線性求解器 A/B 基準測試（MUMPS vs cuDSS）

本 skill 記錄如何對**既有的 `.mph` 模型**做線性求解器基準測試與驗證：直接修改
`.mph`（ZIP 包）內嵌的 `dmodel.xml`，把實際使用的求解器節點切換成
MUMPS / cuDSS / PARDISO，再用 `comsolbatch` 固定時間預算求解，並以
`nvidia-smi` 監控 GPU 利用率。

> 與 `comsol-mcp`（透過 opencode MCP 工具操作）無關；本流程完全繞過 MCP。
> 與 `comsol-analyzer`（分析模型內容）不同，本流程會**修改** solver 設定並求解。

## 核心知識（最重要的坑）

**COMSOL solver 設定藏在 `.mph` 內建的 `dmodel.xml`，而且設定在「停用的節點」= 沒有效果。**

- `.mph` 是 ZIP，內含 `dmodel.xml`（通常 5–8 MB）、`smodel.json`、`mesh1.mphbin`、
  一堆 `solutionblock*.mphbin`（可能幾十 MB 到幾百 MB）等。
- 求解樹結構範例（`sol1` / Time solver `t1`）：
  - `t1`（Time solver）底下有許多 Feature：`dDef`、`d1`..`d4`（Direct）、
    `iDef`/`i1`..（Iterative）、`se1`（Segregated）、`ss1`..（SegregatedStep）、
    `fc1`（Fully Coupled）、`mg1`（Multigrid）… 各自有 `entityFlags`（狀態）。
  - **只有 `entityFlags="NODEACTIVATE"`（啟用）的節點會被執行**；
    `entityFlags="DISABLED"` 的節點完全沒作用。
  - Fully Coupled（`fc1`）的 `p:linsolver` 是 `Reference="/sol/sol1/feature/t1/feature/d4"`
    這類指標，實際線性求解器由被參考的 Direct 節點決定。
- **典型悲劇**：把 `cudss` ／`mumps` 設在一個 `DISABLED` 的 Direct 節點
  （例如 `d1` 或 `dDef`）→ 求解照舊用 PARDISO → GPU 利用率 0%、兩種
  「求解器」結果幾乎一樣 → 以為 cuDSS 沒用或白費力氣。

### 確認「實際在用哪個求解器」

1. 解包並抽取 `dmodel.xml`（見下方方法）。
2. 定位真正啟用的 Direct 節點（`entityFlags` 含 `NODEACTIVATE`，通常是 `d4`），
   讀它的 `p:linsolver`：
   `<propertyValue T="30" value="pardiso" name="p:linsolver">`。
3. 確認 Fully Coupled `fc1` 的參考指向那個節點
   （`name="p:linsolver" Reference="/sol/sol1/feature/t1/feature/d4"`）。
4. 全檔統計：`value="cudss"` / `value="mumps"` / `value="pardiso"` 各有幾次。
   注意 `mumps` 字串常出現在 CDATA 的**預設值列表**（`linsolvermumps` 等），
   不要誤判為目前設定。**以 `value="..." name="p:linsolver"` 為準。**

## 環境（這台機器）

| 項目 | 值 |
|------|-----|
| COMSOL | 6.4.0.293，`C:\Program Files\COMSOL\COMSOL64\Multiphysics` |
| comsolbatch | `...\bin\win64\comsolbatch.exe` |
| comsolserver.dll | `ext\server\win64\` |
| cuDSS DLL | `ext\cudss\win64\`、CUDA 12 在 `ext\cuda\win64\`（都要進 PATH 才能載入） |
| GPU | NVIDIA GeForce GTX 1650（4.00 GB，CC 7.5） |
| nvidia-smi | `C:\Windows\System32\nvidia-smi.exe`（**不是** `C:\Program Files\NVIDIA Corporation\NVSMI\...`） |
| Python | 系統 python（會用 zipfile 解包 .mph） |

**cuDSS 需求**（COMSOL 官方）：顯示卡 CC ≥ 6.0、CUDA 12.4–12.9、cuDSS 0.7.1、
driver ≥ 551.61。本機 driver 591.86、GTX 1650 CC 7.5 — 符合。

## 流程

### 1. 抽取並檢查 solver 設定

```powershell
# .mph 即 ZIP：直接抽 dmodel.xml（無需改副檔名）
Add-Type -AssemblyName System.IO.Compression.FileSystem
$z = [System.IO.Compression.ZipFile]::OpenRead("...\model.mph")
$e = $z.GetEntry("dmodel.xml")
[System.IO.Compression.ZipFileExtensions]::ExtractToFile($e, "dmodel.xml", $true)
$z.Dispose()
```

用 `rg`/`Select-String` 找：

```
value="pardiso" name="p:linsolver"
name="p:linsolver" Reference="/sol/sol1/feature/t1/feature/d4"
entityFlags T="51">NODEACTIVATE
```

### 2. 修改 solver 節點（建立新檔，不覆蓋原檔）

寫 Python 腳本：讀 `dmodel.xml` → regex 定位
`<SolverFeature op="Direct" tag="d4"[^>]*>` 區塊 → 只把該區塊第一個
`value="pardiso" name="p:linsolver"` 改 `value="cudss"`（或 `mumps`）→
重新打包 `.mph`（逐 entry copy，替換 `dmodel.xml`）。

```python
import zipfile, re, os
src = r"...\model.mph"; dst = r"...\model-cudss.mph"
zin = zipfile.ZipFile(src)
dm = zin.read("dmodel.xml").decode("utf-8", "replace")
m = re.search(r'<SolverFeature op="Direct" tag="d4"[^>]*>', dm)
s = m.start(); seg = dm[s:s+2500]
seg2 = seg.replace('value="pardiso" name="p:linsolver"',
                   'value="cudss" name="p:linsolver"', 1)
dm2 = dm[:s] + seg2 + dm[s+len(seg):]
assert dm2.count('value="cudss"') >= 1
zout = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
for info in zin.infolist():
    data = zin.read(info.filename)
    if info.filename == "dmodel.xml": data = dm2.encode("utf-8")
    zout.writestr(info, data)
zout.close(); zin.close()  # 大檔需耐心（幾百 MB，約 1–3 分鐘）
```

驗證新檔後，兩版本只剩那個節點不同 → A/B 公平。

### 3. comsolbatch 求解 + GPU 監控（20 分鐘預算）

- **路徑含空格**：`comsolbatch` 引數不要用 `Start-Process -ArgumentList` 的陣列
  （空格會被切斷成錯誤檔名）；用單一引數字串或寫成 `.bat` 檔。
- **不要在同一個 bash 呼叫內 `WaitForExit` 20 分鐘**（會被中斷）；
  改用 `.bat` + 背景 powershell，或 `cmd /c start` 分離。
- GPU 監控用**獨立隱藏 powershell** 每 0.5 s 取樣寫入 log：

```powershell
# gpu_mon.ps1：param($logPath,$seconds)
for ($k=0; $k -lt $seconds*2; $k++) {
  $t = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
  $l = & "C:\Windows\System32\nvidia-smi.exe" --query-gpu=utilization.gpu,utilization.memory,memory.used,power.draw,temperature.gpu --format=csv,noheader,nounits 2>$null
  "$t $l" | Out-File -Append -Encoding utf8 $logPath
  Start-Sleep -Milliseconds 500
}
```

### 4. 讀取結果

- **cuDSS 是否啟用**：`batch*.log` 開頭要出現
  `GPU 偵測 0: NVIDIA GeForce GTX 1650 (4.00 GB)` 與 `使用 cuDSS.`
  （為中文／big5；PowerShell 顯示亂碼為正常，grep `cuDSS` 即可）。
- **進度**：log 內每步一行 `285  516.19  4.2346  5857  358 5512  1  0  77 ...`
  = 步數、時間 t、dt、Sol 累計、Jac 累計、…。解析第 3–6 欄（t、dt、Sol、Jac）。
- **GPU 利用率**：gpu.log 每行 `日期 時間 U, MU, MEM[, PW, TP]`；
  解析時注意**欄位數**（4-part：U=parts[2], MEM=parts[3]；7-part：MEM=parts[4]）。
- **log 編碼**：comsolbatch log 是 big5（繁體中文 Windows），用
  `encoding="utf-8", errors="replace"` 讀取即可抓數字欄位。

## 實測結果（FCFC Coil，已驗證）

- 模型：FCFC Coil versionV1，study `std4`（FrequencyTransient），116,960 DOF。
- 真正啟用的 Direct 節點：`d4`（`fc1` Fully Coupled 所參考）。
- **很關鍵**：原始 `BENCH-cuDSS-fixed.mph` 與 `BENCH-mumps.mph` **內檔都是 pardiso**，
  `value="cudss"` = 0 次！→ 之前所有 GPU 0% 的測試都是假象。
- patch 後 cuDSS log 確認：`使用 cuDSS.`；GPU 平均約 10%、最大約 789 MiB；
  MUMPS 對照組 GPU 0% / 140 MiB。
- **21.5 分鐘預算結果**：

| 指標 | MUMPS | cuDSS |
|------|-------|-------|
| 模擬時間推進 t | 210.05 | **524.66** |
| 步數 | 203 | 287 |
| Sol 次數 | 5,669 | 5,886 |
| Jac 次數 | 243 | 360 |
| 線性吞吐 Sol/min | 264 | 274 |
| GPU 平均利用 | 0 % | ~10 % |

→ **cuDSS 讓時間推進增 2.5 倍**；單次求解更快（吞吐接近、但每步推進更大）。
GPU 利用率不高屬正常：116k DOF 對 GTX 1650 太小，LU 分解最吃不滿 GPU。

## Gotchas

- `.mph` 若是幾百 MB（含大量 `solutionblock*.mphbin`），重打包很慢；**只改
  `dmodel.xml`**，其餘 entry 原樣 copy。
- `d4` 的 `p:linsolver` 若該區塊還有其他 `pardiso`（mg coarse solver 等），
  **只 replace 第一個、且限在 `tag="d4"` 區塊內**，別整檔全替換。
- 想驗證 cuDSS DLL 裝載：把 `ext\cuda\win64` 與 `ext\cudss\win64` 加入 PATH 後
  `LoadLibrary("cudss64_0.dll")` 會成功；不加 PATH 會 Win32Error 126。
- comsolbatch 啟動 20–30 s（JVM + license）才進入求解，計時別算錯。
- 不要同時跑兩個 comsolbatch（license／CPU／輸出檔衝突）。
- 若 `solved.mph.status` 寫 `Running` 但程序已死 → 之前那次是被外力的 bash
  中斷（`[Tool execution was interrupted]`），資料仍可用但標記為「被中斷」。
- `.mph` >4 GB 時 `comsolbatch` 載入需 5–15 s（含 solutionblock 解壓）；計時從連接成功開始算。
- **mph client-server 單一 session 限制**：同一 Python process 只能有一個 `mph.Client()`。
  需要多次運行時用不同 port 或在同一 client 上連續操作（不要 re-import mph）。
- **`getString('tlist')` vs `getDoubleArray('tlist')`**：解樹的 Time feature 同時支援兩者。
  `getString` 回傳原始 range 表達式（用於修改），`getDoubleArray` 回傳展開值（用於分析）。

## 參考檔案（這台機器）

| 檔案 | 說明 |
|------|------|
| `D:\FCFC\2026-04-24-test\New2 FCFC Coil versionV1-BENCH-cuDSS-actual.mph` | 已 patch 的 cuDSS 版 |
| `D:\FCFC\2026-04-24-test\New2 FCFC Coil versionV1-BENCH-mumps-actual.mph` | 已 patch 的 MUMPS 版 |
| `<run>\stdout.txt` / `batch*.log` | 求解進度日誌（big5） |
| `<run>\gpu*.log` | nvidia-smi 監控 |
| 正式報告 | `D:\FCFC\2026-04-24-test\FCFC_Coil_cuDSS_vs_MUMPS_A-B_基準測試報告.md` |