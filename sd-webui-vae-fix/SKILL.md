---
name: sd-webui-vae-fix
description: 修復 AUTOMATIC1111 Stable Diffusion WebUI（A1111 / sd.webui）「無法切換」檢查點或 VAE 的錯誤（sd_model_checkpoint / sd_vae 選擇失敗）。覆蓋兩種根因：(1) VAE 檔是 diffusers 格式；(2) 完整檢查點（6~7GB，例如 sd_xl_base_1.0_0.9vae.safetensors）誤放 models\VAE 被當成 VAE 選取，log 出現 Missing/Unexpected key(s) 或 AutoencoderKLInferenceWrapper。診斷 VAE 檔格式、從完整檢查點抽取正確 VAE 並移動檢查點、用 run.bat 正確重啟（CWD/環境變數陷阱）、以 /sdapi 或免 --api 的 in-process 方式驗證。Use when asked to 修復 無法切換 / checkpoint 切換失敗 / VAE 切換失敗 / VAE format / Missing key(s) / Unexpected key(s) / AutoencoderKL / sd_vae / sd_model_checkpoint / AutoencoderKLInferenceWrapper。
---

# sd-webui-vae-fix — A1111 檢查點／VAE 切換失敗修復

修 AUTOMATIC1111 Stable Diffusion WebUI（下方稱 A1111）中「切換檢查點或 VAE 失敗」的問題。

## 觸發情境（何時使用此 skill）

- 網頁頂部出現 toast「無法切換 <名稱>」或英文同義訊息。
- VAE 下拉選了某 VAE，或 `sd_model_checkpoint` 切不過去。
- **VAE 下拉出現一顆「看起來像檢查點」的項目**（例如 `sd_xl_base_1.0_0.9vae.safetensors`，檔名像 VAE 但其實 6~7GB）。
- WebUI log / console 出現類似：

```
changing setting sd_vae to xxx.safetensors: RuntimeError
Error(s) in loading state_dict for AutoencoderKL:
	Missing key(s) in state_dict: ...
	Unexpected key(s) in state_dict: ...
```

```
Error(s) in loading state_dict for AutoencoderKLInferenceWrapper:
```

（後者幾乎都是「完整檢查點被誤當 VAE 載入」，見根因 2。）

## 根因（兩種，依序檢查）

### 根因 1：VAE 檔是 diffusers 格式

A1111 的 VAE 載入（`modules/sd_vae.py` 的 `_load_vae_dict` → `load_state_dict(strict=True)`）**只接受 LDM 格式的鍵**，也就是完整檢查點內 `first_stage_model.*` 拆出來的鍵：

```
decoder.conv_in.weight
decoder.mid.attn_1.k.weight
encoder.down.0.block.0...
encoder.up.3...
quant_conv.weight / post_quant_conv.weight
```

而從 HuggingFace 直接下載的 `vae/diffusion_pytorch_model.safetensors` 是 **diffusers 格式**：

```
encoder.down_blocks.0...
decoder.mid_block.attentions...
to_q / to_k / to_v
encoder.conv_norm_out...
```

diffusers 格式放進 `models\VAE\` 後會造成**兩種**「無法切換」：

1. `sd_vae = Automatic`（就近自動選 VAE）時，靠近檢查點的資料夾會自動挑到這顆 VAE → 載入失敗 → **「無法切換 <檢查點名>」**。
2. 手動在 VAE 下拉選它 → 載入失敗 → **「無法切換 <VAE名>」**。

### 根因 2：完整檢查點誤放 `models\VAE`（本次實例）

`sd_xl_base_1.0_0.9vae.safetensors` 這種檔名會令人以為是 VAE，但它其實是**完整 SDXL 檢查點**（6.9GB，metadata `ss_base_model_version=stable-diffusion-xl-v1-base`，頂層鍵含 `conditioner.*` / `model.*` / `first_stage_model.*`）。它會被列進 VAE 下拉（掃 `models\VAE` 下所有 `.safetensors/.ckpt/.pt/.vae.pt`），但選取時 `load_state_dict(strict=True)` 對不上 VAE 結構 → **`AutoencoderKLInferenceWrapper`** RuntimeError。

**快速分辨**：

| 特徵 | 完整檢查點（錯誤放到 VAE 資料夾） | 真正可用的 VAE |
|---|---|---|
| 檔案大小 | 6~7 GB | ~160 MB（fp16）／~320 MB（fp32） |
| 頂層鍵 | `model.` / `cond_stage_model.` / `conditioner.` / `first_stage_model.` | `decoder.` / `encoder.` / `quant_conv.` / `post_quant_conv.` |
| metadata | 有 `ss_*`（如 `ss_base_model_version`） | 通常無 |

## 診斷步驟

1. 健康檢查：`http://127.0.0.1:7860/internal/ping` 應回 200。**注意主機可能沒掛 `--api`**（`webui.py` 中 `launch_api = cmd_opts.api`），沒掛時 `/sdapi/v1/*` 一律回 `{"detail":"Not Found"}`——別誤判成服務壞掉，改用 `internal/ping` 或下述 in-process 驗證。
2. 在 log 中找 `RuntimeError` + `changing setting` + 錯誤的類別名稱（`AutoencoderKL` = 格式錯；`AutoencoderKLInferenceWrapper` = 幾乎必然是完整檢查點誤放）。
3. 用 `scripts/check_vae_format.py` 判別 `models\VAE\<名字>.safetensors` 是 LDM、diffusers 還是完整檢查點（指令見下方）。
4. 輔助：`safe_open(..., framework="pt")` 讀 `f.metadata()` 看 `ss_base_model_version`；並比較檔案大小（160MB vs 6.9GB）一秒分辨。

## 修復流程

### 1. 檢查現有 VAE 檔案格式

```bash
# 需要 webui 的 python（內含 torch + safetensors），例：
PY=.../sd.webui/system/python/python.exe
"$PY" scripts/check_vae_format.py "MODELS\VAE\sd_xl_base_1.0_0.9vae.safetensors"
```

輸出會說明鍵的形式，並提示是 diffusers 格式或完整檢查點（不合 A1111 當 VAE 用）。

### 2. 抽取正確 VAE + 移動檢查點

正確的 0.9 / 其它 VAE 通常「烤進」完整檢查點。**若該檢查點被誤放在 `models\VAE\`，先把它移到 `models\Stable-diffusion\`**（它本來就是檢查點），再抽取獨立 VAE：

```bash
# a) 移動誤放的位置：VAE 資料夾 → 檢查點資料夾
move "models\VAE\sd_xl_base_1.0_0.9vae.safetensors" "models\Stable-diffusion\"

# b) 抽出 first_stage_model.* 存成獨立 VAE（A1111 可載入）
"$PY" scripts/extract_vae.py `
  "models\Stable-diffusion\sd_xl_base_1.0_0.9vae.safetensors" `
  "models\VAE\sd_xl_vae.safetensors"
```

成功會輸出 `wrote <N> tensors -> <PATH> (<bytes>)`（本次實例：248 tensors → 159.6 MiB，keys：decoder 138 / encoder 106 / quant_conv 2 / post_quant_conv 2）。

> 若該 VAE 沒有烤進任何本機檢查點，可從官方 HF 倉庫下載 **SDXL 1.0 VAE**：`https://huggingface.co/stabilityai/sdxl-vae/resolve/main/sdxl_vae.safetensors`（319MB fp32）。注意 0.9 VAE 沒有官方單獨下載，只能從 `sd_xl_base_1.0_0.9vae.safetensors` 抽取；1.0 與 0.9 兩個 VAE 不同。

### 3. 正確重啟 WebUI（本節最容易踩雷）

先確認沒有殘留的 `python launch.py` 實例（多實例會搶 7860 與 GPU）。重啟本身有幾個 Windows 特定的陷阱：

- **啟動檔會用相對路徑**（本實例 `run.bat`：`call environment.bat` → `cd %~dp0webui` → `call webui-user.bat`），**必須以「webui 根目錄」為 CWD 執行**（如 `D:\SD\sd.webui`）。CWD 錯時會先得到 `'environment.bat' 不是內部或外部命令...`，隨後 `exit code: 9009`。
- `environment.bat` 的作用是把 `system\python` / `system\git\bin` 加進 PATH；它失敗 = `%PYTHON%`（預設 `python`）找不到 = `Couldn't launch python` + 9009。
- PowerShell `Start-Process` 派生時務必傳 **`-WorkingDirectory '<webui root>'`**（光靠 bash workdir 不一定生效，傳了才穩）。
- **最陰險：前一次殘留的 `cmd /c call run.bat > log 2>&1` 若還掛著（例如卡在 `pause`），它會鎖住 log 檔**──新實例寫不進去同一個檔，你讀到的是舊內容，會誤判「重啟失敗」。判別法：log 的 `LastWriteTime` 凍結、`Get-FileHash` 報「另一個處理序正在使用檔案」。解法：先 `Stop-Process` 掉掛起的 cmd/python（或找 7860 的 OwningProcess），重啟時**改用全新的 log 檔名**（如 `webui-restart.log`）。
- 驗證啟動：poll `http://127.0.0.1:7860/internal/ping` → 200，且 log 出現 `Running on local URL: http://127.0.0.1:7860`。

### 4. 驗證（有 `--api` 用 a/b/c；沒有就改用「免 --api」法）

```bash
# a) VAE 下拉直接選剛修好的 VAE
POST /sdapi/v1/options  {"sd_vae":"sd_xl_vae.safetensors"}
# b) Automatic + 切檢查點（驗證就近搜尋）
POST /sdapi/v1/options  {"sd_vae":"Automatic"}
POST /sdapi/v1/options  {"sd_model_checkpoint":"sd_xl_base_1.0.safetensors"}
# c) 切到該檢查點
POST /sdapi/v1/options  {"sd_model_checkpoint":"sd_xl_base_1.0_0.9vae.safetensors"}
```

每次改動後 `GET /sdapi/v1/options` 確認 `sd_model_checkpoint` / `sd_vae` 已變更，且 log 沒有新的 `RuntimeError`。

**免 `--api` 的 in-process 驗證**（伺服器沒掛 API 時用這個）：

```python
# set env: GIT_PYTHON_GIT_EXECUTABLE=<system\git\bin\git.exe>（A1111 需要 git）
# sys.path.insert(0, '<webui root>')，再用 modules 模擬 UI 選取 VAE：
import modules.sd_vae as sd_vae
...
# 用與 modules/sd_vae.py 相同的載入路徑 load 指定的 VAE 檔，
# 成功會印出 "VAE weights loaded."；再讀取最新 state dict 逐 key 比對。
```

本實例以這條路徑做出結果證明：新抽取的 `sd_xl_vae.safetensors`（159.6MB）可成功載入 SDXL，`loaded_vae_file` 指向該檔且權重與檢查點內建 VAE 一致。

### 5. 出圖煙霧測試

```bash
POST /sdapi/v1/txt2img  {"prompt":"a red apple","steps":1,"width":128,"height":128,"cfg_scale":1,"batch_size":1}
```

有回圖就代表檢查點 + VAE 整條管線正常。

## 注意事項

- **`A tensor with all NaNs was produced in VAE.`** 是 fp16 VAE 的正常現象，A1111 會自動轉 fp32 重試，不必視為錯誤。
- `AutoencoderKLInferenceWrapper` 錯誤類別幾乎只會出現在「完整檢查點被當 VAE 載入」時；`AutoencoderKL` 才是「VAE 檔案格式錯」。
- A1111 在 `sd_vae = Automatic` 且重啟後，會把解析到的實際檔名寫回 `config.json`，這代表就近偵測成功，不是問題。
- 就近 VAE（`Automatic`）的比對規則是「檢查點 basename 前綴」；想自動套用的 VAE 檔名開頭要跟檢查點一致。
- `Anything-V3.0-X-VAE.pt` 這類是 SD1.x 專用 VAE，用在 SDXL 會色偏要提醒使用者；不要擅自刪使用者檔案。
- 判斷好壞：真正的 LDM VAE 約 **160MB（fp16）**；一顆「VAE」有 6.9GB→就是完整檢查點誤放，345MB 以上卻又是 diffusers 鍵→被錯誤檔案覆蓋。
- 若 log 找不到對應來源，`「無法切換」` toast 是執行期產生的字串，原始碼中搜不到，別花時間追；直接看底下的 RuntimeError。
- 在 Windows 上重啟失敗時，先看 log 時間戳是否凍結（殘留實例鎖檔），再懷疑啟動檔 CWD / PATH。

## 附檔

- `scripts/check_vae_format.py` — 印出 safetensors 鍵前綴統計並判別格式（LDM / diffusers / 完整檢查點）。
- `scripts/extract_vae.py` — 從完整檢查點抽取 `first_stage_model.*` 存成獨立 VAE。