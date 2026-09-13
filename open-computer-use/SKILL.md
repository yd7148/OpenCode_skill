---
name: open-computer-use
description: Platform-neutral guidance for using Open Computer Use, the open-source Computer Use MCP server and CLI for macOS, Linux, and Windows. Use when an agent needs to install, verify, troubleshoot, configure, or operate Open Computer Use through its native CLI, stdio MCP server, or direct Computer Use tool calls.
---

# Open Computer Use

## Overview

Open Computer Use exposes Computer Use as a local CLI and stdio MCP server. It is not Codex.app-specific; adapt the commands and MCP config to the agent runtime you are operating in.

The macOS runtime requires macOS 14.0 or later. Windows and Linux use their own platform runtimes and are not subject to this macOS minimum.

It supports the same core tool surface across macOS, Linux, and Windows:
`list_apps`, `get_app_state`, `click`, `perform_secondary_action`, `scroll`,
`drag`, `type_text`, `press_key`, and `set_value`.

## Core Workflow

1. On macOS, run `sw_vers -productVersion` before invoking the CLI and require macOS 14.0 or later. On older versions, explain that the runtime cannot launch; do not recommend `doctor` or permission changes as a fix for binary incompatibility.
2. Check the CLI is installed with `open-computer-use -h` or `ocu -h`. If installation or setup is missing, read [references/installation.md](references/installation.md).
3. On supported macOS versions, run `open-computer-use doctor` before the first real GUI task. If permissions are missing, ask the user to approve Accessibility and Screen Recording in the onboarding UI.
4. Inspect available apps before acting: `open-computer-use call list_apps`.
5. Capture current UI state with `open-computer-use call get_app_state --args '{"app":"TextEdit"}'`. The default state is usually enough for UI operation.
6. When the task needs longer semantic text, such as chat history, email bodies, document text, or long form content, call `get_app_state` with `text_limit: 1000` or `text_limit: "max"`.
7. When visible long pages or lists appear incomplete even after scrolling, call `get_app_state` with a larger `max_tree_nodes` or `max_tree_depth`.
8. Prefer element-targeted actions using `element_index` from the latest `get_app_state` result.
9. For multi-step CLI work, use `open-computer-use call --calls '<json-array>'` so one process can reuse the latest element index mapping.
10. For agent runtimes that support local MCP servers, configure `open-computer-use mcp` or `ocu mcp` and call the exposed Computer Use tools directly. Read [references/usage.md](references/usage.md).
11. If communication, permission, or desktop-session access fails, read [references/troubleshooting.md](references/troubleshooting.md).

## Operating Rules

- Treat the target desktop as the user's real session. Do not inspect password managers, unrelated private content, or sensitive apps unless the user explicitly asked for that task.
- Ask before sending, deleting, purchasing, approving, uploading, or making other externally visible changes.
- Do not assume Codex.app plugin helpers are available. Use the installed `open-computer-use` / `ocu` CLI or an explicit MCP config.
- Always run `get_app_state` before using `element_index`; do not guess indexes across sessions or after large UI changes.
- Prefer semantic actions and `set_value` for editable controls. Use coordinate `click`, `scroll`, and `drag` only when the element tree does not expose a safer target.
- On macOS, do not enable `OPEN_COMPUTER_USE_ALLOW_GLOBAL_POINTER_FALLBACKS=1` unless the user explicitly requested `click_method: "global"`, a `drag` that must drive a window-server drag session (window move, drag-select text, Finder drag-and-drop), or other diagnostic behavior that may move the real pointer. Without it `drag` reports `Drag delivered via app_post` and those operations have no effect; see `references/usage.md` for alternatives.
- On Windows and Linux, confirm the command is running inside the logged-in desktop session before assuming GUI automation is available.

## Common CLI Actions

```sh
open-computer-use -h
ocu -h
open-computer-use doctor
open-computer-use call list_apps
ocu call list_apps
open-computer-use call get_app_state --args '{"app":"TextEdit"}'
open-computer-use call get_app_state --args '{"app":"TextEdit","text_limit":1000}'
open-computer-use call get_app_state --args '{"app":"TextEdit","text_limit":"max"}'
open-computer-use call get_app_state --args '{"app":"Google Chrome","max_tree_nodes":3000,"max_tree_depth":96}'
open-computer-use call click --args '{"app":"TextEdit","element_index":"0"}'
open-computer-use call type_text --args '{"app":"TextEdit","text":"Hello from Open Computer Use"}'
```

For a short sequence that reuses state in one process:

```sh
open-computer-use call --calls '[
  {"tool":"get_app_state","args":{"app":"TextEdit"}},
  {"tool":"press_key","args":{"app":"TextEdit","key":"Return"}}
]'
```

## MCP Usage

For runtimes that can launch local MCP servers over stdio, use:

```toml
[mcp_servers.open_computer_use]
command = "open-computer-use"
args = ["mcp"]
```

Read [references/usage.md](references/usage.md) for JSON config examples, direct tool-call patterns, and platform notes.

## References

- [references/installation.md](references/installation.md): one-time CLI install, agent MCP install commands, and macOS permissions.
- [references/usage.md](references/usage.md): MCP config, direct CLI calls, sequencing, and platform behavior.
- [references/troubleshooting.md](references/troubleshooting.md): permission, desktop-session, app discovery, and action failures.

## 本機實測筆記（macOS，2026-09）

實測環境：macOS + `open-computer-use` v0.3.5，以下為本次完整安裝到操作的經驗。

- **Node 安裝**：本機若無 node/npm，先 `brew install node`（實測 v26.8.2 / npm 11.19.1）。
- **npm 安裝**：`npm i -g open-computer-use`。若出現 `npm warn install-scripts open-computer-use@0.3.5 (postinstall…)` 表示 postinstall 被 npm 阻擋，**不影響執行**（runtime 內建於套件）；若真的有缺檔再補 `npm i -g --allow-scripts=open-computer-use`。
- **權限**：`open-computer-use doctor` 顯示 `accessibility=missing / screenRecording=missing` 時，用下列指令直接開設定頁，請使用者勾選「執行 opencode 的終端機 app」：
  ```sh
  open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"
  open "x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture"
  ```
  授權後 `doctor` 應顯示 `accessibility=granted, screenRecording=granted`。
- **已實測通過**的工具：`list_apps`、`get_app_state`（含 `text_limit` 搜尋）、`click`（`element_index`）、`set_value`、`type_text`、`press_key`。
- **陷阱 1**：`open -a TextEdit` 啟動會停在「打開」open-panel，`press_key Escape` 無法關閉，需找 `新增文件`（`ID: NewDocumentButton`）以 `click` 建立空白文件；此後才有 `First Text View` 可 `set_value`／`type_text`。
- **陷阱 2**：有未存內容時 `press_key Cmd+Q` 會彈「儲存/刪除」對話框，點 `刪除`（`ID: DontSaveButton`）後 TextEdit 會**自動重開**（pid 改變）回到開啟面板，需再按一次 `Cmd+Q`（或 `osascript -e 'tell application "TextEdit" to quit'`）才會真正結束。
- **多步驟重用狀態**：`open-computer-use call --calls '[{...},{...}]'` 讓單一 process 內連續動作共用最近的 `element_index` 對映，避免跨 process index 失效。
