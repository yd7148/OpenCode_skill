---
name: sd-webui-vae-fix
description: 修復 AUTOMATIC1111 Stable Diffusion WebUI（A1111 / sd.webui）「無法切換」檢查點或 VAE 的錯誤（跨到 sd_model_checkpoint / sd_vae 選擇失敗）。診斷 VAE 檔是 diffusers 格式還是 LDM first_stage_model.* 格式、從完整檢查點抽取正確 VAE 覆寫 models\VAE、重啟並用 /sdapi/v1/options 與 log traceback 驗證。Use when asked to 修復 無法切換 / checkpoint 切換失敗 / VAE 切換失敗 / VAE format / Missing key(s)/Unexpected key(s) / sd_vae / sd_model_checkpoint。
---

# sd-webui-vae-fix — A1111 檢查點／VAE 切換失敗修復

修 AUTOMATIC1111 Stable Diffusion WebUI（下方稱 A1111）中「切換檢查點或 VAE 失敗」的問題。

## 觸發情境（何時使用此 skill）

- 網頁頂部出現 toast「無法切換 <名稱>」或英文同義訊息。
- VAE 下拉選了某 VAE，或 `sd_model_checkpoint` 切不過去。
- WebUI log / console 出現類似：

```
changing setting sd_vae to xxx.safetensors: RuntimeError
Error(s) in loading state_dict for AutoencoderKL:
	Missing key(s) in state_dict: ...
	Unexpected key(s) in state_dict: ...
```

## 根因（幾乎都是這個）

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

## 診斷步驟

1. 連續啟動：`http://127.0.0.1:7860/internal/ping` 應回 200；若有 `--api` 可用 `/sdapi/v1/options`。
2. 在 log 中找 `RuntimeError` + `changing setting`，確認失敗發生在 VAE 載入（不是 GPU 記憶體不足）。
3. 用 `scripts/check_vae_format.py` 判別 `models\VAE\<名字>.safetensors` 是 LDM 還是 diffusers 格式（指令見下方）。

## 修復流程

### 1. 檢查現有 VAE 檔案格式

```bash
# 需要 webui 的 python（內含 torch + safetensors），例：
PY=.../sd.webui/system/python/python.exe
"$PY" scripts/check_vae_format.py "MODELS\VAE\sd_xl_base_1.0_0.9vae.safetensors"
```

輸出會說明鍵的形式；如果出現 `down_blocks / mid_block / to_q` 就是 diffusers 格式，不合 A1111。

### 2. 從完整檢查點抽取正確 VAE

正確的 0.9 / 其它 VAE 通常都「烤進」完整檢查點（檔案較大那顆，例如 6.6GB 的 `sd_xl_base_1.0_0.9vae.safetensors`）。直接抽出 `first_stage_model.*` 再存成獨立 VAE：

```bash
"$PY" scripts/extract_vae.py `
  "MODELS\Stable-diffusion\sd_xl_base_1.0_0.9vae.safetensors" `
  "MODELS\VAE\sd_xl_base_1.0_0.9vae.safetensors"
```

成功會輸出 `wrote <N> tensors -> <PATH> (<bytes>)`。

> 若該 VAE 沒有「烤進」任何本機檢查點，可從官方 HF 倉庫下載 **sd_dynamic_theme 以外的 A1111 版本**，或把官方檔轉格式（diffusers → LDM 需要 rename key 後再存）。

### 3. 覆寫後重新啟動

- 先確認沒有殘留的 `python launch.py` 實例（多實例會搶 7860 與 GPU）。
- 用原本的啟動檔（含 `--api` 較好驗證）。
- 啟動時先刪/備份舊 log，方便對照新 log。

### 4. API 驗證（3 個方向）

```bash
# a) VAE 下拉直接選剛修好的 VAE
POST /sdapi/v1/options  {"sd_vae":"sd_xl_base_1.0_0.9vae.safetensors"}
# b) Automatic + 切檢查點（驗證就近搜尋）
POST /sdapi/v1/options  {"sd_vae":"Automatic"}
POST /sdapi/v1/options  {"sd_model_checkpoint":"sd_xl_base_1.0.safetensors"}
# c) 切到「烤 VAE」的那顆檢查點
POST /sdapi/v1/options  {"sd_model_checkpoint":"sd_xl_base_1.0_0.9vae.safetensors"}
```

每次改動後 `GET /sdapi/v1/options` 確認 `sd_model_checkpoint` / `sd_vae` 已變更，且 log 沒有新的 `RuntimeError`。

### 5. 出圖煙霧測試

```bash
POST /sdapi/v1/txt2img  {"prompt":"a red apple","steps":1,"width":128,"height":128,"cfg_scale":1,"batch_size":1}
```

有回圖就代表檢查點 + VAE 整條管線正常。

## 注意事項

- **`A tensor with all NaNs was produced in VAE.`** 是 fp16 VAE 的正常現象，A1111 會自動轉 fp32 重試，不必視為錯誤。
- A1111 在 `sd_vae = Automatic` 且重啟後，會把解析到的實際檔名寫回 `config.json`（例如 `sd_xl_base_1.0_0.9vae.safetensors`），這代表就近偵測成功，不是問題。
- 就近 VAE（`Automatic`）的比對規則是「檢查點 basename 前綴」；想自動套用的 VAE 檔名開頭要跟檢查點一致。
- `Anything-V3.0-X-VAE.pt` 這類是 SD1.x 專用 VAE，用在 SDXL 會色偏要提醒使用者；不要擅自刪使用者檔案。
- 判斷好壞：修好的 `sd_xl_base_1.0_0.9vae.safetensors` 約 160MB（fp16 LDM）；若是 320MB 且又是 diffusers 鍵，代表又被錯誤檔案覆蓋。
- 若 log 找不到對應來源，`「無法切換」` toast 是執行期產生的字串，原始碼中搜不到，別花時間追；直接看底下的 RuntimeError。

## 附檔

- `scripts/check_vae_format.py` — 印出 safetensors 鍵前綴統計並判別格式。
- `scripts/extract_vae.py` — 從完整檢查點抽取 `first_stage_model.*` 存成獨立 VAE。