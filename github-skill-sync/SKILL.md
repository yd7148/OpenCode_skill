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

## 環境路徑（已就緒）

| 項目 | 路徑 |
|------|------|
| 本機 skills 目錄 | `~/.config/opencode/skills/` |
| GitHub repo 本機 clone | `~/OpenCode_skill` |
| GitHub 遠端 | `git@github.com:yd7148/OpenCode_skill.git`（SSH） |
| 共用說明文件 | `README.md`、`SKILLS.md`（repo 根目錄） |

前置需求：SSH key 已加至 GitHub（`ssh -T git@github.com` 驗證通過），repo 以 SSH remote clone 到 `~/OpenCode_skill`。

## 通用規則（兩個方向都適用）

- **排除**：`rsync` 一律排除 `.venv/`、`__pycache__/`，避免虛擬環境與快取混入 repo。
- **空目錄**：Git 不追蹤空目錄，空的 skill 資料夾（無 SKILL.md）不會上傳；上傳前若某 skill 是空資料夾要提醒使用者。
- **說明文件一致性**：repo 根目錄的 `README.md` / `SKILLS.md` 若更新，應複製一份到本機 skills 目錄根，讓地端與 GitHub 說明一致。
- **commit 身份**：`git -c user.name="yd7148" -c user.email="yd7148@hotmail.com.tw"`。

## 方向一：下載（GitHub → 本機）

把 GitHub 上最新的 skill 內容拉下來，覆蓋到本機使用目錄。

```bash
# 1. 更新本機 clone
git -C ~/OpenCode_skill pull origin main

# 2. 把 repo 中各 skill 同步到本機使用目錄（排除虛擬環境）
SRC=~/OpenCode_skill; DST=~/.config/opencode/skills
for d in "$SRC"/*/; do
  name=$(basename "$d")
  [ "$name" = ".git" ] && continue
  rsync -a --exclude='.venv/' --exclude='__pycache__/' "$d/" "$DST/$name/"
done

# 3. 同步根目錄說明文件
cp "$SRC/README.md" "$DST/README.md"
cp "$SRC/SKILLS.md" "$DST/SKILLS.md"
```

## 方向二：上傳（本機 → GitHub）

把本機新增或修改的 skill 提交並 push 到 GitHub。

```bash
# 1. 先確認本機 clone 是最新
git -C ~/OpenCode_skill fetch origin && git -C ~/OpenCode_skill pull origin main

# 2. 把本機 skills 同步進 clone（排除虛擬環境）
SRC=~/.config/opencode/skills; DST=~/OpenCode_skill
for d in "$SRC"/*/; do
  name=$(basename "$d")
  [ -n "$(ls -A "$d")" ] || { echo "SKIP 空目錄: $name"; continue; }
  rsync -a --exclude='.venv/' --exclude='__pycache__/' "$d/" "$DST/$name/"
done

# 3. 更新 repo 根 README.md / SKILLS.md 到 clone（保持說明一致）
cp "$SRC/README.md" "$DST/README.md"
cp "$SRC/SKILLS.md" "$DST/SKILLS.md"

# 4. 檢視變更、commit、push
cd ~/OpenCode_skill
git add -A
git status --short
git -c user.name="yd7148" -c user.email="yd7148@hotmail.com.tw" \
    commit -m "sync skills"
git push origin main
```

## 注意事項

- `.venv` 是各 skill 在本機的 python 虛擬環境，**永不**提交（已被各 skill 的 `.gitignore` 與 rsync 排除遮蔽）。
- 若新增了 repo 沒有的 skill，記得同步更新 `README.md` 目錄表與 `SKILLS.md` 對應章節。
- push 用 SSH（`origin` remote 已設為 SSH URL），不需 token；可用 `ssh -T git@github.com` 確認認證是否有效。
