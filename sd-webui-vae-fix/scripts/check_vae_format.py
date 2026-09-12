"""判別 safetensors 檔案是 LDM VAE 還是 diffusers 格式。

用法:
    python check_vae_format.py <path.safetensors>

輸出鍵前綴統計並判定格式，供 sd-webui-vae-fix skill 使用。
"""

import argparse
import sys

try:
    from safetensors import safe_open
except ImportError:
    sys.exit("需要 safetensors: pip install safetensors (或用 webui 內建 python)")


def main() -> None:
    parser = argparse.ArgumentParser(description="判斷 VAE/檢查點 safetensors 的鍵格式")
    parser.add_argument("path", help="safetensors 檔案路徑")
    args = parser.parse_args()

    with safe_open(args.path, framework="pt") as f:
        keys = list(f.keys())

    total = len(keys)
    prefix_count: dict[str, int] = {}
    for k in keys:
        if k.startswith("first_stage_model."):
            head = "first_stage_model"
        else:
            head = k.split(".")[0] if "." in k else k
        prefix_count[head] = prefix_count.get(head, 0) + 1

    print(f"總鍵數: {total}")
    for p, c in sorted(prefix_count.items(), key=lambda x: -x[1])[:20]:
        print(f"  {p}: {c}")

    has_first_stage = any(k.startswith("first_stage_model.") for k in keys)
    has_diffusers = any(
        ("down_blocks." in k or "mid_block." in k or "up_blocks." in k) for k in keys
    )
    has_checkpoint = any(
        (
            "model.diffusion_model" in k
            or "cond_stage_model" in k
            or "text_model" in k
            or "conditioner" in k
        )
        for k in keys
    )

    if has_first_stage:
        print("→ 完整檢查點（內含 first_stage_model）")
        if has_diffusers:
            print("   (可疑：同時出現 diffusers 鍵，請進一步檢查)")
        print("   ※ 若要當 VAE 用，請先抽取出 first_stage_model.*（見 extract_vae.py）")
    elif has_diffusers:
        print("→ DIFFUSERS 格式 — A1111 無法直接當 VAE 使用")
    elif has_checkpoint:
        print("→ 檢查點但不含 first_stage_model 前綴（需檢視內容）")
    elif set(prefix_count).intersection({"decoder", "encoder", "quant_conv", "post_quant_conv"}):
        print("→ LDM VAE 格式 — A1111 可直接使用（正確）")
    else:
        print("→ 無法判別")


if __name__ == "__main__":
    main()