# sd-webui-vae-fix

一個 OpenCode skill，用來修復 **AUTOMATIC1111 Stable Diffusion WebUI**（A1111 / sd.webui）中「無法切換檢查點或 VAE」的問題。

適用情境與更多細節見 [`SKILL.md`](SKILL.md)。

---

## 症狀

- 網頁頂部跳出 toast：**「無法切換 <名稱>」**
- VAE 下拉選擇某 VAE 沒反應
- `sd_model_checkpoint`（檢查點）切不過去
- WebUI console / log 出現 RuntimeError：

```
changing setting sd_vae to xxx.safetensors: RuntimeError
Missing key(s)/Unexpected key(s) in state_dict for AutoencoderKL
```

或

```
Error(s) in loading state_dict for AutoencoderKLInferenceWrapper
```

## 根因（兩種）

### 根因 1：VAE 檔是 diffusers 格式

A1111 載入 VAE 時**只接受「LDM 格式」的鍵**（例如 `decoder.conv_in.weight`、`quant_conv.weight`）。

從 HuggingFace 直接下載的 `vae/diffusion_pytorch_model.safetensors` 其實是 **diffusers 格式**（鍵長這樣：`encoder.down_blocks.0...`、`decoder.mid_block...`、`to_q`）。

把 diffusers 格式的檔放進 `models\VAE\` 後：

| 情境 | 結果 |
|------|------|
| `sd_vae = Automatic`，切換到附近檢查點 | 自動挑到這顆壞 VAE → 載入失敗 → 「無法切換 <檢查點>」 |
| VAE 下拉手動選它 | 載入失敗 → 「無法切換 <VAE>」 |

### 根因 2：完整檢查點誤放 `models\VAE`（最常被忽略）

`sd_xl_base_1.0_0.9vae.safetensors` 這種檔名會令人以為是 VAE，但它其實是**完整 SDXL 檢查點**（6.9GB，頂層鍵含 `model.`/`conditioner.`/`first_stage_model.`）。它會被列進 VAE 下拉，但選取時 `load_state_dict(strict=True)` 對不上 → **`AutoencoderKLInferenceWrapper`** RuntimeError。

快速分辨：

| 特徵 | 完整檢查點（誤放 VAE 資料夾） | 真正可用的 VAE |
|---|---|---|
| 檔案大小 | 6~7 GB | ~160 MB（fp16）／~320 MB（fp32） |
| 頂層鍵 | `model.` / `cond_stage_model.` / `conditioner.` / `first_stage_model.` | `decoder.` / `encoder.` / `quant_conv.` / `post_quant_conv.` |

## 修復步驟（摘要）

1. **診斷格式**：用 `scripts/check_vae_format.py` 檢查 `models\VAE\` 下哪顆是 diffusers 格式或完整檢查點；輔以檔案大小與 `safe_open(...).metadata()` 判別。
2. **移動誤放的檢查點**：`models\VAE\...` → `models\Stable-diffusion\`（它本來就是檢查點）。
3. **抽取正確 VAE**：正確版本通常已烤進完整檢查點（例如 6.6GB 的 `sd_xl_base_1.0_0.9vae.safetensors`）。用 `scripts/extract_vae.py` 抽出 `first_stage_model.*` 存成獨立 VAE（例：248 tensors → 159.6 MiB），覆寫/新增到 `models\VAE\`。
4. **重啟 WebUI**：
   - 清掉殘留的 `python launch.py`（搶 7860 與 GPU）。
   - 啟動檔（如 `run.bat`）用相對路徑，**必須以 webui 根目錄為 CWD** 執行（PS：`Start-Process -WorkingDirectory '<根目錄>'`）。
   - **殘留的 `cmd /c call run.bat > log` 會鎖住 log 檔**，新實例寫不進去會被誤判成「重啟失敗」；先 Kill 掛起實例，重啟時改用**全新 log 檔名**。
   - 順序：`environment.bat` 加 PATH 失敗 → `'environment.bat' 不是內部或外部命令` + `exit code: 9009`（CWD 錯）；`python` 找不到 → `Couldn't launch python`（environment.bat 沒跑到）。
5. **驗證**（伺服器有 `--api` 時）：
   - `POST /sdapi/v1/options` 分別測「VAE 下拉選修好的檔」「`Automatic` + 切檢查點」「切檢查點」
   - `GET /sdapi/v1/options` 確認參數已變更，log 無新 `RuntimeError`
   - 伺服器**沒**掛 `--api` 時 `/sdapi/v1/*` 回 `{"detail":"Not Found"}`——改用 `http://127.0.0.1:7860/internal/ping` 做健康檢查，並以**免 API 的 in-process 驗證**（`modules.sd_vae` 載入路徑 + `GIT_PYTHON_GIT_EXECUTABLE`）證明 VAE 可載入。
6. **出圖煙霧測試**：`POST /sdapi/v1/txt2img` 能回圖即完成。

## 附檔

| 檔案 | 用途 |
|------|------|
| `SKILL.md` | 供 opencode 載入的完整流程說明 |
| `scripts/check_vae_format.py` | 判別 VAE 檔是 LDM、diffusers 還是完整檢查點 |
| `scripts/extract_vae.py` | 從完整檢查點抽取正確 VAE 並另存 |

## 注意事項

- `A tensor with all NaNs was produced in VAE.` 是 fp16 VAE 的正常訊息，A1111 會自動轉 fp32 重試。
- 錯誤類別區分：`AutoencoderKL` = VAE 格式錯；`AutoencoderKLInferenceWrapper` = 完整檢查點被當 VAE。
- 修好的 VAE 約 **160MB**（fp16）；看到 6.9GB 的「VAE」就是完整檢查點誤放。
- SDXL 官方獨立 VAE（**1.0 版**，fp32 319MB）：`https://huggingface.co/stabilityai/sdxl-vae/resolve/main/sdxl_vae.safetensors`；0.9 版無官方單獨下載，只能從檢查點抽取。
- `Anything-V3.0-X-VAE.pt` 是 SD1.x 用 VAE，套在 SDXL 會色偏，會提醒使用者而非刪檔。
- Windows 重啟失敗時，先看 log 的 `LastWriteTime` 是否凍結（殘留實例鎖檔），再檢查 CWD / PATH。