# Mate Engine X 3.3.0 動畫節點盤點

> 來源：`MateEngineX_Data/sharedassets0.assets`；主 Animator：pathid 554。
> 本報告只盤點，不修改遊戲檔案。

## 摘要

- AnimationClip：82 支
- 主 Animator 實際使用的 Clip：77 支
- 未被任何 Animator 狀態引用：1 支
- 主 Animator 層：5 層
- 全部 AnimatorController 層：9 層

## 主 Animator 參數

| 索引 | 類型 | 參數 |
|---:|---|---|
| 0 | Bool | `isIdle` |
| 1 | Bool | `isDragging` |
| 2 | Bool | `isDancing` |
| 0 | Float | `Blend` |
| 1 | Float | `IdleIndex` |
| 3 | Bool | `HoverTrigger` |
| 4 | Bool | `isSitting` |
| 5 | Bool | `HoverFaceTrigger` |
| 2 | Float | `DanceIndex` |
| 6 | Bool | `isWindowSit` |
| 7 | Bool | `isTaskbarSit` |
| 8 | Bool | `isBigScreen` |
| 9 | Bool | `isBigScreenSaver` |
| 10 | Bool | `isBigScreenAlarm` |
| 3 | Float | `WindowSitIndex` |
| 11 | Bool | `IsSleeping` |
| 4 | Float | `BigScreenBlend` |
| 12 | Bool | `isTalking` |
| 5 | Float | `isMale` |
| 6 | Float | `isFemale` |
| 13 | Bool | `isCustomDancing` |
| 14 | Bool | `isWaitingForDancing` |
| 15 | Bool | `Headpat` |
| 16 | Bool | `IntimeRegion` |
| 17 | Bool | `FaceLoop` |
| 18 | Bool | `HairStroke` |
| 19 | Bool | `isEating` |
| 20 | Bool | `isDrinking` |
| 21 | Bool | `HideLeft` |
| 22 | Bool | `HideRight` |
| 23 | Bool | `WalkLeft` |
| 24 | Bool | `WalkRight` |

## 主 Animator 層與狀態

### Base Layer

| 狀態索引 | 狀態 | 動畫／BlendTree 葉節點 | 迴圈 | 速度 |
|---:|---|---|---|---:|
| 0 | Intro | `PET_INTRO`, `HUS_IDLE09` | 否 | 1 |
| 1 | Drag | `PET_DRAGGING`, `HUS_DRAG` | 是 | 1 |
| 2 | Dance | `PET_DANCING`, `PET_DANCING_2`, `PET_DANCING_3`, `PET_DANCING_4`, `PET_DANCING_5`, `PET_DANCING_6`, `PET_DANCING_7`, `PET_DANCING_8`, `PET_DANCING_9`, `PET_DANCING_10`, `PET_DANCING_11`, `PET_DANCING_12`, `PET_DANCING_13`, `PET_DANCING`, `HUS_DANCE_01`, `HUS_DANCE_02`, `HUS_DANCE_03`, `HUS_DANCE_04`, `HUS_DANCE_01`, `HUS_DANCE_02`, `HUS_DANCE_03`, `HUS_DANCE_04`, `HUS_DANCE_01`, `HUS_DANCE_02`, `HUS_DANCE_03`, `HUS_DANCE_04`, `HUS_DANCE_02`, `HUS_DANCE_01` | 是 | 1 |
| 3 | Head Pat | `PET_LAUGHING` | 是 | 1 |
| 4 | Idle | `PET_IDLE`, `PET_IDLE_UPDATE2_01`, `PET_IDLE_UPDATE2_02`, `PET_IDLE_UPDATE2_03`, `PET_IDLE_UPDATE2_04`, `PET_IDLE_2`, `PET_IDLE_14`, `PET_IDLE_4`, `PET_IDLE_3`, `PET_IDLE_5`, `PET_IDLE_15`, `PET_IDLE_13`, `PET_IDLE_9`, `PET_IDLE_12`, `PET_IDLE_6`, `PET_IDLE_10`, `PET_IDLE_11`, `PET_IDLE_7`, `PET_IDLE_8`, `PET_IDLE`, `HUS_IDLE01`, `HUS_IDLE02`, `HUS_IDLE03`, `HUS_IDLE04`, `HUS_IDLE05`, `HUS_IDLE06`, `HUS_IDLE07`, `HUS_IDLE08`, `HUS_IDLE09`, `HUS_IDLE05`, `HUS_IDLE03`, `HUS_IDLE06`, `HUS_IDLE07`, `HUS_IDLE02`, `HUS_IDLE04`, `HUS_IDLE09`, `HUS_IDLE06`, `HUS_IDLE08`, `HUS_IDLE03`, `HUS_IDLE01` | 是 | 1 |
| 5 | Sitting | `KawaiiMacaronMotion02` | 是 | 1 |
| 6 | WindowSit | `PET_SIT_05`, `PET_SIT_01`, `PET_SIT_02`, `PET_SIT_03`, `sit 1`, `PET_SIT_06`, `PET_SIT_03`, `PET_SIT_02`, `PET_SIT_01`, `sit 1`, `BETA_PET_WINDOW_LAY`, `PET_SIT_07`, `BETA_PET_WINDOW_LAY`, `PET_SIT_06` | 是 | 1 |
| 7 | Alarm | `BIG_SCREEN_01` | 是 | 1 |
| 8 | Big Screen | `BIG_SCREEN_01`, `SCREEN_SAVER_01`, `PET_IDLE_UPDATE2_02`, `PET_IDLE_UPDATE2_03`, `PET_IDLE_UPDATE2_04`, `PET_IDLE_UPDATE2_01`, `BIG_SCREEN_01` | 是 | 1 |
| 9 | Eat | — | 是 | 1 |
| 10 | Screen Saver | `SCREEN_SAVER_04` | 是 | 1 |
| 11 | Animation 1 | `SCREEN_SAVER_01` | 是 | 1 |
| 12 | Animation 2 | `SCREEN_SAVER_02` | 是 | 1 |
| 13 | Animation 3 | `SCREEN_SAVER_03` | 是 | 1 |
| 14 | Drink | — | 是 | 1 |
| 15 | Sleeping | `PET_SLEEPING` | 是 | 0.6 |
| 16 | Custom Dance | `CUSTOM_DANCE` | 是 | 1 |
| 17 | Intime Region | `PET_POSE_3` | 是 | 1 |
| 18 | Next Custom Dance | — | 是 | 1 |
| 19 | Previous Custom Dance | — | 是 | 1 |
| 20 | Hide | — | 是 | 1 |
| 21 | Wait For Dance | `PET_IDLE_12` | 是 | 1 |
| 22 | Hide Right | `TEST_HIDE_RIGHT` | 是 | 1 |
| 23 | Hide Left | `TEST_HIDE_LEFT` | 是 | 1 |
| 24 | Hidden Left | — | 是 | 1 |
| 25 | Hidden Right | — | 是 | 1 |

### Face Layer

| 狀態索引 | 狀態 | 動畫／BlendTree 葉節點 | 迴圈 | 速度 |
|---:|---|---|---|---:|
| 0 | Faceloop | `FACE_RESET` | 是 | 1 |
| 1 | Head Pat | `FACE_SMILE` | 是 | 1 |
| 2 | Face Loop | `FACE_IDLE_1` | 是 | 1 |
| 3 | Drag | `FACE_DRAG` | 是 | 1 |
| 4 | Intime Region | `FACE_INTIME` | 是 | 1 |
| 5 | Hair Stroke | `FACE_HAIR_STROKE` | 是 | 1 |

### Speak Layer

| 狀態索引 | 狀態 | 動畫／BlendTree 葉節點 | 迴圈 | 速度 |
|---:|---|---|---|---:|
| 0 | None | — | 是 | 10 |
| 1 | Talk | `PET_TALKING` | 是 | 1 |
| 2 | Cry | — | 是 | 1 |
| 3 | Angry | — | 是 | 1 |
| 4 | Fear | — | 是 | 1 |
| 5 | Happy | — | 是 | 1 |

### Eat Layer

| 狀態索引 | 狀態 | 動畫／BlendTree 葉節點 | 迴圈 | 速度 |
|---:|---|---|---|---:|
| 0 | Idle | — | 是 | 1 |
| 1 | Eat | — | 是 | 1 |
| 2 | Drink | — | 是 | 1 |

### Locomotion Layer

| 狀態索引 | 狀態 | 動畫／BlendTree 葉節點 | 迴圈 | 速度 |
|---:|---|---|---|---:|
| 0 | Intro | — | 是 | 1 |
| 1 | Idle | — | 是 | 1 |
| 2 | Walk Right | `PET_WALK_RIGHT` | 是 | 1 |
| 3 | Walk Left | `PET_WALK_LEFT` | 是 | 1 |

## 主 Animator 轉場

| 層 | 來源狀態 | 條件 | 目的狀態 | 過場秒數 | 使用離場時間 |
|---|---|---|---|---:|---|
| Base Layer | Intro | Exit Time | Idle | 1 | 是 |
| Base Layer | Intro | If `isDragging` | Drag | 0.25 | 否 |
| Base Layer | Intro | If `isSitting` | Sitting | 0.45 | 否 |
| Base Layer | Drag | IfNot `isDragging` + IfNot `isWindowSit` | Idle | 0.25 | 否 |
| Base Layer | Drag | IfNot `isDragging` + IfNot `isWindowSit` | Dance | 0.25 | 否 |
| Base Layer | Drag | If `isSitting` | Sitting | 0.45 | 否 |
| Base Layer | Drag | If `isWindowSit` | WindowSit | 0.25 | 否 |
| Base Layer | Drag | If `HideRight` | Hide Right | 0.25 | 否 |
| Base Layer | Drag | If `HideLeft` | Hide Left | 0.25 | 否 |
| Base Layer | Dance | IfNot `isDancing` + IfNot `isDragging` | Idle | 1 | 否 |
| Base Layer | Dance | If `isDragging` | Drag | 0.249999 | 否 |
| Base Layer | Dance | If `isSitting` + If `isDancing` | Sitting | 0.25 | 是 |
| Base Layer | Head Pat | IfNot `Headpat` + IfNot `isDragging` | Idle | 1 | 否 |
| Base Layer | Head Pat | If `isDragging` | Drag | 0.25 | 否 |
| Base Layer | Head Pat | If `isSitting` | Sitting | 0.45 | 否 |
| Base Layer | Idle | If `isDancing` + IfNot `isSitting` | Dance | 0.5 | 否 |
| Base Layer | Idle | If `isDragging` | Drag | 0.25 | 否 |
| Base Layer | Idle | IfNot `isDancing` + IfNot `isDragging` + If `isIdle` + If `Headpat` | Head Pat | 0.25 | 否 |
| Base Layer | Idle | If `isSitting` | Sitting | 0.45 | 否 |
| Base Layer | Idle | If `isBigScreen` | Big Screen | 0.5 | 否 |
| Base Layer | Idle | If `IsSleeping` | Sleeping | 1 | 否 |
| Base Layer | Idle | If `isCustomDancing` | Custom Dance | 1 | 否 |
| Base Layer | Idle | IfNot `isDancing` + IfNot `isDragging` + If `isIdle` + If `IntimeRegion` | Intime Region | 0.25 | 否 |
| Base Layer | Sitting | IfNot `isSitting` + If `isDragging` | Drag | 0.3 | 否 |
| Base Layer | Sitting | IfNot `isSitting` | Idle | 0.45 | 否 |
| Base Layer | WindowSit | IfNot `isWindowSit` | Drag | 0.2 | 否 |
| Base Layer | Alarm | IfNot `isBigScreenAlarm` | Big Screen | 0.25 | 否 |
| Base Layer | Big Screen | IfNot `isBigScreen` | Idle | 0.4 | 否 |
| Base Layer | Big Screen | If `isBigScreenSaver` | Screen Saver | 1 | 否 |
| Base Layer | Big Screen | If `isBigScreenAlarm` | Alarm | 0.25 | 否 |
| Base Layer | Screen Saver | IfNot `isBigScreenSaver` | Big Screen | 1 | 否 |
| Base Layer | Screen Saver | Exit Time | Animation 1 | 0.999999 | 是 |
| Base Layer | Animation 1 | Exit Time | Animation 2 | 0.999999 | 是 |
| Base Layer | Animation 1 | IfNot `isBigScreenSaver` | Big Screen | 1 | 否 |
| Base Layer | Animation 2 | Exit Time | Animation 3 | 1 | 是 |
| Base Layer | Animation 2 | IfNot `isBigScreenSaver` | Big Screen | 1 | 否 |
| Base Layer | Animation 3 | Exit Time | Screen Saver | 2 | 是 |
| Base Layer | Animation 3 | IfNot `isBigScreenSaver` | Big Screen | 1 | 否 |
| Base Layer | Sleeping | IfNot `IsSleeping` | Idle | 0.45 | 否 |
| Base Layer | Sleeping | IfNot `IsSleeping` + If `isDragging` | Drag | 0.25 | 是 |
| Base Layer | Custom Dance | IfNot `isCustomDancing` + IfNot `isWaitingForDancing` | Idle | 1 | 否 |
| Base Layer | Custom Dance | If `isWaitingForDancing` | Wait For Dance | 1 | 否 |
| Base Layer | Intime Region | If `isDragging` | Drag | 0.25 | 否 |
| Base Layer | Intime Region | IfNot `IntimeRegion` + IfNot `isDragging` | Idle | 0.5 | 否 |
| Base Layer | Intime Region | If `isSitting` | Sitting | 0.25 | 否 |
| Base Layer | Wait For Dance | IfNot `isWaitingForDancing` | Custom Dance | 2 | 否 |
| Base Layer | Hide Right | IfNot `HideRight` | Drag | 0.25 | 否 |
| Base Layer | Hide Left | IfNot `HideLeft` | Drag | 0.25 | 否 |
| Face Layer | Faceloop | If `FaceLoop` + IfNot `isCustomDancing` | Face Loop | 0.5 | 是 |
| Face Layer | Head Pat | IfNot `Headpat` | Face Loop | 1 | 否 |
| Face Layer | Head Pat | If `isDragging` | Drag | 0.25 | 否 |
| Face Layer | Face Loop | If `FaceLoop` + If `isCustomDancing` | Faceloop | 0.5 | 否 |
| Face Layer | Face Loop | If `Headpat` | Head Pat | 1 | 否 |
| Face Layer | Face Loop | If `isDragging` | Drag | 0.2 | 否 |
| Face Layer | Face Loop | If `IntimeRegion` | Intime Region | 0.2 | 否 |
| Face Layer | Face Loop | If `HairStroke` | Hair Stroke | 0.25 | 否 |
| Face Layer | Drag | IfNot `isDragging` | Face Loop | 0.2 | 否 |
| Face Layer | Intime Region | IfNot `IntimeRegion` | Face Loop | 0.2 | 否 |
| Face Layer | Intime Region | If `isDragging` | Drag | 0.25 | 否 |
| Face Layer | Hair Stroke | IfNot `HairStroke` | Face Loop | 0.25 | 否 |
| Speak Layer | None | If `isTalking` | Talk | 0.05 | 是 |
| Speak Layer | Talk | IfNot `isTalking` | None | 0.05 | 是 |
| Eat Layer | Idle | If `isEating` | Eat | 0.25 | 是 |
| Eat Layer | Idle | If `isDrinking` | Drink | 0.25 | 是 |
| Eat Layer | Eat | IfNot `isEating` | Idle | 0.25 | 是 |
| Eat Layer | Drink | IfNot `isDrinking` | Idle | 0.25 | 是 |
| Locomotion Layer | Intro | Exit Time | Idle | 0.25 | 是 |
| Locomotion Layer | Idle | If `WalkLeft` | Walk Left | 1 | 否 |
| Locomotion Layer | Idle | If `WalkRight` | Walk Right | 1 | 否 |
| Locomotion Layer | Walk Right | IfNot `WalkRight` | Idle | 0.5 | 否 |
| Locomotion Layer | Walk Left | IfNot `WalkLeft` | Idle | 0.5 | 否 |

## 各 BlendTree 結構

### Base Layer / Intro / BlendTree 1

- 節點總數：5
- 根節點：0
- 葉節點：
  - node 2 → clipID 71 → `PET_INTRO`（duration 1）
  - node 4 → clipID 28 → `HUS_IDLE09`（duration 1）

### Base Layer / Drag / BlendTree 1

- 節點總數：5
- 根節點：0
- 葉節點：
  - node 2 → clipID 40 → `PET_DRAGGING`（duration 1）
  - node 4 → clipID 41 → `HUS_DRAG`（duration 1）

### Base Layer / Dance / BlendTree 1

- 節點總數：31
- 根節點：0
- 葉節點：
  - node 2 → clipID 42 → `PET_DANCING`（duration 1）
  - node 3 → clipID 43 → `PET_DANCING_2`（duration 1.66667）
  - node 4 → clipID 44 → `PET_DANCING_3`（duration 1）
  - node 5 → clipID 45 → `PET_DANCING_4`（duration 1）
  - node 6 → clipID 46 → `PET_DANCING_5`（duration 1）
  - node 7 → clipID 47 → `PET_DANCING_6`（duration 1）
  - node 8 → clipID 48 → `PET_DANCING_7`（duration 0.8）
  - node 9 → clipID 49 → `PET_DANCING_8`（duration 0.8）
  - node 10 → clipID 50 → `PET_DANCING_9`（duration 1）
  - node 11 → clipID 51 → `PET_DANCING_10`（duration 1）
  - node 12 → clipID 52 → `PET_DANCING_11`（duration 1）
  - node 13 → clipID 53 → `PET_DANCING_12`（duration 1）
  - node 14 → clipID 54 → `PET_DANCING_13`（duration 1）
  - node 15 → clipID 42 → `PET_DANCING`（duration 1）
  - node 17 → clipID 56 → `HUS_DANCE_01`（duration 1.25）
  - node 18 → clipID 57 → `HUS_DANCE_02`（duration 1.25）
  - node 19 → clipID 58 → `HUS_DANCE_03`（duration 1.25）
  - node 20 → clipID 59 → `HUS_DANCE_04`（duration 1.25）
  - node 21 → clipID 56 → `HUS_DANCE_01`（duration 1.25）
  - node 22 → clipID 57 → `HUS_DANCE_02`（duration 1.25）
  - node 23 → clipID 58 → `HUS_DANCE_03`（duration 1.25）
  - node 24 → clipID 59 → `HUS_DANCE_04`（duration 1.25）
  - node 25 → clipID 56 → `HUS_DANCE_01`（duration 1.25）
  - node 26 → clipID 57 → `HUS_DANCE_02`（duration 1.25）
  - node 27 → clipID 58 → `HUS_DANCE_03`（duration 1.25）
  - node 28 → clipID 59 → `HUS_DANCE_04`（duration 1.25）
  - node 29 → clipID 57 → `HUS_DANCE_02`（duration 1.25）
  - node 30 → clipID 56 → `HUS_DANCE_01`（duration 1.25）

### Base Layer / Head Pat / BlendTree 1

- 節點總數：1
- 根節點：0
- 葉節點：
  - node 0 → clipID 70 → `PET_LAUGHING`（duration 1）

### Base Layer / Idle / BlendTree 1

- 節點總數：43
- 根節點：0
- 葉節點：
  - node 2 → clipID 0 → `PET_IDLE`（duration 2.5）
  - node 3 → clipID 1 → `PET_IDLE_UPDATE2_01`（duration 1）
  - node 4 → clipID 2 → `PET_IDLE_UPDATE2_02`（duration 1）
  - node 5 → clipID 3 → `PET_IDLE_UPDATE2_03`（duration 1）
  - node 6 → clipID 4 → `PET_IDLE_UPDATE2_04`（duration 1）
  - node 7 → clipID 5 → `PET_IDLE_2`（duration 1）
  - node 8 → clipID 6 → `PET_IDLE_14`（duration 2.5）
  - node 9 → clipID 7 → `PET_IDLE_4`（duration 1）
  - node 10 → clipID 8 → `PET_IDLE_3`（duration 1）
  - node 11 → clipID 9 → `PET_IDLE_5`（duration 1）
  - node 12 → clipID 10 → `PET_IDLE_15`（duration 2.5）
  - node 13 → clipID 11 → `PET_IDLE_13`（duration 2.5）
  - node 14 → clipID 12 → `PET_IDLE_9`（duration 1.33333）
  - node 15 → clipID 13 → `PET_IDLE_12`（duration 2.5）
  - node 16 → clipID 14 → `PET_IDLE_6`（duration 1）
  - node 17 → clipID 15 → `PET_IDLE_10`（duration 1.17647）
  - node 18 → clipID 16 → `PET_IDLE_11`（duration 2.5）
  - node 19 → clipID 17 → `PET_IDLE_7`（duration 1）
  - node 20 → clipID 18 → `PET_IDLE_8`（duration 1）
  - node 21 → clipID 0 → `PET_IDLE`（duration 2.5）
  - node 23 → clipID 20 → `HUS_IDLE01`（duration 1.53846）
  - node 24 → clipID 21 → `HUS_IDLE02`（duration 1.53846）
  - node 25 → clipID 22 → `HUS_IDLE03`（duration 1.53846）
  - node 26 → clipID 23 → `HUS_IDLE04`（duration 1.53846）
  - node 27 → clipID 24 → `HUS_IDLE05`（duration 1.53846）
  - node 28 → clipID 25 → `HUS_IDLE06`（duration 1.53846）
  - node 29 → clipID 26 → `HUS_IDLE07`（duration 1.53846）
  - node 30 → clipID 27 → `HUS_IDLE08`（duration 1.53846）
  - node 31 → clipID 28 → `HUS_IDLE09`（duration 1.53846）
  - node 32 → clipID 24 → `HUS_IDLE05`（duration 1.53846）
  - node 33 → clipID 22 → `HUS_IDLE03`（duration 1.53846）
  - node 34 → clipID 25 → `HUS_IDLE06`（duration 1.53846）
  - node 35 → clipID 26 → `HUS_IDLE07`（duration 1.53846）
  - node 36 → clipID 21 → `HUS_IDLE02`（duration 1.53846）
  - node 37 → clipID 23 → `HUS_IDLE04`（duration 1.53846）
  - node 38 → clipID 28 → `HUS_IDLE09`（duration 1.53846）
  - node 39 → clipID 25 → `HUS_IDLE06`（duration 1.53846）
  - node 40 → clipID 27 → `HUS_IDLE08`（duration 1.53846）
  - node 41 → clipID 22 → `HUS_IDLE03`（duration 1.53846）
  - node 42 → clipID 20 → `HUS_IDLE01`（duration 1.53846）

### Base Layer / Sitting / BlendTree 1

- 節點總數：1
- 根節點：0
- 葉節點：
  - node 0 → clipID 73 → `KawaiiMacaronMotion02`（duration 1）

### Base Layer / WindowSit / BlendTree 1

- 節點總數：15
- 根節點：0
- 葉節點：
  - node 1 → clipID 74 → `PET_SIT_05`（duration 1）
  - node 2 → clipID 75 → `PET_SIT_01`（duration 1）
  - node 3 → clipID 76 → `PET_SIT_02`（duration 1）
  - node 4 → clipID 77 → `PET_SIT_03`（duration 1）
  - node 5 → clipID 78 → `sit 1`（duration 1）
  - node 6 → clipID 79 → `PET_SIT_06`（duration 1）
  - node 7 → clipID 77 → `PET_SIT_03`（duration 1）
  - node 8 → clipID 76 → `PET_SIT_02`（duration 1）
  - node 9 → clipID 75 → `PET_SIT_01`（duration 1）
  - node 10 → clipID 78 → `sit 1`（duration 1）
  - node 11 → clipID 84 → `BETA_PET_WINDOW_LAY`（duration 0.5）
  - node 12 → clipID 85 → `PET_SIT_07`（duration 1）
  - node 13 → clipID 84 → `BETA_PET_WINDOW_LAY`（duration 0.5）
  - node 14 → clipID 79 → `PET_SIT_06`（duration 1）

### Base Layer / Alarm / BlendTree 1

- 節點總數：1
- 根節點：0
- 葉節點：
  - node 0 → clipID 88 → `BIG_SCREEN_01`（duration 1）

### Base Layer / Big Screen / BlendTree 1

- 節點總數：8
- 根節點：0
- 葉節點：
  - node 1 → clipID 88 → `BIG_SCREEN_01`（duration 2）
  - node 2 → clipID 90 → `SCREEN_SAVER_01`（duration 2）
  - node 3 → clipID 2 → `PET_IDLE_UPDATE2_02`（duration 1.42857）
  - node 4 → clipID 3 → `PET_IDLE_UPDATE2_03`（duration 1.42857）
  - node 5 → clipID 4 → `PET_IDLE_UPDATE2_04`（duration 1.42857）
  - node 6 → clipID 1 → `PET_IDLE_UPDATE2_01`（duration 1.42857）
  - node 7 → clipID 88 → `BIG_SCREEN_01`（duration 2）

### Base Layer / Screen Saver / BlendTree 1

- 節點總數：1
- 根節點：0
- 葉節點：
  - node 0 → clipID 96 → `SCREEN_SAVER_04`（duration 1）

### Base Layer / Animation 1 / BlendTree 1

- 節點總數：1
- 根節點：0
- 葉節點：
  - node 0 → clipID 90 → `SCREEN_SAVER_01`（duration 1）

### Base Layer / Animation 2 / BlendTree 1

- 節點總數：1
- 根節點：0
- 葉節點：
  - node 0 → clipID 98 → `SCREEN_SAVER_02`（duration 1）

### Base Layer / Animation 3 / BlendTree 1

- 節點總數：1
- 根節點：0
- 葉節點：
  - node 0 → clipID 99 → `SCREEN_SAVER_03`（duration 1）

### Base Layer / Sleeping / BlendTree 1

- 節點總數：1
- 根節點：0
- 葉節點：
  - node 0 → clipID 100 → `PET_SLEEPING`（duration 1）

### Base Layer / Custom Dance / BlendTree 1

- 節點總數：1
- 根節點：0
- 葉節點：
  - node 0 → clipID 101 → `CUSTOM_DANCE`（duration 1）

### Base Layer / Intime Region / BlendTree 1

- 節點總數：1
- 根節點：0
- 葉節點：
  - node 0 → clipID 102 → `PET_POSE_3`（duration 1）

### Base Layer / Wait For Dance / BlendTree 1

- 節點總數：1
- 根節點：0
- 葉節點：
  - node 0 → clipID 13 → `PET_IDLE_12`（duration 1）

### Base Layer / Hide Right / BlendTree 1

- 節點總數：1
- 根節點：0
- 葉節點：
  - node 0 → clipID 104 → `TEST_HIDE_RIGHT`（duration 1）

### Base Layer / Hide Left / BlendTree 1

- 節點總數：1
- 根節點：0
- 葉節點：
  - node 0 → clipID 105 → `TEST_HIDE_LEFT`（duration 1）

### Face Layer / Faceloop / BlendTree 1

- 節點總數：1
- 根節點：0
- 葉節點：
  - node 0 → clipID 106 → `FACE_RESET`（duration 1）

### Face Layer / Head Pat / BlendTree 1

- 節點總數：1
- 根節點：0
- 葉節點：
  - node 0 → clipID 107 → `FACE_SMILE`（duration 1）

### Face Layer / Face Loop / BlendTree 1

- 節點總數：1
- 根節點：0
- 葉節點：
  - node 0 → clipID 108 → `FACE_IDLE_1`（duration 1）

### Face Layer / Drag / BlendTree 1

- 節點總數：1
- 根節點：0
- 葉節點：
  - node 0 → clipID 109 → `FACE_DRAG`（duration 1）

### Face Layer / Intime Region / BlendTree 1

- 節點總數：1
- 根節點：0
- 葉節點：
  - node 0 → clipID 110 → `FACE_INTIME`（duration 1）

### Face Layer / Hair Stroke / BlendTree 1

- 節點總數：1
- 根節點：0
- 葉節點：
  - node 0 → clipID 111 → `FACE_HAIR_STROKE`（duration 1）

### Speak Layer / Talk / BlendTree 1

- 節點總數：1
- 根節點：0
- 葉節點：
  - node 0 → clipID 112 → `PET_TALKING`（duration 1）

### Locomotion Layer / Walk Right / BlendTree 1

- 節點總數：1
- 根節點：0
- 葉節點：
  - node 0 → clipID 113 → `PET_WALK_RIGHT`（duration 1）

### Locomotion Layer / Walk Left / BlendTree 1

- 節點總數：1
- 根節點：0
- 葉節點：
  - node 0 → clipID 114 → `PET_WALK_LEFT`（duration 1）

## 其他 AnimatorController

### DOT_B_anime（pathid 555）

- Base Layer / 0xF4DBDF21: `PBB_anime`

### DanceModExampleController（pathid 556）

- Base Layer / Dance: `CUSTOM_DANCE`
- Base Layer / 0x38B17551: `DANCE_END`

### DanceModExampleController（pathid 556）


### Flowering（pathid 557）

- Base Layer / 0x885368AB: `Flowering`

## 全部 AnimationClip

| PathID | Clip | 主 Animator 使用 | 曲線/資料摘要 |
|---:|---|---|---|
| 485 | `BETA_PET_WINDOW_LAY` | 是 | muscle=27 |
| 430 | `BIG_SCREEN_01` | 是 | muscle=27 |
| 452 | `CUSTOM_DANCE` | 是 | muscle=27 |
| 501 | `CUSTOM_DANCE` | 否 | muscle=27 |
| 502 | `DANCE_END` | 否 | muscle=27 |
| 504 | `DanceModExampleAnimation` | 否 | muscle=27 |
| 425 | `FACE_DRAG` | 是 | muscle=27 |
| 426 | `FACE_HAIR_STROKE` | 是 | muscle=27 |
| 427 | `FACE_IDLE_1` | 是 | muscle=27 |
| 428 | `FACE_INTIME` | 是 | muscle=27 |
| 429 | `FACE_RESET` | 是 | muscle=27 |
| 481 | `FACE_SMILE` | 是 | muscle=27 |
| 505 | `Flowering` | 否 | muscle=27 |
| 435 | `HUS_DANCE_01` | 是 | muscle=27 |
| 436 | `HUS_DANCE_02` | 是 | muscle=27 |
| 437 | `HUS_DANCE_03` | 是 | muscle=27 |
| 438 | `HUS_DANCE_04` | 是 | muscle=27 |
| 453 | `HUS_DRAG` | 是 | muscle=27 |
| 454 | `HUS_IDLE01` | 是 | muscle=27 |
| 455 | `HUS_IDLE02` | 是 | muscle=27 |
| 456 | `HUS_IDLE03` | 是 | muscle=27 |
| 457 | `HUS_IDLE04` | 是 | muscle=27 |
| 458 | `HUS_IDLE05` | 是 | muscle=27 |
| 459 | `HUS_IDLE06` | 是 | muscle=27 |
| 460 | `HUS_IDLE07` | 是 | muscle=27 |
| 461 | `HUS_IDLE08` | 是 | muscle=27 |
| 462 | `HUS_IDLE09` | 是 | muscle=27 |
| 506 | `KawaiiMacaronMotion02` | 是 | muscle=27 |
| 503 | `PBB_anime` | 否 | muscle=27 |
| 439 | `PET_DANCING` | 是 | muscle=27 |
| 440 | `PET_DANCING_10` | 是 | muscle=27 |
| 441 | `PET_DANCING_11` | 是 | muscle=27 |
| 442 | `PET_DANCING_12` | 是 | muscle=27 |
| 443 | `PET_DANCING_13` | 是 | muscle=27 |
| 444 | `PET_DANCING_2` | 是 | muscle=27 |
| 445 | `PET_DANCING_3` | 是 | muscle=27 |
| 446 | `PET_DANCING_4` | 是 | muscle=27 |
| 447 | `PET_DANCING_5` | 是 | muscle=27 |
| 448 | `PET_DANCING_6` | 是 | muscle=27 |
| 449 | `PET_DANCING_7` | 是 | muscle=27 |
| 450 | `PET_DANCING_8` | 是 | muscle=27 |
| 451 | `PET_DANCING_9` | 是 | muscle=27 |
| 482 | `PET_DRAGGING` | 是 | muscle=27 |
| 463 | `PET_IDLE` | 是 | muscle=27 |
| 464 | `PET_IDLE_10` | 是 | muscle=27 |
| 465 | `PET_IDLE_11` | 是 | muscle=27 |
| 466 | `PET_IDLE_12` | 是 | muscle=27 |
| 467 | `PET_IDLE_13` | 是 | muscle=27 |
| 468 | `PET_IDLE_14` | 是 | muscle=27 |
| 469 | `PET_IDLE_15` | 是 | muscle=27 |
| 470 | `PET_IDLE_2` | 是 | muscle=27 |
| 471 | `PET_IDLE_3` | 是 | muscle=27 |
| 472 | `PET_IDLE_4` | 是 | muscle=27 |
| 473 | `PET_IDLE_5` | 是 | muscle=27 |
| 474 | `PET_IDLE_6` | 是 | muscle=27 |
| 475 | `PET_IDLE_7` | 是 | muscle=27 |
| 476 | `PET_IDLE_8` | 是 | muscle=27 |
| 477 | `PET_IDLE_9` | 是 | muscle=27 |
| 496 | `PET_IDLE_UPDATE2_01` | 是 | muscle=27 |
| 497 | `PET_IDLE_UPDATE2_02` | 是 | muscle=27 |
| 498 | `PET_IDLE_UPDATE2_03` | 是 | muscle=27 |
| 499 | `PET_IDLE_UPDATE2_04` | 是 | muscle=27 |
| 478 | `PET_INTRO` | 是 | muscle=27 |
| 483 | `PET_LAUGHING` | 是 | muscle=27 |
| 484 | `PET_POSE_3` | 是 | muscle=27 |
| 486 | `PET_SIT_01` | 是 | muscle=27 |
| 487 | `PET_SIT_02` | 是 | muscle=27 |
| 488 | `PET_SIT_03` | 是 | muscle=27 |
| 489 | `PET_SIT_05` | 是 | muscle=27 |
| 490 | `PET_SIT_06` | 是 | muscle=27 |
| 491 | `PET_SIT_07` | 是 | muscle=27 |
| 495 | `PET_SLEEPING` | 是 | muscle=27 |
| 500 | `PET_TALKING` | 是 | muscle=27 |
| 479 | `PET_WALK_LEFT` | 是 | muscle=27 |
| 480 | `PET_WALK_RIGHT` | 是 | muscle=27 |
| 431 | `SCREEN_SAVER_01` | 是 | muscle=27 |
| 432 | `SCREEN_SAVER_02` | 是 | muscle=27 |
| 433 | `SCREEN_SAVER_03` | 是 | muscle=27 |
| 434 | `SCREEN_SAVER_04` | 是 | muscle=27 |
| 492 | `TEST_HIDE_LEFT` | 是 | muscle=27 |
| 493 | `TEST_HIDE_RIGHT` | 是 | muscle=27 |
| 494 | `sit 1` | 是 | muscle=27 |

## 未被任何 Animator 狀態引用的 Clip

- `DanceModExampleAnimation`（pathid 504）
