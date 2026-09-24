---
name: comsol-gpu-env
description: COMSOL Multiphysics 6.4 的 GPU/系統 CUDA 環境設定與驗證（RTX 5080 Blackwell）。涵蓋切換到系統 CUDA 12.9.1 的版本限制（官方僅支援至 CUDA 12、cuDSS 0.7.1 只能用 bundled）、comsol.prefs 關鍵參數、以 opencode Computer Use 操作 COMSOL「偏好設定→計算中→GPU 加速」GUI 的 a11y 心得（tree item 用 app_post、對話框按 Return、element index 重開即重置、checkbox 狀態不可見）、nvidia-smi/deviceQuery129/bandwidthTest/rtcheck 無 GUI 驗證法與產生 Phase15 報告，以及顯示/視窗維修（不要加 AppCompat DPI/GPU flags、視窗最小化導致「看不見」的判斷與 SW_RESTORE、開模型空白 RendererEventHandlingThread 例外）、徹底解除安裝與 E 槽重裝建議。Use when asked to "切換 COMSOL CUDA", "COMSOL GPU 加速", "驗證 CUDA 安裝", "cuDSS", "RTX 5080", "COMSOL 計算中 GPU 設定", "COMSOL 看不見", "COMSOL 視窗最小化", "COMSOL DPI", "解除安裝 COMSOL", "重裝 COMSOL", or to setup/verify COMSOL GPU acceleration environment.
license: MIT
compatibility: opencode
metadata:
  audience: opencode agents
  workflow: comsol-gpu-env-setup
  languages: zh-TW
---

# comsol-gpu-env — COMSOL 6.4 GPU / 系統 CUDA 環境設定與驗證

本 skill 文件化如何在本機為 COMSOL Multiphysics 6.4 設定併用 **系統 CUDA** 的 GPU 加速環境，
涵蓋：版本相容性限制、`comsol.prefs` 關鍵參數、以 opencode 的 Computer Use（a11y）操作
「偏好設定 → 計算中 → GPU 加速」GUI 的心得、以及無 GUI 的環境驗證與產出報告。

Do **not** use this skill to build models via MCP（`comsol-mcp`）或分析 `.mph` 檔（`comsol-analyzer`）。

## 目標環境（本機已驗證）

| 項目 | 值 |
|------|-----|
| COMSOL | 6.4（原 `C:\Program Files\COMSOL\COMSOL64\Multiphysics`；**2026-09-24 已於 C 槽徹底移除**，重裝建議 `E:\COMSOL\COMSOL64\Multiphysics`，Update 1） |
| 顯示卡 | NVIDIA GeForce RTX 5080，16303 MiB，Compute Capability **12.0**（sm_120） |
| 驅動程式 | 610.88（**勿更動**） |
| 系統 CUDA | **12.9.1**（nvcc 12.9 / V12.9.86，`C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.9`）；另有 v12.8 並排安裝（`CUDA_PATH_V12_8`） |
| cuDSS | 僅能用 COMSOL bundled 0.7.1（`ext\cudss\win64\cudss64_0.dll`），**不可**切系統 cuDSS |
| 設定檔 | `C:\Users\4pins\.comsol\v64\comsol.prefs` |
| 相關 skill | `comsol-mcp`（MCP 建模）、`comsol-analyzer`（.mph 分析） |

## 版本兼容性（官方限制，務必遵守）

- COMSOL 6.4 **支援到 CUDA 12**：可選 12.4.x/12.5.x/12.6.x/12.8.x/12.9.x，但 **不可用 CUDA 13.x**（超出官方上限）。
- 官方資料標示搭配 **CUDA 12.9.1** 需 **minimal driver 576.57**；本機 610.88 已滿足。
- 為何要系統 CUDA：COMSOL bundled CUDA 12.4.x 不帶 Blackwell `sm_120` 的原生支援，RTX 5080（CC 12.0）只能跑到 **compute capability error（0）**；CC 12.0 需 CUDA ≥ 12.8 才原生支援 → 切到系統 **12.9**。
- cuDSS：COMSOL 目前**只支援附帶版本 0.7.1**，系統 cuDSS root 應留空。
- **永不覆蓋** COMSOL bundled lib（`ext\cuda\win64\cudart64_12.dll` 等）——切換只改 `comsol.prefs` 的 root 指向，不動 bundled 檔。

## comsol.prefs 關鍵參數（目標終態）

| 鍵 | 值 | 意義 |
|----|----|------|
| `gpu.settings.usecudaroot` | `on` | 使用系統 CUDA 工具包 |
| `gpu.settings.cudaroot` | `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.9` | 系統 CUDA root |
| `gpu.settings.usecudssroot` | `off` | 不使用系統 cuDSS（維持 bundled 0.7.1） |
| `gpu.settings.cudssroot` | `（空）` | 系統 cuDSS 路徑留空 |
| `gpu.settings.traindnnongpu` | `off` | 深度神經網路訓練回退至 GPU 以內的值（維持 off） |

驗證方式：以 `Select-String`/Read 比對 `comsol.prefs` 中的 `gpu.settings.*` 是否如上。

## Computer Use（a11y）操作 GUI 的心得

在「**檔案 → 偏好設定 → 計算中 → GPU 加速**」頁進行的自動化經驗：

1. **元素 index 每次重開視窗就重置** → 每次操作前先 `get_app_state` 取最新 a11y 樹，勿沿用上次 index。
2. **偏好設定樹狀區**在 a11y 是 tree item：`click`（accessibility）對 tree item / text 常失敗（fallback 也失敗）→ 改用 **`perform_secondary_action` 的 `click_method: "app_post"`**（例如 `open-computer-use_click` 帶 `click_method: "app_post"` + 目標 **element_index**）即可選取而載入右側設定頁。
3. **對話框（如「驗證 CUDA 安裝」結果、About 等）的 OK 鈕**：accessibility click 與 app_post click 都可能失敗、元素樹也未提供 → **按 `Return` 鍵一次**關閉；按 Return 通常會連帶把偏好設定視窗一起關掉，屬正常。
4. **a11y dump 不會顯示 checkbox 的勾選狀態** → 用 `comsol.prefs` 或頁面「狀態」文字交叉驗證，勿以樹中狀態為準。
5. 成功訊號：「驗證 CUDA 安裝」按下後，樹/視窗出現對話框文案 **「已找到一個相容的 CUDA 安裝」** = 成功；按 Return 關閉。
6. 選完 CUDA 工具包 root 後，部分畫面需重新操作「驗證 CUDA 安裝」讀取新值。

## 無 GUI 驗證（CUDA runtime 層級）

自行編譯的 CUDA 12.9 sample 執行檔（例：`C:\Users\4pins\AppData\Local\Temp\opencode\`）：
- `nvidia-smi`：確認 driver / VRAM（610.88 / 16303 MiB）。
- `deviceQuery129.exe`：輸出 `Detected 1 CUDA Capable device(s)`，RTX 5080，Compute Capability = **12.0**。
- `bandwidthTest.exe`：`Device to Device` 傳輸 **PASS**。
- `rtcheck.exe`（runtimeCheck）：**PASS**，`cudaRuntimeGetVersion = 12.9`、`cudaDriverGetVersion = 13.3`（driver 內含 runtime 13.3 正常，COMSOL 仍以 12.9 執行）。

結合上述輸出與 `comsol.prefs` 比對 → 產出「Phase 15」式環境報告（Summary / Field Values 表 / Verification Evidence / Final Status）。

## 產出

- `<專案根>\PhaseNN_COMSOL_6.4_GPU_Environment_Report.md` 環境報告（繁中，含版本對照、prefs 鍵值表、驗證證據、Final Status）。
- 本機 GPU 環境終態：usecudaroot=on（v12.9）、usecudssroot=off、traindnnongpu=off。

## 注意

- 切換後 **重啟 COMSOL** 再驗證，prefs 才生效；重開後偏好設定的「GPU 加速」頁應顯示使用系統 CUDA 工具包 on + CUDA 目錄 v12.9。
- 若使用者要求維持並排 v12.8：系統已同時安裝 v12.8（`CUDA_PATH_V12_8`），`cudaroot` 指向哪個版本由 prefs 決定，不要改 PATH 全域。
- RTX 5080 為 Blackwell（CC 12.0）：CUDA < 12.8 一律不原生支援，報錯即以 bundled 12.4 出現 compute capability error。

## 顯示／視窗／解除安裝與重裝（2026-09-24 維修實錄）

硬體分工：**GPU0 = RTX 5080（僅運算，無影像輸出）**；**GPU1 = Intel 內顯（HDMI 輸出，驅動
32.0.101.8331，OpenGL 4.6）**。系統縮放 175%。

### 看到的症狀與根因

1. **比例錯亂／版面溢出**：原有 AppCompat 旗標 `HIGHDPIAWARE DISABLE_GPU_ACCELERATION`
   破壞 COMSOL（WPF）在縮放環境的 DPI 處理 → 樹節點寬度 > 容器、視窗縮小。
2. **「打開了卻看不到」＝主視窗以最小化啟動**：AWT/WPF 主視窗 rect 停於
   （−32000,−32000）+ `IsIconic=True`，非黑窗也非 crash。判斷法：列舉頂層視窗
   （`GetWindowRect`/`IsIconic`）或畫素取樣。處置：`ShowWindow(h,9)`（SW_RESTORE）+`ShowWindow(h,3)`（SW_MAXIMIZE）。
   已存成 `E:\01-Project\2026-09-Comsol-Coil\Fix-ComsolWindow.ps1`（可加 `-Launch` 併啟動）。
3. **開 .mph 後整窗空白**：`comsolnet*.log`/`comsolnet*_render.log` 出現
   `Caught Unknown Exception in RendererEventHandlingThread`（renderingthread.cpp:209）+
   WPF 端 `Create DisconnectGraphicsCommand`。以 `comsol.exe -open <file>` 重測**未複現**
   （模型約 10 秒載完、無新例外）。OpenGL context 正常建立在 Intel（log 中 `Vendor: Intel`）。

### 注意事項（避免重蹈覆轍）

- **不要**對 `comsol.exe`/`ComsolUI.exe` 加任何 AppCompat Layers（`HIGHDPIAWARE`/`DPIUNAWARE`/
  `DISABLE_GPU_ACCELERATION`）——是本次顯示問題的根因。
- 若要保持 RTX 純運算，改在
  `HKCU\Software\Microsoft\DirectX\UserGpuPreferences` 設（等同「圖形→省電」）：
  `comsol.exe`/`ComsolUI.exe` = `VideoProcessing=1;Renderer=D3D11;PowerPreference=Integrated`，
  `comsolxpl.exe` = `GpuPreference=1;`。此設定**只影響顯示，不影響 CUDA 求解**（solver 走
  `comsolmphserver`，AppCompat/DirectX 層夠不到）。

### 徹底解除安裝（官方路徑，乾淨不用重裝）

- 關閉所有 COMSOL 程序後執行：
  `"<安裝目錄>\bin\win64\setup.exe" -u true "<安裝目錄>"`（Java 版會開「移除界面」視窗，等待即完成）。
- 收尾清除：`C:\Program Files\COMSOL`、`C:\Users\<user>\.comsol`（.comsol\v64 含 prefs/log）、
  `%LOCALAPPDATA%\COMSOL`、Start Menu 捷徑、Uninstall 登錄項目、AppCompat Layers、
  UserGpuPreferences、`.mph` 關聯（官方 uninstaller 會一併處理大部分）。PATH 通常無項目。