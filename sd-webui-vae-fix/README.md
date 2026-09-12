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

## 根因

A1111 載入 VAE 時**只接受「LDM 格式」的鍵**（例如 `decoder.conv_in.weight`、`quant_conv.weight`）。

從 HuggingFace 直接下載的 `vae/diffusion_pytorch_model.safetensors` 其實是 **diffusers 格式**（鍵長這樣：`encoder.down_blocks.0...`、`decoder.mid_block...`、`to_q`）。

把 diffusers 格式的檔放進 `models\VAE\` 後：

| 情境 | 結果 |
|------|------|
| `sd_vae = Automatic`，切換到附近檢查點 | 自動挑到這顆壞 VAE → 載入失敗 → 「無法切換 <檢查點>」 |
| VAE 下拉手動選它 | 載入失敗 → 「無法切換 <VAE>」 |

## 修復步驟（摘要）

1. **診斷格式**：用 `scripts/check_vae_format.py` 檢查 `models\VAE\` 下哪顆是 diffusers 格式。
2. **抽取正確 VAE**：正確版本通常已烤進完整檢查點（例如 6.6GB 的 `sd_xl_base_1.0_0.9vae.safetensors`）。用 `scripts/extract_vae.py` 抽出 `first_stage_model.*` 存成獨立 VAE，覆寫到 `models\VAE\`。
3. **重啟 WebUI**：清掉殘留的 `python launch.py`，用含 `--api` 的啟動檔重開，備份舊 log 對照。
4. **API 驗證**：
   - `POST /sdapi/v1/options` 分別測「VAE 下拉選修好的檔」「`Automatic` + 切檢查點」「切 6.6GB 烤 VAE 檢查點」
   - `GET /sdapi/v1/options` 確認參數已變更，log 無新 `RuntimeError`
5. **出圖煙霧測試**：`POST /sdapi/v1/txt2img` 能回圖即完成。

## 附檔

| 檔案 | 用途 |
|------|------|
| `SKILL.md` | 供 opencode 載入的完整流程說明 |
| `scripts/check_vae_format.py` | 判別 VAE 檔是 LDM 還是 diffusers 格式 |
| `scripts/extract_vae.py` | 從完整檢查點抽取正確 VAE 並另存 |

## 注意事項

- `A tensor with all NaNs was produced in VAE.` 是 fp16 VAE 的正常訊息，A1111 會自動轉 fp32 重試。
- 修好的 `sd_xl_base_1.0_0.9vae.safetensors` 約 **160MB**（fp16）；若是 320MB 的 diffusers 格式就是被覆蓋了。
- `Anything-V3.0-X-VAE.pt` 是 SD1.x 用 VAE，套在 SDXL 會色偏，會提醒使用者而非刪檔。