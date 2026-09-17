---
name: comsol-mcp
description: Drive COMSOL Multiphysics 6.4 on this machine through the opencode COMSOL MCP server (wjc9011/COMSOL_Multiphysics_MCP, local fork yd7148). Covers the required launcher startup, the verified tool sequence (model -> component -> geometry -> physics -> mesh -> study -> solve -> evaluate), the client-API gotchas discovered in testing, and the working external-engine recipes (comsolmphserver client-server Eval/solnum evaluation, comsolbatch solving, recovery-file disk management) for models the MCP path cannot load. Use when asked to "用 COMSOL 建模", "跑 COMSOL 仿真", "使用 comsol MCP", or to operate COMSOL via opencode MCP tools.
license: MIT
compatibility: opencode
metadata:
  audience: opencode agents
  workflow: comsol-mcp-operation
  languages: zh-TW
---

# comsol-mcp — 透過 opencode 操作 COMSOL 6.4

This skill documents how to **operate COMSOL Multiphysics 6.4** on this machine
through the COMSOL MCP server using opencode's `comsol_*` tools. It assumes the
MCP server was already installed, configured, and verified end-to-end.

Do **not** use this skill to analyze an existing `.mph` file — that is
`comsol-analyzer`.

## Environment (this machine)

| Item | Value |
|------|-------|
| COMSOL version | 6.4 (`C:\Program Files\COMSOL\COMSOL64\Multiphysics_copy1` — original `Multiphysics` dir unregistered; mph registry resolves to `..._copy1`) |
| Python venv | `C:\Users\admin\Projects\COMSOL_Multiphysics_MCP\.venv` (mcp 1.30.0, mph 1.4.0, jpype1 1.7.1) |
| Server repo | `C:\Users\admin\Projects\COMSOL_Multiphysics_MCP` (upstream `wjc9011/COMSOL_Multiphysics_MCP`, core deps only; chromadb/torch not installed) |
| Startup | `python -m src.server` (upstream pre-starts the JVM before `mcp.run()`) |
| opencode config | `C:\Users\admin\.config\opencode\opencode.jsonc` → `comsol` entry, env `PYTHONPATH=<repo>`, `COMSOL_MCP_CORES=4` |
| Git remotes | none (downloaded via API, no git on this machine); fork `yd7148/...` is gone (404) |
| Hardware | 2 logical cores / ~34 GB RAM VM; C: is small (keep ≥ ~9 GB free), E: has ample space |
| External solver | `comsolmphserver` (`...\Multiphysics_copy1\bin\win64\comsolmphserver.exe`, port 2036) and `comsolbatch` are the two engines that actually load/solve 6.4 models on this box |
| OpenCode MCP prefix | server tools are exposed as `comsol_comsol_start`, `comsol_model_create`, `comsol_physics_add_electrostatics`, `comsol_study_solve`, `comsol_results_global_evaluate`, … |

## Critical startup rule

Installation on this machine uses the **upstream** repo, which embeds the
pre-start in `src/server.py`: `main()` calls `session_manager.start()` (JVM +
COMSOL client) **before** `mcp.run()`, then starts the stdio transport.
Starting the JVM *after* `mcp.run()` has opened stdin deadlocks indefinitely
(observed: >10 min, CPU ~0) — do not reorder this. Configured automatically in
`opencode.jsonc` (command `-m src.server`, envs `PYTHONPATH=<repo>` and
`COMSOL_MCP_CORES=4`). If `comsol_comsol_start` hangs, first ensure opencode
was restarted after installing the server.

## Verified end-to-end sequence

Use `comsol_comsol_start` (or `comsol_comsol_status`) first, then:

1. `comsol_model_create(name)` — new model.
2. `comsol_model_create_component(component_name="comp1", space_dimension=3)` — 3D component.
3. `comsol_geometry_create(geometry_name="geom1", space_dimension=3)` — 3D geometry sequence.
4. `comsol_geometry_add_block(size=[0.1,0.05,0.02])` — block feature (fixed `_next_feature_name` naming bug upstream).
5. `comsol_geometry_build()` — build geometry sequence.
6. `comsol_physics_add_electrostatics()` (or solid / laminar flow wrappers).
7. `comsol_mesh_create()` — auto-creates `mesh1`.
8. `comsol_study_create(study_type="Stationary")` then `comsol_study_solve()`.
9. `comsol_results_global_evaluate(expression="es.normE", unit="V/m")`.

Optional boundary conditions between 6 and 7:
`comsol_physics_configure_boundary(physics_name="es", boundary_condition="ElectricPotential", boundary_selection=[2], properties={"V0": "5[V]"})` and `Ground` on another face.

Verified smoke test: 0.1×0.05×0.02 m block, 5 V on one face + ground on the
opposite → `es.normE` ≈ 343 V/m, solve ~3 s.

## Client-API gotchas (mph 1.4 + COMSOL 6.4)

1. **Physics must receive the geometry tag.** `comp.physics().create(tag, type)`
   creates an interface with no space dimension → fails ("不支援空間維度: 0D").
   Correct: `comp.physics().create("es", "Electrostatics", "geom1")`. The repo
   now wraps this in `_create_physics()` in `src/tools/physics.py`.
2. **Study steps need full type names.** `study.create("step1", "Stationary")`
   works; short id `"stat"` fails ("操作不能在此背景中建立"). Repo `study_create`
   tries full names then falls back (`src/tools/study.py`).
3. **Model components**: `model_create_component` tries
   `component().create(tag, True, dim)` and falls back to
   `create(tag, True)` when the overload is unavailable.
4. **`HeatTransfer` currently fails** on this machine — ASHRAE/sqlite reference
   data initialization throws inside `com.comsol.heat.util.ashrae`
   ("物理介面初始化失敗"). Not related to the geometry argument. Verified working
   physics: `Electrostatics`, `SolidMechanics`, `LaminarFlow`.
   ⚠️ Loading ANY existing model that *contains* HeatTransfer through mph
   standalone / MCP `comsol_model_load` fails the same way
   (`Failed_to_initialize_physics_interface`) — use the external
   `comsolmphserver` + `mph.Client` (or `comsolbatch`) instead (see sections below).
5. **Known repo bugs (unfixed, non-blocking)**: `comsol_geometry_get_boundaries`
   raises `'ComponentGeomListClient' object is not subscriptable`.
6. **`comsol_comsol_start` returns instantly** ("Cleared existing session and
   ready.") because the client is pre-started; it also clears any current model.

## When to be careful

- Solving can take a long time for large meshes; prefer `comsol_study_solve(wait=True, timeout=<s>)` and start models with coarse meshes.
- The MCP server holds several CPU cores while running (idle client still holds JVM); disconnect when done to release them.

---

# 外部引擎：comsolmphserver（client-server）與 comsolbatch（實測 2026-09-17）

The MCP/standalone mph path **cannot load this coil model** (below). The reliable
engines on this machine are the **external `comsolmphserver`** (client-server)
and **`comsolbatch`**. These recipes were verified on
`New2-FCFC-Coil-versionV1.mph` and are the recommended path for any real 6.4 work
here.

## MPH 本機載入／MCP `comsol_model_load` 是壞的

- Loading any model containing `HeatTransfer` (and this coil model does) through
  mph standalone **or** the MCP server throws
  `FlException('Failed_to_initialize_physics_interface')` (物理介面初始化失敗,
  same ASHRAE/sqlite class of failure as gotcha #4; the standalone JVM lacks the
  server's license/module context). **Workaround: never load via MCP/standalone
  mph for such models.** Use `mph.Client` → external server, or `comsolbatch`.

## 起動外部伺服器（注意：不可 pipe 給 Out-Null）

```powershell
$env:TMP="E:\ComsolTemp"; $env:TEMP="E:\ComsolTemp"
Start-Process -FilePath "C:\Program Files\COMSOL\COMSOL64\Multiphysics_copy1\bin\win64\comsolmphserver.exe" `
  -ArgumentList "-silent","-server","-port","2036","-multi","on","-jvmargs","-Xmx24g" -WindowStyle Hidden
```
- `Start-Process` is required — a foreground `& ...exe | Out-Null` blocks forever.
- Verify port: poll `TcpClient.Connect("localhost",2036)`.
- Connect: `client = mph.Client(port=2036, host="localhost")`; `model = client.load(path)`.
- `model.java.save(out_path)` works (engine-side save, 4.6 GB model ≈ 40 s).
- **Patched JVM heap for the client**: `jpype.startJVM` must receive
  `-Xmx24g`, else`NumericalFeature`/load runs out of memory:
  ```python
  _orig = jpype.startJVM
  jpype.startJVM = lambda *a, **k: _orig(*(a + ("-Xmx24g",)), **k) if not any("-Xmx" in str(x) for x in a) else _orig(*a, **k)
  ```

## 評估（Eval）配方 — mph `evaluate()` 會 OOM

- `model.evaluate("T", dataset=..., inner=[...])` **always materializes ALL inner
  times first** (mph `model.py` ~line 602) → `java.lang.OutOfMemoryError:
  記憶體不足` even on 24 GB heaps for 814-step solution. **Do not use it on stored
  transient solutions**.
- Working recipe (single time slice, ~80 k points ≈ 1.1 s/slice):
  ```python
  ev = model.java.result().numerical().create("neval1", "Eval")
  ev.set("data", ds_tag)                       # dataset TAG, see below
  ev.set("expr", [["T"]])                      # axisym: use r/z, NOT x/y
  ev.set("solnum", jpype.JArray(jpype.JInt)([int(solnum)]))   # int[] REQUIRED
  ev.run(); d = np.asarray(ev.getReal(), float)               # (npts,) rows
  ```
- `set("solnum", [int])` (Python list) → jpype “Ambiguous overloads” TypeError;
  must pass an explicit `jpype.JArray(jpype.JInt)([...])`.
- **Dataset is resolved by LABEL, not tag**: `model/'datasets'/'dset5'` raises
  `ValueError('Dataset "dset5" does not exist.')`. Iterate
  `for c in model/'datasets': if str(c.java.tag()).startswith('dset')`.
- Numerical feature types `Max`/`Min`/`Avg` **cannot be created** —
  `Operation_cannot_be_created_in_this_context` — in the client *and* in
  comsolbatch. Only `Eval`/`EvalGlobal` are creatable. Compute stats in numpy.
- Image/plot export via `result().export().create('expim1','Image')` also fails
  (`缺少屬性 plot` / context restriction). Render matplotlib from exported
  `(r,z,T)` point data instead.
- `sol('sol1').getSolutioninfo().getSolnum(1, False)` gives 1-based inner indices;
  `getPVals()` gives time values. After `clearSolutionData()` the index list may
  remain non-empty and stale solnum values can be out-of-range — filter to `<= n`.

## 新增結果繪圖（1D 繪圖群組 + Global 曲線）— 實測配方

Verifier (built 2026-09-17, `New2-FCFC-Coil-versionV1_solved_r5.mph`): a
`1D 繪圖群組` with a Global curve **can be created headlessly** via the client:

```python
JStr = jpype.JArray(jpype.JString)
pg = model.java.result().create('pg60', 'PlotGroup1D')      # ResultClient.create works (no .plot() attr!)
pg.label("1D 繪圖群組 60")                                    # Traditional-Chinese ok
gl = pg.create('globP', 'Global')
gl.set('expr', JStr(['mf.PCoil_2', '']))                    # expr needs JArray(String), trailing ''
gl.set('data', 'dset5')                                      # solution dataset tag
gl.set('descr', JStr(['功率 Power (W)']))
expr_readback = pg.feature('globP').getString('expr')        # getString works; getStringArray overload often fails
```

- `ResultsClient` has `create`/`get`/`tags` but **no `plot()`** — create plot groups
  straight on `model.java.result()` with type `'PlotGroup1D'` (default label becomes
  「1D 繪圖群組 N」).
- Global/eval results: `EvalGlobal.getReal()` returns **`double[][]`** (one row per
  expression) — convert 2-D, not 1-D. `mf.PCoil2`/`comp1.mf.coil2.ICoil` evaluate
  fine for a current-driven coil; a `...VCoil` expression is "undefined" (voltage is
  not a stored output of a current-excited coil) — use power instead of V×I.
- **Saving over the loaded source fails** (`IOException: 檔案被另一個程式鎖定`,
  engine holds its input). Save to a temp path, then stop the server (or wait for
  unlock) and copy over the target file.

## 整批求解（comsolbatch）

- Solve a copy (batch **overwrites the input file** unless you run with
  `-outputfile`):
  ```powershell
  & "...\bin\win64\comsolbatch.exe" -inputfile X.mph -study std4 `
      -outputfile out.mph -np 2 2>&1 | Tee-Object solve_log.txt
  ```
- Stdout is Big5-garbled under CP950 → **capture to a file** and grep ASCII
  markers/`EXIT=`; treat `EXIT=0` as “completed” not necessarily “converged”.
- `-batch <file>.java` is invalid (「輸入名稱未定義」) — compile to `.class`
  with the bundled javac (`<root>\java\win64\jre\bin\javac.exe`,
  `-classpath plugins\*;apiplugins\*`) and pass the `.class` via `-inputfile`;
  `main(String[])` receives **null args** (guard `args != null`).
- Fresh-solver regeneration after deleting `sol1` **fails** with
  「有與分離式求解器組合的變數類型不匹配」(segregated variable/solver type
  mismatch) — the 6.3 solver config cannot be rebuilt by 6.4. **Do not delete
  sol1.** To re-solve from t=0 use:
  ```python
  model.java.sol('sol1').feature('t1').set('tlist', 'range(0,3,4872)')
  model.java.sol('sol1').clearSolutionData()   # empty data, KEEP config
  ```
- **Mesh regeneration can silently break point probes**: add a `Size` feature and
  let batch remesh → solve aborts with
  「來源網格區沒有被產生 - 輸出: geom1 - 點: 6 - 運行位置: comp1.point1_operator1」
  (the probe `T_meas`/「控溫點」 loses its point-6 mesh vertex even though geom1
  has 193 vertices). In the client `mesh1.run()` is a no-op (returns 0 elems).
  So **mesh refinement is NOT currently possible headlessly**; reuse the stored
  mesh (`getNumElem()`/`getNumVertex()` verify it survives the round-trip).

## 磁碟：復原檔會灌爆 C:

- **every** server session writes a multi-GB recovery under
  `C:\Users\admin\.comsol\v64\recoveries\MPHRecovery*.mph\model.mph`
  **regardless of TMP/TEMP**. Mitigation already applied:
  - moved all recoveries to `E:\ComsolTemp\recoveries`;
  - replaced `C:\Users\admin\.comsol\v64\recoveries` with a directory junction
    (`mklink /J` → `E:\ComsolTemp\recoveries`);
  - start servers with `TMP/TEMP=E:\ComsolTemp`.
  Keep C: ≥ ~9 GB free or even loading models fails (「沒有足夠的磁碟空間」).

## 已知限制（此模型）

- Solving `研究 4` (Frequency-Transient, mf+ht+rad) in 6.4 reproducibly diverges:
  `comp1.rad.Ju band` non-finite on Boundaries **24-25, 29-31, 68** (at ~754 s with
  3 s steps; at the final step with 6 s steps). Solve log also warns about
  `comp1.rad.Fbacksided_band` / `Fbacksideu_band` (backside/facing settings) —
  the most likely root cause, unrelated to mesh size. Original full solution
  (814 steps to 4876.95 s) was produced under COMSOL 6.x < 6.4.
- 6.3solved file now on disk exposes 84.7% NaN evaluation points (mesh/data
  mismatch from earlier partial re-saves) and a corrupted final irregular step.

## Model persistence

- Save: `comsol_model_save(file_path=<abs path>.mph)` or
  `comsol_model_save_version(description=...)` (writes timestamped copies under
  `./comsol_models/{name}/`).
- Use `comsol_model_save` before closing a session if the user wants the model preserved.
- `comsol_comsol_disconnect` destroys the client and clears all models.
- Client-server saves also via `model.java.save(<path>)`.

## Troubleshooting

- `comsol_comsol_start` hangs → check opencode.jsonc uses `-m launcher`, restart opencode.
- Model disappears after `comsol_comsol_start` → expected (it clears the session); create a fresh model.
- Physics add fails with any dimension error → make sure a geometry was created **and built** first.
- `es.normE` returns 0 → no boundary conditions applied; add a potential + ground and re-solve.
- Unreadable Chinese error text in console → set `[Console]::OutputEncoding = UTF8`, `$env:PYTHONIOENCODING = "utf-8"`, or use the `msg`/`getMessages()` on the Japanese FlException.

## When to be careful

- Solving can take a long time for large meshes; prefer `comsol_study_solve(wait=True, timeout=<s>)` and start models with coarse meshes.
- The MCP server holds several CPU cores while running (idle client still holds JVM); disconnect when done to release them.