---
name: opencode-session-auto-name
description: 讓 opencode 的 session 標題自動以「第一次 prompt 的總結」命名（或進行中 todo）。使用 opencode-auto-name plugin（0 Token、純規則式、與模型無關），並記錄原生自動命名（small model）在 opencode/big-pickle 供應商下的已知 bug 與替代方案比較。Use when asked to "自動命名 session", "標題自動取名", "session 標題總結", "第一個 prompt 當作標題", "自動命名 conversation title", or to configure opencode session auto-titling.
license: MIT
compatibility: opencode
metadata:
  audience: opencode agents
  workflow: opencode-session-auto-title
  languages: zh-TW
---

# opencode-session-auto-name — Session 標題自動命名

讓 opencode 的 session 名稱自動取自「第一次使用者 prompt 的總結」或「進行中 todo」，
解決原生開新 session 只有 `New session - ...` 泛型標題的困擾。

## 已安裝設定（本機，2026-09-21）

- Plugin：**opencode-auto-name v0.1.3**（luchev），安裝在 `C:\Users\N000149839\.config\opencode\node_modules\`。
- 全域設定 `C:\Users\N000149839\.config\opencode\opencode.jsonc`：
  ```jsonc
  {
    "plugin": [
      ["opencode-auto-name", { "template": "{firstMessage}", "maxLength": 50 }]
    ]
  }
  ```
- `template: "{firstMessage}"` → 標題**只取第一個訊息的總結**（符合「第一 prompt 總結」需求）。
  若想要「有進行中 todo 時優先顯示 todo」，改回預設 `"{task || firstMessage}"`。
- plugin 引入方式：config 的 `plugin` 陣列只需寫套件名稱（`"opencode-auto-name"` 或
  `["opencode-auto-name", {...}]`）；opencode 從 config 目錄 `node_modules` 解析。
  npm install 時 Node 22.17.1 會出現 `EBADENGINE`（建議 ^22.22.2）只是警告，可用。

## 安裝 / 重裝步驟

```powershell
cd "$env:USERPROFILE\.config\opencode"
npm install opencode-auto-name
# 在 opencode.jsonc 加入 plugin 陣列（如上）
# 重啟 opencode
```

## 運作機制（opencode-auto-name）

- 監聽 `session.created` / `message.updated` / `todo.updated` / `command.executed`，
  以樣板算標題；**debounce 10s**（避免對話中標題狂跳），另每 60s 周期重查。
- 「總結」是**純規則式**，**不呼叫 LLM、0 Token、與模型無關**：
  去除開頭贅詞（"i want to"、"can you"、""請…"等）→ 取第一句 → 去尾標點 →
  超過 `maxLength` 截斷並加 `…`。
- 因此「總結」= 第一個 prompt 的**首句裁剪**，不是 AI 語意摘要。

### 樣板變數
| 變數 | 意義 |
|------|------|
| `{project}` | 專案名（git repo / 目錄 basename） |
| `{task}` | 目前 `in_progress` todo 內容 |
| `{firstMessage}` | 第一個使用者訊息的總結 |
| `{messageCount}` | 訊息數 |
| `{model}` | 目前使用的模型 |
| `{date}` / `{time}` | 日期（MM/DD）／時間（HH:MM） |

樣板語法：`{a || b}` 表示 a 為空時退回 b。

## 驗證

1. 重啟 opencode（plugin 僅啟動時載入）。
2. 新開 session → 打第一句話 → 等 ~10 秒 → 標題列顯示該訊息首句。
3. 手動改過標題的舊 session 不受影響（opencode 只覆寫「仍是預設標題」者）。

## 為什麼不用「原生自動命名」

opencode 原生（`packages/opencode/src/session/prompt.ts` 的 `ensureTitle`）會在開新
session、僅有一則真實 user 訊息且仍是預設標題時，用 **small model** 總結第一則訊息取名。
已知問題：

- **issue #30662**：用 `opencode` 供應商模型（如 `opencode/big-pickle`）當 small model 時，
  自動命名**默默失敗**，標題停在 `New session - ...`。
- **issue #7523**：命名依賴 small model（預設類 `gpt-5-nano`）；該模型未開/壞掉就失效。

所以本機（big-pickle）直接靠 plugin 方案；原生修法空白（`"small_model": "provider/modelID"`
指到可工作的模型）仍受 #30662 影響，不推薦。

## 替代方案比較（若需要「AI 語意總結」再考慮）

| 方案 | 機制 | Token | 需要 LLM |
|------|------|-------|---------|
| A. 原生 `small_model` 修法 | core 用 small model 總結第一則訊息 | ~1 call/session，極低 | ✅（big-pickle 下壞） |
| B. opencode-auto-name（已裝） | 規則式首句裁剪 | **0** | ❌ |
| C. opencode-session-summary | 每次閒置 + ≥4 新訊息，LLM 重生成一句；可設 `model` | 每 call 帶對話脈絡，長 session 可能數萬 Token | ✅ |
| D. opencode-autotitle | 關鍵字即時取名(🔍) + AI 精煉(✨)，自動挑最便宜模型；需 clone+build 放 `~/.config/opencode/plugins/` | 🔍0 + ✨0.5–2K/call | 🔍❌ + ✨✅ |

## Deliverables checklist
- [ ] `npm install opencode-auto-name` 成功（config 目錄 `node_modules`）
- [ ] `opencode.jsonc` 有 `plugin` 陣列（名稱或 tuple 帶 options）
- [ ] 重啟後新 session 首句即出現於標題