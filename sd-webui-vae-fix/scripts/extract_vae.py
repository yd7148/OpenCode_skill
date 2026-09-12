"""從完整檢查點抽取 first_stage_model.* 存成 A1111 可用的獨立 VAE。

用法:
    python extract_vae.py <checkpoint.safetensors> <out_vae.safetensors>

範例:
    python extract_vae.py ^
      "MODELS\\Stable-diffusion\\sd_xl_base_1.0_0.9vae.safetensors" ^
      "MODELS\\VAE\\sd_xl_base_1.0_0.9vae.safetensors"
"""

import argparse
import os
import sys

try:
    import torch
    from safetensors.torch import load_file, save_file
except ImportError:
    sys.exit("需要 torch + safetensors (請用 webui 內建 python 執行)")


def main() -> None:
    parser = argparse.ArgumentParser(description="從檢查點抽出 first_stage_model.* VAE")
    parser.add_argument("checkpoint", help="來源完整檢查點 .safetensors")
    parser.add_argument("output", help="輸出 VAE .safetensors")
    args = parser.parse_args()

    if not os.path.isfile(args.checkpoint):
        sys.exit(f"找不到檢查點: {args.checkpoint}")

    print(f"讀取 {args.checkpoint} ...")
    sd = load_file(args.checkpoint, device="cpu")
    vae = {
        k[len("first_stage_model."):]: v
        for k, v in sd.items()
        if k.startswith("first_stage_model.")
    }
    if not vae:
        sys.exit("此檢查點沒有 first_stage_model.* 鍵，無法抽取")
    del sd

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    save_file(vae, args.output)
    print(
        f"wrote {len(vae)} tensors -> {args.output} "
        f"({os.path.getsize(args.output):,} bytes)"
    )


if __name__ == "__main__":
    main()