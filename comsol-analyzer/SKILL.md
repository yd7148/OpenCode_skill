---
name: comsol-analyzer
description: Analyze COMSOL Multiphysics .mph model files by extracting and parsing their internal XML/JSON structure. Produces a detailed Traditional Chinese markdown report covering model metadata, parameters, physics interfaces, geometry, materials, studies, and mesh. Use when asked to "分析 COMSOL 模型", "說明 .mph 檔案", "COMSOL 模型結構", "comsol model analysis", or to examine a .mph file. Also use for COMSOL 續解 / 帶窗奇異性診斷 / comsolbatch Java 求解腳本 / 暫態求解器疑難排解 (time-dependent solve experiments, continuing solves past stored time, comsolbatch Java scripting, solver-failure diagnosis).
license: MIT
compatibility: opencode
metadata:
  audience: workflow
  languages: opencode agents, comsol-analysis, zh-TW
---

# comsol-analyzer — COMSOL .mph 模型檔案分析

Analyze a COMSOL Multiphysics `.mph` model file and produce a detailed Traditional Chinese markdown documentation report. The `.mph` file is a ZIP archive containing XML + binary data; this skill guides extraction and parsing without requiring COMSOL installed.

## When to use

- User says 分析 COMSOL 模型 / 說明 .mph 檔案 / COMSOL 模型結構 / comsol model analysis, or hands you a `.mph` file to document.
- Also use when the user asks about the physics, geometry, materials, or studies defined in a COMSOL model.

## Prerequisites

- **No COMSOL installation required** — the `.mph` file is a standard ZIP archive.
- **無額外 Python 套件（無依賴）** — 只需標準程式庫 `zipfile` / `xml.etree` / `json`，macOS 與 Windows 內建 Python 3 皆可用。
- Windows: PowerShell 5.1（內建）。macOS: 任一 Python 3 + `unzip`（內建）。
- Working temp directory: 任一支暫存目錄（如 `/var/folders/.../tmp` 或 `C:\Users\...\AppData\Local\Temp\opencode`）

## ⚠ 大型檔案（>1 GB）處理原則（實測重點）

- 真實工程 `.mph` 常達 **1–6 GB**，內含數百個 33 MB 的 `solutionblock*.mphbin`（暫態解區塊）。**絕對不要 `Expand-Archive` 整個解壓縮**——會超過工具 120 秒 timeout（實測 5.9 GB 檔案失敗）。
- 正確做法：**用 .NET `ZipFile.OpenRead()` 直接從 ZIP 讀取指定 entry**，只抽取需要的文字檔（`dmodel.xml`、`modelinfo.xml` 等），完全不落地解壓。
- 若 `ZipFile.OpenRead` 丟錯 `IOException: 另一個處理序正在使用檔案`，代表 **COMSOL（ComsolUI 程序）正開啟此檔**（會有同名的 `.lock` 檔）。先以 `FileShare.ReadWrite` 複製一份再開檔。
- 見下方「Step 1（替代方案）」。

## .mph File Structure

A COMSOL `.mph` file is a ZIP archive containing:

| File | Content | Readable? |
| --- | --- | --- |
| `fileversion` | COMSOL version string (e.g. `2092:COMSOL 6.4.0.429`) | Yes (text) |
| `model.xml` | Minimal XMI model wrapper | Yes (XML) |
| `modelinfo.xml` | Model metadata: version, physics, license, geometry info | Yes (XML) |
| `dmodel.xml` | **Core model definition** — all physics, geometry, materials, studies, results | Yes (XML, 5–60 MB) |
| `smodel.json` | Structured model tree (JSON) — useful for quick parameter/setting lookup | Yes (JSON) |
| `guimodel.xml` | GUI state (current view, selected nodes) | Yes (XML) |
| `auxiliarydatainfo.json` | Auxiliary data file references | Yes (JSON) |
| `usedlicenses.txt` | List of required license modules | Yes (text) |
| `geometry*.mphbin` | Binary geometry data (Parasolid/CAD kernel) | Binary |
| `solution*.mphbin` | **Binary solution data — 大型暫態檔的主體（每塊約 32–33 MB）** | Binary |
| `mesh*.mphbin` | Binary mesh data | Binary |
| `geommanager*.mphbin` | Geometry manager data | Binary |
| `tabledata*.mphbin` | Table data for parametric sweeps | Binary |
| `fileids.xml` | Internal file ID mappings | Yes (XML) |
| `clusterignore.xml` | Cluster computation ignore list | Yes (XML) |

## Pipeline (follow in order)

### Step 1 (首選) — 用 .NET 直接讀取 ZIP entry（大型檔案適用，不落地解壓）

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem
$src = "<path_to_model>.mph"          # 原檔（可能 >1 GB）
$zip = [System.IO.Compression.ZipFile]::OpenRead($src)
$entry = $zip.GetEntry('modelinfo.xml')
$reader = New-Object System.IO.StreamReader($entry.Open())
$modelinfoXml = $reader.ReadToEnd(); $reader.Close()
# 需要時抽取其他 entry：
#   fileversion / dmodel.xml / smodel.json / guimodel.xml / usedlicenses.txt
$zip.Dispose()
# 之後把 dmodel.xml 內容寫入暫存檔供 Read/Grep 工具分析（避免單一 CLI 呼叫輸出過大）：
[System.IO.File]::WriteAllText("C:\Users\<user>\AppData\Local\Temp\opencode\dmodel.xml", $dmodelXml)
```

**鎖檔處理**：若 `OpenRead` 或 `File.OpenRead` 丟 `IOException: 檔案正在使用中`，代表 COMSOL GUI（ComsolUI 程序）正開著此檔（同目錄會出現 `<檔名>.lock`）。複製一份後再讀：

```powershell
$fs = [System.IO.File]::Open($src, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
$tmp = "C:\Users\<user>\AppData\Local\Temp\opencode\model_copy.mph"
$copyFs = [System.IO.File]::Create($tmp); $fs.CopyTo($copyFs); $copyFs.Close(); $fs.Close()
# 之後對 $tmp 用 ZipFile.OpenRead 即可
```

### Step 1b (僅小檔 <500 MB 才用) — Copy + Expand-Archive

```powershell
$src = "<path_to_model>.mph"
$tmpZip = "C:\Users\<user>\AppData\Local\Temp\opencode\comsol_temp.zip"
$extractDir = "C:\Users\<user>\AppData\Local\Temp\opencode\comsol_extract"
Copy-Item $src $tmpZip -Force
Expand-Archive -Path $tmpZip -DestinationPath $extractDir -Force
```

### Step 2. Read metadata files (parallel reads)

Read these files simultaneously for quick overview:

- `fileversion` — COMSOL version
- `modelinfo.xml` — model type, physics list, license info, computation history
- `usedlicenses.txt` — required modules
- `guimodel.xml` — GUI state (current study, current view)

### Step 3. Parse `dmodel.xml` for full model details

The `dmodel.xml` is the core file (often 5–60 MB). Parse it section by section:

#### 3a. Global Parameters

Search for `<ModelParam tag="param">` and extract `<expressions>` elements:

- Parameter names, expressions, values
- Parameter groups and descriptions

#### 3b. Physics Interfaces

Search for `<Physics op="...">` tags. Each physics interface has:

- `op` attribute: the physics type (e.g. `InductionCurrents`, `HeatTransferInSolidsAndFluids`, `LaminarFlow`)
- `tag` and `name`: identifier and display name
- `PhysicsFeatureList`: individual features (boundary conditions, sources, material models)
- Key features to look for:
  - **Coil definitions** (`op="Coil"`): coil type (Circular/Numeric),匝數 N, current source, wire properties
  - **Material models** (`op="AmperesLawFluid"`, `op="SolidHeatTransferModel"`): constitutive relations
  - **Boundary conditions**: `NoFlux`, `DiffuseSurface`, `InitialValues`, etc.
  - **Multiphysics couplings**: `<MultiphysicsCoupling op="...">` — electromagnetic heating, radiation coupling

#### 3c. Geometry

Search for `<GeomSequence tag="geom1">`:

- Geometry kernel type (`geomrep`: `cadps` = Parasolid)
- Units (`lengthUnit`, `angularUnit`)
- Bounding box (`boundingBox`)
- Entity counts (`numEntities`: vertices, edges, faces, domains)
- Geometry features (`<GeomFeature op="...">`):
- `Polygon`, `Circle` — 2D sketch primitives
    - `Revolve`, `Extrude` — 3D operations
    - `Difference`, `Union`, `Intersection` — Boolean operations
    - `Array` — pattern阵列
    - `Extract`, `PartitionEdges` — post-processing
    - `Finalize` — formation of one body
    - `RemoveDetails` — geometry simplification
- Work planes (`<WorkPlaneFeature op="WorkPlane">`): plane orientation (xy/xz/yz)
- **比較兩檔幾何時**：多邊形座標存在 `<GeomFeature>...<param param="p:table">` 內的 `valueMatrix="..."` 屬性中（注意屬性順序為 `valueMatrix` 在前、`name=...` 在後）。用自動化方式逐一比對各多邊形頂點即可精準找出尺寸差異（例如本專案中 `pol1/pol16/pol18` 所有 z=20→z=50，即「底面 −30mm」）。

#### 3d. Materials

Search for `<Material op="Common" tag="mat...">`:

- Material name and identifier
- Property values (thermal conductivity, density, heat capacity, electrical conductivity, etc.)
- Temperature-dependent properties (look for interpolation table data)

#### 3e. Studies

Search for `<StudyList>` → `<Study>`:

- Study types: `CoilCurrentCalculation` (CCC), `Frequency`, `Transient`, `Stationary`, `FrequencyTransient`
- Study parameters: frequency, time range, parametric sweep
- Computation history: time, date, COMSOL version used

#### 3f. Mesh

Search for `<MeshSequence>` or `<mesh>`:

- Mesh type (Free, Swept, Mapped, Tet)
- Element size settings
- Element counts

#### 3g. Results/Plots

Search for `<ResultFeature>`:

- Plot groups (`<PlotGroup>`)
- Surface plots, contour plots, 3D plots
- Data expressions being plotted

#### 3h. Physics 啟用狀態（重要）

每個 `<Physics op="...">` 的 `<entityFlags T="51">` 若含 `DISABLED`，代表該物理場**已停用、不參與求解**（即使 modelinfo 列有六個 physics，實際求解可能只剩熱傳/輻射/磁場/PID）。比較模型時務必逐一檢查狀態，不要只看 physics 清單。

常見解析片段（`physicsStatus`）：

```powershell
# 對 dmodel.xml 內容抓 physics 名稱與啟用狀態：
$m = [regex]::Matches($xml, '<Physics op="([^"]+)" tag="([^"]+)"[\s\S]*?<entityFlags T="51">([^<]*)</entityFlags>')
foreach ($mm in $m) {
  $status = if ($mm.Groups[3].Value -match 'DISABLED') { 'DISABLED' } else { 'ACTIVE' }
  Write-Output "$($mm.Groups[2].Value) ($($mm.Groups[1].Value)): $status"
}
```

注意 mf（InductionCurrents）的 physics 段落沒有 `DISABLED` flag 結構，需以「無 DISABLED 即 ACTIVE」判讀。

## 比較兩模型（Comparison Workflow）

當使用者要求「比較兩個 .mph」（例如版本 A vs 版本 B 的幾何/物理/材料變更）時：

1. **依序用 Step 1 讀取兩檔**（若其中一檔被 COMSOL 鎖定，先複製），各自匯出 `dmodel.xml`。
2. **存到不同暫存檔**（如 `dmodel_a.xml` / `dmodel_b.xml`），方便後續比對。
3. **比較清單**（依重要度）：
   - 版本、license、modelinfo（lastComputationTime／pragmaValue：秒數，可換算為幾小時）
   - 全部 `p:table` 多邊形座標（逐 Polygon 找 `valueMatrix`，抓出 z/x 位移）
   - 全域參數（`<ModelParam tag="param">` 的 expressions 數值）
   - Physics 啟用狀態、線圈設定（N、ICoil）、全域方程（PID 增益）
   - Study（freq、tlist、pLists 數量/末點）
   - Mesh（三角形數、品質、hmax/hmin）
   - Materials（tag/名稱/entities）
4. **相同項目也要列出**，結尾用「總結」表列出「相同點 vs 差異點」。
5. 產出 `<比較-檔A-vs-檔B>.md`（見 Step 5 報告結構），差異點放前、相同點放後。

### Step 4. Parse `smodel.json` for quick lookup

The JSON file provides a structured tree that's easier to parse than XML for:

- Parameter values (with scalarReal/scalarImag)
- Material names and property values
- Study configuration summaries

### Step 5. Generate Markdown Report

Create a detailed markdown file in the project directory with these sections:

1. **基本資訊** — file name, COMSOL version, model title, units, computation history
2. **所需授權模組** — license modules table
3. **模型概述** — one-paragraph summary of what the model simulates
4. **物理場（Physics Interfaces）** — table of all physics with tags, types, descriptions
5. **多物理耦合** — multiphysics coupling features
6. **線圈定義** (if applicable) — coil types, turns, current sources, wire properties
7. **模型參數** — global parameters table with values and descriptions
8. **3D 幾何** — geometry construction sequence, dimensions, operations
9. **材料** — materials table with names and key properties
10. **研究（Studies）** — study types, settings, computation history
11. **網格（Mesh）** — mesh settings summary
12. **數值求解器觀察** — solver configuration notes
13. **模型檔案結構** — internal .mph file listing with sizes
14. **總結** — comprehensive summary

### Step 6. Cleanup

若用了 Step 1b（解壓縮）或 Step 1（匯出 dmodel 至暫存），務必移除暫存檔（多檔 + 5.9 GB 複本會爆磁碟）：

```powershell
$paths = @(
  "<extractDir>",                  # Step 1b 解壓目錄
  "<tmpZip>",                      # Step 1b zip 複本（可達 GB 級）
  "C:\Users\<user>\AppData\Local\Temp\opencode\model_copy.mph",  # 鎖檔複本（可達 GB 級）
  "C:\Users\<user>\AppData\Local\Temp\opencode\dmodel_a.xml",     # 匯出的 dmodel
  "C:\Users\<user>\AppData\Local\Temp\opencode\dmodel_b.xml"
)
foreach ($p in $paths) { if (Test-Path -LiteralPath $p) { Remove-Item -LiteralPath $p -Recurse -Force } }
```

## Key XML Patterns Reference

| What to find | XML pattern |
| --- | --- |
| Physics interface | `<Physics op="..." tag="..." name="...">` |
| Physics enabled? | `<entityFlags T="51">...|DISABLED|...` |
| Coil definition | `<PhysicsFeature op="Coil" tag="coilN">` |
| Coil type | `<param param="CoilType" value="...">` |
| Coil turns | `<param param="N" value="...">` |
| Coil current | `<param param="ICoil" value="...">` |
| Material | `<Material op="Common" tag="matN" name="...">` |
| Study | `<Study tag="stdN" name="...">` |
| Study type | `<StudyFeature op="...">` (CCC/Frequency/Transient/Stationary) |
| Frequency | `<propertyValue name="p:freq" value="...">` |
| Time range | `<propertyValue name="p:tlist" value="...">` |
| Stored time points | `<pLists T="13">0,...,252000</pLists>`（數量=暫態輸出時間點、末值×60=tmax 秒） |
| Geometry features | `<GeomFeature op="..." tag="..." name="...">` |
| Polygon vertices | `<param param="p:table"...>...valueMatrix="..." ...` |
| **Entity 對應 | `<Selection ...>...<explicit entities="[數值]"/>`（逗號分隔、`[n,e]`＝第 n 個特徵的第 e 個實體） |
| Bounding box | `<boundingBox>minX,maxX,minY,maxY,minZ,maxZ</boundingBox>` |
| Entity count | `<numEntities>vertices,edges,faces,domains</numEntities>` |
| Multiphysics coupling | `<MultiphysicsCoupling op="..." tag="..." name="...">` |
| Global equations (PID) | `<Physics op="GlobalEquations">` with `<PhysicsFeature op="GlobalEquations">` |
| Rotating frame | `<PhysicsFeature op="RotatingFrameFD">` |

## 數值抽取（mph / JavaBridge）— 溫度場等暫態解讀取

當需要「數值資料」（如溫度場 CSV、場分布）而非僅結構解析，且已安裝 COMSOL + Python `mph` 套件時，改用 mph direct API 讀取**解結果**：

1. **一律 stand-alone 模式**：mph 預設 `client-server`（`comsolmphserver`) 易掛起。開場先：
   ```python
   mph.option('session', 'stand-alone')
   ```
2. **環境變數**（Windows）：
   - `JAVA_HOME` → COMSOL 內建 JRE，如 `C:\Program Files\COMSOL\COMSOL64\Multiphysics\java\win64\jre`
   - `JAVA_TOOL_OPTIONS=-Xmx8g -Xms1g -Dfile.encoding=UTF-8 -Dsun.jnu.encoding=UTF-8`（大型模型需 ≥8g）
3. **單一授權席位**：`license.dat` 若為「單一 SERIAL」節點鎖，COMSOL GUI 與 mph 不能並存——跑 mph 前須先關閉 ComsolUI。
4. **模型載入有隨機失敗**（`FlException: Failed_to_initialize_physics_interface`）→ 先用空白模型暖身（`client.create('__warm'); client.remove('__warm')`）再加重試迴圈（~5 次、間隔 20 s）。
5. **抽取指定時間步**：暫態 dataset 名稱如 `研究 4//解 1`；**時間單位是秒**（分鐘×60）。不要一次 `mph.evaluate` 全時間序列（OOM），改手動：
   ```python
   (m/'evaluations').create('Eval', {'data': m/'datasets'/<dset_name>, 'expr': ['r','z','T'], 'solnum': [<1-based idx>]})
   arr = np.array(m/'evaluations'/'Eval').getData()   # shape (3,1,npts)
   r,z,T = arr[:,0,:]
   ```
6. 評估網格覆蓋的是該 physics 啟用範圍，加熱區外可能缺點→後處理需留意（`np.isnan` 過濾 + T>閾值遮罩）。
7. 圖表中文：matplotlib 預設無中文字形，註冊 `C:\Windows\Fonts\msjh.ttc`（微軟正黑體）並設 `font.sans-serif`；避免在字串中用 Unicode 減號 `−`（U+2212）以免字形警告。

## 互動圖表與自動化驗證（plotly + playwright）— 2026-09 實測筆記

當從 mph 抽取的 CSV（如 `field_{A|B}_t{...}.csv`，欄 `time,r,z,T`）要轉成交互式 HTML（熱圖儀表板／3D 動畫）時，以下是要點：

### 繪圖流程（系統 Python `py`，具 numpy/scipy/plotly）
- CSV 為散點（r 0–215 mm、z −350–700 mm）→ 用 `scipy.interpolate.griddata(..., method='linear')` 先規格化到規則網格（熱圖用 r 步 1.25 / z 步 2.5；3D 用 r 2.5 / z 5）。
- 網格外 NaN（資料凸包外）在熱圖會渲染成「深色透明」= 看似黑塊，屬正常；可用 `scipy.spatial.cKDTree` 量每個網格點到最近資料點距離，超過 3 mm 就遮罩 NaN，避免外插假資料。
- `np.rint()` 四捨五入再丟給 plotly，可大幅縮小 HTML（T 可差 3~4 倍檔大小）。
- 離線使用務必 `fig.write_html(path, include_plotlyjs='inline')`（CDN 版在瀏覽器擋外部網域或斷網時會「像是沒畫完、白畫面」）。注意：檔案內仍可 grep 到 `cdn.plot.ly` 字串，那是 plotly.js 內建 `topojsonURL` 預設值，與離線渲染無關。

### plotly.js 已知行為（重要，容易誤判為 bug）
- 一個 figure 同時含 `frames` + `slider` 時，`newPlot` **載入後會自動 animate 到最後一個 frame**（slider `active` 變最後一步，畫面＝末時間步）。解法：base 圖直接用「最後一步（穩態）」的資料當初始，讓畫面、slider 標籤、active 三者一致，別再用第 0 步。
- Slider step label 若已含單位（`4200 min`），`currentvalue suffix=' min'` 別再加單位，否則顯示「4200 min min」。建議 label 只留數字。
- `margin` 底部留 ≥120，否則滑桿與末列子圖軸重疊。
- 黑暗模板配 `plotly_dark`；播放/暫停用 `updatemenus` buttons（`method='animate'`：[None,{frame:{duration:500},fromcurrent:true}]）。

### 驗證（headless Playwright/Firefox，webwright venv）
webwright venv **沒有 numpy/plotly**：生成檔用系統 `py`，量測腳本放 webwright venv，像素分析再交回 `py`（PIL），中間用 JSON 檔或 stdout 傳座標。

- 結構量測：`gd._transitionData._frames` 長度（=時間步數）；`g.slider-container`、`g.updatemenu-container`（注意不是 `.updatemenu`）；`page.on('pageerror')` 捕捉 JS 錯誤。
- 功能量測：`await Plotly.animate(gd,[frameName],{mode:'immediate',transition:{duration:0}})` 切到已知步，再讀 `gd._fullData[i].z[0][0]` 對照 CSV 值，確認資料真的有換。
- 畫面驗證（確認「數據真的有畫」而非 NaN 空圖）：runtime `Plotly.addTraces` 塞 marker 到已知物理點 → `getBoundingClientRect()` 取 `.scatterlayer path` 的螢幕座標 → 截圖 → PIL 取像素 RGB → 與已知溫度（如高溫點 2708 K 應為亮黃白、低溫 688 K 為藍紫）比對。
- 為使用者留預覽圖：對 HTML 以瀏覽器 viewport 截 PNG 存到 `analysis\`（如 `dashboard_interactive_preview.png`）。
- 注意：本模型**無法直接「看」截圖**（Read 圖片回傳 error），一律以像素探針量化驗證。

## Comsol 6.4 mph API Gotchas（2026-09 PVT 實測）

以下發現來自 2026-09-18~20 的 PVT SiC 長晶 70 hr 熱場分析專案（4.47 GB .mph 檔）。

### 變數名稱：用 `T` 而非 `ht3.T`
- `model.evaluate(['ht3.T'], ...)` 只回傳 **fluid domain** 的節點（dom 2,4,7,13），固體域（石墨 dom 3/5/14/15、粉體 dom 6、晶種 dom 8）全部 NaN。
- 正確做法：用全域變數 `T`（或 `comp1.T`），它涵蓋所有啟用 physics 的域。
  ```python
  # ✅ 正確
  v = m.evaluate(['T', 'dom', 'r'], dataset='研究 15//解 14', inner='last')
  # ❌ 錯誤（固體域全 NaN）
  v = m.evaluate(['ht3.T', 'dom', 'r'], dataset='研究 15//解 14', inner='last')
  ```

### 時間列表讀取
- `t1.getString('tlist')` → 回傳原始字串（如 `'range(0,0.5,15) range(15,30,150)...'`）
- `t1.getDoubleArray('tlist')` → 回傳展開後的浮點數組（已解析所有 range）
- 两者都要試，getString 用於修改，getDoubleArray 用於分析。
  ```python
  t1 = j.sol().get('sol14').feature().get('t1')
  tlist_str = t1.getString('tlist')        # 原始表達式
  tarr = np.asarray(t1.getDoubleArray('tlist'))  # 展開值 (min)
  ```

### 域選擇（solid1 / fluid1）
- `ht3` physics 有 `solid1` 和 `fluid1` 兩個子 feature，各自有自己的 domain selection：
  ```python
  ht3 = j.physics().get('ht3')
  solid_doms = list(ht3.feature('solid1').selection().entities(2))  # [3,5,6,8,9,...]
  fluid_doms = list(ht3.feature('fluid1').selection().entities(2))  # [2,4,7,13]
  ```
- 用這兩個列表來映射 domain number → 材料類型。

### 客戶端-伺服器模式
- **不要**在每個 script 重新 start server。啟動一次 persistent server：
  ```powershell
  Start-Process -FilePath "C:\Program Files\COMSOL\COMSOL64\Multiphysics\bin\win64\comsolmphserver.exe" `
    -ArgumentList "-np 8 -port 2039 -multi on" -WindowStyle Hidden
  ```
- Python 連接：`c = mph.Client(port=2039, host='localhost')`（不能用 stand-alone + 同一 port 多次連接）
- **單一 Python session 只能有一個 Client**（`Only one client can be instantiated per Python session`）。
  需要多個連接時用不同 port 或同 port 重連（先断开舊的）。
- 模型載入後可多次 evaluate/solve 不需 reload。

### Frame-0 artifact（暫態求解重要已知問題）
- 即使設 `useinitsol=off` + `initstudy=zero`，**frame 0（t=0）仍可能顯示舊解的高溫**而非 Tinit。
- 真正暫態從 frame 1（第一個 time step 後）開始。
- 判斷方法：frame 0 Tmax ≈ 舊穩態值，frame 1 開始下降/上升 → artifact。
- 解法：evaluating 時跳過 frame 0，或從 frame 1+ 開始分析。

### 輻射發射率 API 限制
- COMSOL 6.4 的 `DiffuseSurface` feature **不公開** `emiss` / `emissivity` 屬性給 mph API。
- 所有常見名稱（`emiss`, `emissivity`, `eps`）都回傳 `Unknown_parameter_X`。
- 若需關閉輻射對比測試，須透過 GUI 或直接 patch `dmodel.xml`（將 `<param param="emiss"...>` 的值改為 `0`）。

### Domain average 計算
- 用 `evaluate(['T','dom','r'], inner='last')` 後在 Python 端做域過濾 + 平均。
- 軸對稱體積權重近似：`V_d ∝ r_mean_d × n_d`（各節點乘以其 r 座標再平均）。
- COMSOL `Avge` numerical node 在 client-server 模式下建立會失敗（`不允許此类操作`）。
  改用 Python 端過濾比較可靠。

## comsolbatch Java 續解與帶窗奇異性診斷（2026-09 FCFC 線圈專案實測）

以下發現來自 2026-09-11 的 FCFC 感應線圈暖態暫態續解專案（原始檔 4.3 GB .mph、目標 0→120 min）。是「分析」之外另一種高價任務：**用 Java + comsolbatch 改設定並重跑求解**。

### 框架與冷啟動限制（最重要）
- 編譯：`comsolcompile.exe <Class>.java`（error 詳見 `C:\Users\<user>\.comsol\v64\logs\compile*.log`）；執行：`comsolbatch.exe -inputfile <Class>.class`。
- 標準骨架：`ModelUtil.load("Model", IN_FILE)` → 反射改特徵/屬性 → `model.sol("sol1").runAll()` → `model.save(OUT_FILE)`。
- **無暖啟動（cold-start only）**：comsolbatch 無法由已存解熱啟動續跑（`useinitsol` 也救不了）→ 每個帶內實驗都必須由 t=0 全段重解。實測每次 0→120 min 到達故障帶需 ~10–25 min。
- comsolbatch 每次結束（成功或失敗）都會在 workdir 自動寫 `<Class>_Model.mph`（4.5 GB）+ `.status`——**必須清理**，否則連跑幾次就爆碟。

### 背景執行（opencode bash 工具注意）
- 前台跑長求解會被工具 timeout 殺掉整棵子程序樹 → 一律 `Start-Process -RedirectStandardOutput $log ... -WindowStyle Minimized` 背景跑，再輪詢。
- 輪詢節奏：每 ~110 s 檢查 `Get-Process comsolbatch` 的 CPU／進度 %（log 中的 `���e�{��: NN %` 為亂碼的「進度」）／log tail 有無 `SOLVE FINISHED` 或「相依變數出現複數」。
- 單次 bash 呼叫若同時含長 `Start-Sleep` + 其他命令，可能觸發 `ChildProcess.kill` —— 盡量一次只做一件事。

### Java 反射 API（comp1 / common / physics feature）
- `model.component("comp1")` 回傳 `ModelNodeMEClient`（編譯期無 `feature()`）→ 一律 `getClass().getMethod(...).invoke(...)` 反射呼叫。
- 移動網格：`component("comp1").common()` 回 `ComponentCommonListMEClient`，`tags()` 得特徵清單、`get(tag)` 得 `CommonFeatureMEClient`。
  - FCFC 實例特徵：`free1`（自由位移）、`disp1`（PrescribedMeshDisplacement，值 [0,0,0]）、`pnmv1`（prescribedNormalVelocity，**運動來源 = G_mmh**）、`sym1`、`pnmd1`（[0]）。
  - 方法：`getString` / `getStringArray` / `getStringMatrix` / `hasProperty` / `getAllowedPropertyValues` / `set(String,String)`。
- physics feature 同理（例如 `model.physics("rad").feature("dsurf1")`）。
- **凍結移動網格技巧**：`set("prescribedNormalVelocity","G_mmh*(t<=4800[s])")`，再用 `getString` 回讀確認生效（pnmv1 在 comp1.common 之下，不在 physics 下）。
- 注意：停用的 obsolete feature（如 rad 的 `os1` OpaqueSurface，`entityFlags` 含 `DISABLED`）**不能設屬性**（拋「無法設定屬性」）。

### RadiationSettings / Time solver 屬性名實測
- `prop("RadiationSettings")` **可寫** 的屬性：
  - `viewFactorUpdateThreshold`：`everyIteration` / `everyNTime`
  - `viewFactorsUpdateTime`：**必須帶單位**（`"600[s]"`；純數字 `"600"` 會拋錯）
  - `storeViewFactors`：`"0"` / `"1"`
  - `failonbackside`：只能 `"0"` / `"1"`（**禁用 `"off"`**，會拋錯）
- 下列名稱全部 N/A（`InvocationTargetException`，勿再試）：`radiationIterations`、`maxRadIterations`、`viewFactorAlgorithm`、`maxComputationalTime`、`dependDiffuseSurfaceOn`、`constraintMethod`、`maxAllowedIterations`、`discretizationType`。
- Time solver `t1`（`<SolverFeature op="Time" tag="t1">`）可寫屬性（dmodel.xml 中 `name="p:xxx"`）：`rtol`（FCFC=0.005）、`atolglobalfactor`、`maxorder`（=2）、`complex`（允許複數 on/off）、`estrat`（誤差估測）、`tlist`（一次給足全程 `range(0,0.1,80) range(80,1,120)`）。
- 讀 dmodel.xml 找屬性：propertyValue 前一行常是中文 `<!-- 註解 -->`，屬性名即 `name="p:xxx"`。

### 帶窗放射度奇異性（本專案最終根因，屬「結構性、無法以數值繞過」）
- 現象：兩波段 S2S（波段 `[0\, 2.5[um]` 與 `[2.5[um]\, +∞[`）放射度變數 `Ju_band` / `Jd_band` 在暖態 ~85–96 min 成複數。
- 失敗邊界隨 run 漂移（非固定幾何背面）：`5185.9@16`、`5262.77@16`、`5496.6@24-25,29-31,68`、`5706.3@8,10,32,34,36`。
- **已逐一排除**的數值手段：步距（0.02–1 min）、容差 rtol、視因子更新 everyIteration vs everyNTime、failonbackside 0/1、網格凍結（t≤4800s）、`complex` on/off、ε 帶窗（急降 1e-4 與平滑斜坡 `flc2hs(t-5040[s],300/40)` 全在窗入口或 ε 開始變 1% 即翻複數）。
- 成因分析：暖態高溫使放射度耦合矩陣 `(1-ε)F` 譜半徑逼近 1 → 系統跨越奇異點 → 無實數解。**任何 ε→0 的旁路只會讓矩陣更近奇異**（ε=0 時行和=1 恰奇異），故旁路不可行。
- 冷啟動（293 K）未碰到奇異點，故 0–80 min 可解且可靠；原始模型自己的 `range(0,0.1,120)` 一樣過不了帶（原檔本就無暖態全段解）。
- 唯一出路：在 COMSOL GUI 改物理設定（例：改單頻帶灰體、檢修 DiffuseSurface from_mat 發射率、調整 SpectralBand 結構）後再重跑——**數值/求解器設定無法解決**。

### 收尾實務
- CSV 驗證格式：`t[s],t[min],Tprobe[K],avgTfield[K],minTfield[K],maxTfield[K]`（801 步）；FCFC 參考值 `avh1@4800 s ≈ 2571 K`。
- PowerShell 注意：`\uXXXX` 轉義**不被 PowerShell 解讀**，含中文之路徑請用萬用字元（如 `D:\10-*\Comsol\`）或以 `[char]0x..` 組字。

## Environment gotchas

- **`.mph` is a ZIP file** — must rename to `.zip` or use `Copy-Item` + `Expand-Archive` (PowerShell won't expand files with `.mph` extension directly).
- **`.mph` 檔常 >1 GB、含數百個 `solutionblock*.mphbin`** — 不要整包解壓縮（會超過 120 s timeout）。用 `ZipFile.OpenRead()` 直接抽文字 entry（見 Step 1）。
- **COMSOL 會鎖定正開啟的 .mph**（同目錄有 `.lock`）— `ZipFile.OpenRead` 讀不到時，用 `FileShare.ReadWrite` 複製一份再讀；分析完務必刪除這份 GB 級複本。
- **`dmodel.xml` can be very large** (5–60 MB) — read in chunks using `offset`/`limit` parameters；或將內容寫到暫存檔再給 Read/Grep 工具（CLI 一次輸出太多會截斷）。
- **XML contains Chinese characters** encoded as `&#xHEX;` — Windows 可用 `[System.Web.HttpUtility]::HtmlDecode()` 解碼；**若載入該型別失敗**，改用 `[System.Net.WebUtility]::HtmlDecode()`（.NET 內建，無須 Add-Type）。
- **Grep/Glob 工具是「目錄級」搜尋** — 單一 `Select-String -Path` 指定目標檔，才不會一次搜到同目錄所有相同檔名（如同時抓到 dmodel_a 與 dmodel_b）。
- **註解跳出**：`</GeomFeature>` 會在 `<PhysicsFeatureList>` 中以 `</GeomFeature>` 結尾重複出現，用非貪婪 `[\s\S]*?</GeomFeature>` 會停太早。改以 `<GeomFeature` 開頭切段（split）再比對 tag，較穩健。
- **Binary `.mphbin` files** cannot be read as text — skip them, they contain geometry/solution/mesh binary data.
- **專案目錄 vs 預設工作目錄**：若專案檔很大，所有暫存一律放 temp 目錄，最後只在專案目錄留 md 報告，避免專案資料夾被塞爆。

## Deliverables checklist

- `<model_name>-模型詳細說明.md` in the project directory
- Temp files cleaned up
