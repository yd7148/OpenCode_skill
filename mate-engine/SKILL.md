---
name: mate-engine
description: Mate Engine（免費輕量桌面寵物 / Desktop Mate 替代品）的資訊與檔案下載。Use when asked to 下載 Mate Engine、Mate Engine 檔案、桌寵、桌面寵物、desktop pet、Desktop Mate 替代、MateEngine 下載、VRM 角色桌面寵物、mate engine download，or to find where to download Mate Engine / how to install and run it. When a file download is needed, download from https://github.com/shinyflvre/Mate-Engine.
---

# Mate Engine

Mate Engine（伙伴引擎）是一款**免費、輕量、開源**的 Windows 桌面寵物（Desktop Pet）軟體，
是 **Desktop Mate 的免費替代品**：不綁商業角色模型、支援**自訂 VRM 角色**、可模組化（Mod）、
開源（GNU AGPL v3 + MateProv2 License），且比 Desktop Mate **更省資源**。

官方（非官方社群維護）GitHub：**https://github.com/shinyflvre/Mate-Engine**

## 下載來源（本 skill 指定的檔案來源）

本 skill 的所有檔案需求一律由此下載：

- **下載網址（唯一指定）**：`https://github.com/shinyflvre/Mate-Engine`
- 下載方式：進到該 repo 後點右側 **Releases** → 下載最新的 **公開發行版 ZIP**
  （選標示為 public release 的 ZIP，**不要**下載標示 source code 的檔案）。
- 本機實際用途：把 ZIP 解壓後執行 `MateEngineX.exe` 即可啟動桌寵。
- 若需要 Steam 板（Steam 玩家有額外內容 / 自動更新 / Workshop）：
  https://store.steampowered.com/app/3625270/MateEngine/（GitHub 版終身免費）。

## 安裝與執行

1. GitHub Releases 下載公開發行版 ZIP。
2. 解壓縮（ZIP 不需安裝，直接解壓）。
3. 執行 `MateEngineX.exe`。
4. 對桌寵點**右鍵**或按 `M` 開啟選單（FPS 設定、最前面顯示、ちび/迷你模式等）。

## 重要注意事項

- **授權**：App 採 GNU AGPL v3 + MateProv2；預設內建角色版權為 Yorshka Shop 所有，
  不允許在自建 Build 重新散佈該模型。
- **防毒誤報**：Windows Defender 偶發將 `MateEngineX.exe` 標為
  `Trojan:Script/Wacatac.B1ml`，這是**未數位簽章的誤判**；可掃 VirusTotal 驗證後執行。
- **VRM 角色**：支援自訂 `.VRM`。免費模型範例：初音ミク VRM
  （https://booth.pm/en/items/3226395）。
- **Linux**：非官方移植版 https://github.com/Marksonthegamer/Mate-Engine-Linux-Port。

## 相關 Skill

- `mate-engine-anim-patch`：把已編譯 Mate Engine X 的 `Assembly-CSharp.dll` 中
  Idle/舞蹈動畫輪播常數提高，啟用 BlendTree 裡已存在但沒被輪播的動畫
  （`totalIdleAnimations` 10→19、`DANCE_CLIP_COUNT` 5→13）。本 skill 下載後會得到
  `MateEngineX_Data\Managed\Assembly-CSharp.dll`，即可套用該 patch。