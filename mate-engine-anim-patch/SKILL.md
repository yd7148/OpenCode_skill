---
name: mate-engine-anim-patch
description: 擴充已編譯 Unity 的 Mate Engine X（MateEngineX，桌面虛擬伴侶/桌寵）的動作數量——把 AvatarAnimatorController 的 totalIdleAnimations / DANCE_CLIP_COUNT 常數提高，讓 BlendTree 中已存在但未輪播的 idle/舞蹈動畫全部啟用。流程：dnfile+dncil 反組譯 Assembly-CSharp.dll 定位 .ctor 常數、UnityPy 驗證 AnimatorController BlendTree 實際 clip 數、Mono.Cecil 重寫 IL、dnfile 全量驗證。Use when asked to 增加 Mate 動作 / 增加 idle 數量 / 增加舞蹈數量 / 擴充 mate 動作 / mate idle 輪播 / patch MateEngine 動畫計數 / mate engine anim patch。
---

# Mate Engine X 動作數量擴充（Idle / Dance）

針對已編譯 Unity（Mono）的 Mate Engine X（`MateEngineX.exe`，Steam 版桌面伴侶）——**無原始碼**，只能改
`Assembly-CSharp.dll`。目標是把 BlendTree 中**已存在但被常數寫死而沒輪播**的動畫全部啟用。

## 核心事實（X3.3.0，Unity 6000.2.6）

| 項目 | 值 |
|---|---|
| 動畫控制器 | `AvatarAnimatorControllerV2 1`（sharedassets0.assets pathid 554） |
| 類別 | `AvatarAnimatorController`（TypeDef 62），欄位 token `totalIdleAnimations=0x04000144`、`DANCE_CLIP_COUNT=0x04000147` |
| 預設值（.ctor） | `totalIdleAnimations = 10`（`ldc.i4.s`）；`DANCE_CLIP_COUNT = 5`（`ldc.i4.5`） |
| 實際 idle 動畫 | **19 個** PET_IDLE（0..18），但 count=10 → 只輪播前 10 個 |
| 實際舞蹈 | **13 個** PET_DANCING..13，但 count=5 → 只輪播前 5 個 |
| 誰寫入欄位 | **僅 .ctor**（全 IL stfld 掃描證實），場景/設定檔不覆寫 → patch ctor 即生效 |
| 支援格式/組件 | 動畫 clip 在 sharedassets0.assets；Mono 執行期不驗證 PE 佈局（Cecil 重寫安全） |

## 環境工具（本機已就緒）

| 工具 | 路徑 |
|---|---|
| dnfile + dncil | `C:\Users\USER\AppData\Local\Temp\opencode\matedlltools`（Python：`sys.path.insert(0, ...)`） |
| UnityPy | `C:\Users\USER\AppData\Local\Temp\opencode\unitypy` |
| Mono.Cecil + 補丁程式 | `C:\Users\USER\AppData\Local\Temp\opencode\cecil\PatchField.exe`（net40 Cecil + csc 編譯） |
| .NET Framework csc | `C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe` |
| 目標 DLL | `D:\2026-08-Vtuber\14-Mate-Engine-X3.3.0\MateEngineX_Data\Managed\Assembly-CSharp.dll` |

## 流程

### 1. 反組譯 .ctor，確認現況
用 dnfile 找 `AvatarAnimatorController` 的 `.ctor`（TypeDef 62，`row.MethodList[].row`），
dncil `read_method_body_from_bytes` 反組譯。RVA→檔案偏移：text section 內
`off = PointerToRawData + (rva - VirtualAddress)`。`.ctor` 內共有 9 個欄位常數，
`ldc.i4.s 10 → stfld 0x04000144`（totalIdleAnimations）、`ldc.i4.5 → stfld 0x04000147`（DANCE_CLIP_COUNT）。

### 2. 用 UnityPy 驗證 BlendTree 真的有那麼多 clip（關鍵！）
讀 `sharedassets0.assets`，找 pathid 554 的 AnimatorController 的 `m_Controller`（ControllerConstant）：
- `m_StateMachineArray[0].data.m_StateConstantArray` → 每個 StateConstant 的 `m_BlendTreeConstantArray[0]`
- 遍歷 `m_NodeArray`（`m_ChildIndices` 遞迴，葉子用 `m_ClipID` 對 `m_AnimationClips` 取名）
- Idle = State 4：node[1] 子樹 clipIDs 0..18 = 19 個 PET_IDLE；Dance = State 2：13 個 PET_DANCING..13
- 若樹只有 N 個葉子，count 最多設 N（設超過會 clamp 到最後一個）

### 3. 值能否用「同長度位元組」表示？
- 可（1 byte 定值 opcode）：直接 hex 改。例如 `ldc.i4.s 19`（`1F 13`）替換 `ldc.i4.s 10`（`1F 0A`）。
- 不可（`ldc.i4.5` 只有 1 byte，改 `ldc.i4.s 13` 會 +1 byte → 位移後續全部 method RVA）：
  **必須用 Mono.Cecil 重寫**。在本機 csc + PatchField.exe：
  ```
  PatchField.exe <in.dll> <out.dll> DANCE_CLIP_COUNT 13
  ```
  內建邏輯：找 `ldc.i4.5; stfld <欄位名>`，把前一個指令改為 `ldc.i4.s <值>`。
  ⚠️ 不要手工插入 byte（會讓整份檔 .text 之後所有 method RVA 錯位）。

### 4. 驗證（寫入前→新檔，確認後才覆蓋）
- `dnfile` 能解析（TypeDef/MethodDef 行數不變：487 / 2718）
- 反組譯 `.ctor`：`ldc.i4.s 19`/`ldc.i4.s 13` 正確，其他 stfld token 不變
- 全量 sweep：對每支 MethodDef 反組譯全部 instructions 均成功
- 覆蓋前先備份：`.bak`（原始）、`.bak2`（前一階段）

### 5. 還原
把 `Assembly-CSharp.dll.bak`（原始）複製回 `Assembly-CSharp.dll` 即可。

## 常見陷阱

- 先確認欄位「只被 .ctor 寫」：掃全 DLL 的 `stfld token(0x04000144/0x04000147)`。若 SaveLoadHandler 也寫
  就從設定面著手。
- 確認「場景沒有序列化覆寫」：用 UnityPy 掃所有 MonoBehaviour 原始位元組，若找不到
  特徵序列 `[int count][float 12.0][float 3.0][int 5][bool][bool][float 15.0][float 2.0]`，
  代表元件是執行期 AddComponent，ctor 預設才會生效。
- 別用 PowerShell heredoc 跑 python（5.1 不支援 `<<`）；寫成 `.py` 檔再 `python x.py`。
- 舞蹈的 13：PET_DANCING 為 index0，`DANCE_CLIP_COUNT=13` 會讓 `Random.Range(0,13)` 與 `%13` 涵蓋所有舞步。
- Husbando 模式（isMale）只有 9 個 HUS_IDLE，IdleIndex≥8 會 clamp 到最後一個，屬正常行為。