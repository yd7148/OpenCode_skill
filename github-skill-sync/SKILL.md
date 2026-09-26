---
name: github-skill-sync
description: 同步本機 OpenCode skills（~/.config/opencode/skills/）與 GitHub 上的 OpenCode_skill 收藏庫（yd7148/OpenCode_skill），支援下載（GitHub→本機）與上傳（本機→GitHub）兩個方向。處理排除規則（.venv、__pycache__）、空目錄、commit 與 SSH push，並同步 GitHub 根目錄的 README.md / SKILLS.md 到地端。Use when asked to "同步 skill", "更新 skill 收藏庫", "sync skills", "上傳本機 skill 到 GitHub", "從 GitHub 拉下 skills", or to keep local skills in sync with the OpenCode_skill repo.
license: MIT
compatibility: opencode
metadata:
  audience: opencode agents
  workflow: opencode-skill-sync
  languages: zh-TW
---

# github-skill-sync — 本機 ↔ GitHub Skills 同步

同步本機 OpenCode skills 目錄與 GitHub 上的 `yd7148/OpenCode_skill` 收藏庫。本 skill 同時管理
**下載（GitHub→本機）** 與 **上傳（本機→GitHub）** 兩個方向，並維持兩邊說明文件（README.md / SKILLS.md）一致。

## 環境路徑（此機器已就緒）

| 項目 | 路徑 |
|------|------|
| 本機 skills 目錄 | `C:\Users\admin\.config\opencode\skills\`（Windows） |
| GitHub repo 本機 clone | `C:\Users\admin\OpenCode_skill` |
| GitHub 遠端 | `git@github.com:yd7148/OpenCode_skill.git`（**SSH**） |
| 共用說明文件 | `README.md`、`SKILLS.md`（repo 根目錄） |

本機環境：Windows PowerShell 5.1，**沒有 `rsync`**；用 `Copy-Item`/`robocopy` 取代 rsync 語法。

## SSH 設定（關鍵！）

- 使用 **Git for Windows 內附的 OpenSSH**，不是 Windows 系統 OpenSSH：
  Windows OpenSSH 9.5 與 GitHub 握手會失敗（`choose_kex: unsupported KEX method sntrup761x25519-sha512@openssh.com`）。
- 在 repo clone 內設定（**正斜線 + 8.3 短檔名，不可用反斜線/空格**）：
  ```powershell
  git config core.sshCommand "C:/PROGRA~1/Git/usr/bin/ssh.exe"
  ```
- 金鑰 `~/.ssh/id_ed25519`（ed25519），已貼到 GitHub Settings → SSH keys。
- 驗證：`git fetch origin` 成功即 OK。

## 通用規則（兩個方向都適用）

- **排除**：一律排除 `.venv/`、`__pycache__/`，避免虛擬環境與快取混入 repo。
- **空目錄**：Git 不追蹤空目錄，空的 skill 資料夾（無 SKILL.md）不會上傳；上傳前若某 skill 是空資料夾要提醒使用者。
- **說明文件一致性**：repo 根目錄的 `README.md` / `SKILLS.md` 若更新，應複製一份到本機 skills 目錄根，讓地端與 GitHub 說明一致。
- **commit 身份**：`git -c user.name="yd7148" -c user.email="yd7148@hotmail.com.tw"`。

## 方向一：下載（GitHub → 本機）

把 GitHub 上最新的 skill 內容拉下來，覆蓋到本機使用目錄。

```powershell
# 1. 更新本機 clone
git -C "C:\Users\admin\OpenCode_skill" pull origin main

# 2. 把 repo 中各 skill 同步到本機使用目錄（排除虛擬環境）
$SRC = "C:\Users\admin\OpenCode_skill"; $DST = "C:\Users\admin\.config\opencode\skills"
Get-ChildItem -LiteralPath $SRC -Directory | Where-Object { $_.Name -ne ".git" } | ForEach-Object {
  $name = $_.Name
  Copy-Item -Path (Join-Path $_.FullName "*") -Destination (Join-Path $DST $name) -Recurse -Force `
    -Exclude ".venv","__pycache__"
}
# 3. 同步根目錄說明文件
Copy-Item "$SRC\README.md" "$DST\README.md" -Force
Copy-Item "$SRC\SKILLS.md" "$DST\SKILLS.md" -Force
```

## 方向二：上傳（本機 → GitHub）

把本機新增或修改的 skill 提交並 push 到 GitHub。

```powershell
# 1. 先確認本機 clone 是最新
git -C "C:\Users\admin\OpenCode_skill" fetch origin; git -C "C:\Users\admin\OpenCode_skill" pull origin main

# 2. 把本機 skills 同步進 clone（排除虛擬環境）
$SRC = "C:\Users\admin\.config\opencode\skills"; $DST = "C:\Users\admin\OpenCode_skill"
Get-ChildItem -LiteralPath $SRC -Directory | ForEach-Object {
  $name = $_.Name; $dest = Join-Path $DST $name
  if ((Get-ChildItem -LiteralPath $_.FullName -Force | Measure-Object).Count -eq 0) { "SKIP 空目錄: $name"; return }
  Copy-Item -Path (Join-Path $_.FullName "*") -Destination $dest -Recurse -Force `
    -Exclude ".venv","__pycache__"
}
# 3. 更新 repo 根 README.md / SKILLS.md 到 clone（保持說明一致）
Copy-Item "$SRC\README.md" "$DST\README.md" -Force
Copy-Item "$SRC\SKILLS.md" "$DST\SKILLS.md" -Force

# 4. 檢視變更、commit、push（SSH；clone 已設 core.sshCommand 指向 Git OpenSSH）
Set-Location "C:\Users\admin\OpenCode_skill"
git add -A
git status --short
git -c user.name="yd7148" -c user.email="yd7148@hotmail.com.tw" commit -m "sync skills"
git push origin main
```

## 注意事項

- `.venv` 是各 skill 在本機的 python 虛擬環境，**永不**提交（已被各 skill 的 `.gitignore` 與上面的
  Copy-Item 排除遮蔽）。
- 若新增了 repo 沒有的 skill，記得同步更新 `README.md` 目錄表與 `SKILLS.md` 對應章節。
- push 用 **SSH**；若曾改用 HTTPS clone，記得 `git remote set-url origin git@github.com:yd7148/OpenCode_skill.git`。
- 若 `git push` 報 `unsupported KEX method`，代表用到了 Windows OpenSSH——先確認 core.sshCommand 設定（見上）。