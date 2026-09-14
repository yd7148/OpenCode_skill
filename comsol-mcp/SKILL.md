---
name: comsol-mcp
description: Drive COMSOL Multiphysics 6.4 on this machine through the opencode COMSOL MCP server (wjc9011/COMSOL_Multiphysics_MCP, local fork yd7148). Covers the required launcher startup, the verified tool sequence (model -> component -> geometry -> physics -> mesh -> study -> solve -> evaluate), and the client-API gotchas discovered in testing (physics needs a geometry tag, full study step names, HeatTransfer ASHRAE limitation). Use when asked to "用 COMSOL 建模", "跑 COMSOL 仿真", "使用 comsol MCP", or to operate COMSOL via opencode MCP tools.
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
| COMSOL version | 6.4 (`C:\Program Files\COMSOL\COMSOL64\Multiphysics`) |
| Python venv | `D:\80-Opnecode\workspace\_maidate_work\venv` (mcp 1.30.0, mph 1.4.0, jpype1 1.7.1) |
| Server repo | `D:\80-Opnecode\Projects\COMSOL_Multiphysics_MCP` |
| Startup | **must** be `python -m launcher` (NOT `-m src.server`) |
| opencode config | `C:\Users\N000149839\.config\opencode\opencode.jsonc` → `comsol` entry, env `COMSOL_MCP_CORES=4` |
| Git remotes | `origin` = `https://github.com/yd7148/COMSOL_Multiphysics_MCP.git` (private fork); `upstream` = `wjc9011/COMSOL_Multiphysics_MCP.git` |
| OpenCode MCP prefix | server tools are exposed as `comsol_comsol_start`, `comsol_model_create`, `comsol_physics_add_electrostatics`, `comsol_study_solve`, `comsol_results_global_evaluate`, … |

## Critical startup rule

**Never start the server as `python -m src.server`.** JPype's in-process JVM
startup hangs indefinitely when anyio/FastMCP worker threads are already
running when `jpype.startJVM` is called (observed: >10 min, CPU ~0).

`launcher.py` (repo root) pre-starts the COMSOL client on the main thread
before `mcp.run()`, making startup ~instant. Configured automatically in
`opencode.jsonc` (command `-m launcher`, env `COMSOL_MCP_CORES=4`). If the
user reports `comsol_comsol_start` hanging, first ensure the config uses
launcher and that opencode was restarted.

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
5. **Known repo bugs (unfixed, non-blocking)**: `comsol_geometry_get_boundaries`
   raises `'ComponentGeomListClient' object is not subscriptable`.
6. **`comsol_comsol_start` returns instantly** ("Cleared existing session and
   ready.") because the client is pre-started; it also clears any current model.

## Model persistence

- Save: `comsol_model_save(file_path=<abs path>.mph)` or
  `comsol_model_save_version(description=...)` (writes timestamped copies under
  `./comsol_models/{name}/`).
- Use `comsol_model_save` before closing a session if the user wants the model preserved.
- `comsol_comsol_disconnect` destroys the client and clears all models.

## Troubleshooting

- `comsol_comsol_start` hangs → check opencode.jsonc uses `-m launcher`, restart opencode.
- Model disappears after `comsol_comsol_start` → expected (it clears the session); create a fresh model.
- Physics add fails with any dimension error → make sure a geometry was created **and built** first.
- `es.normE` returns 0 → no boundary conditions applied; add a potential + ground and re-solve.
- Unreadable Chinese error text in console → set `[Console]::OutputEncoding = UTF8`, `$env:PYTHONIOENCODING = "utf-8"`, or use the `msg`/`getMessages()` on the Japanese FlException.

## When to be careful

- Solving can take a long time for large meshes; prefer `comsol_study_solve(wait=True, timeout=<s>)` and start models with coarse meshes.
- The MCP server holds several CPU cores while running (idle client still holds JVM); disconnect when done to release them.