---
name: comsol-analyzer
description: Analyze COMSOL Multiphysics .mph model files by extracting and parsing their internal XML/JSON structure. Produces a detailed Traditional Chinese markdown report covering model metadata, parameters, physics interfaces, geometry, materials, studies, and mesh. Use when asked to "分析 COMSOL 模型", "說明 .mph 檔案", "COMSOL 模型結構", "comsol model analysis", or to examine a .mph file.
license: MIT
compatibility: opencode
metadata:
  audience: opencode agents
  workflow: comsol-analysis
  languages: zh-TW
---

# comsol-analyzer — COMSOL .mph 模型檔案分析

Analyze a COMSOL Multiphysics `.mph` model file and produce a detailed Traditional Chinese
markdown documentation report. The `.mph` file is a ZIP archive containing XML + binary data;
this skill guides extraction and parsing without requiring COMSOL installed.

## When to use
- User says 分析 COMSOL 模型 / 說明 .mph 檔案 / COMSOL 模型結構 / comsol model analysis, or hands you a `.mph` file to document.
- Also use when the user asks about the physics, geometry, materials, or studies defined in a COMSOL model.

## Prerequisites
- **No COMSOL installation required** — the `.mph` file is a standard ZIP archive.
- **無額外 Python 套件（無依賴）** — 只需標準程式庫 `zipfile` / `xml.etree` / `json`，macOS 與 Windows 內建 Python 3 皆可用。
- Windows: PowerShell 5.1（內建）。macOS: 任一 Python 3 + `unzip`（內建）。
- Working temp directory: 任一支暫存目錄（如 `/var/folders/.../tmp` 或 `C:\Users\...\AppData\Local\Temp\opencode`）

## .mph File Structure

A COMSOL `.mph` file is a ZIP archive containing:

| File | Content | Readable? |
|---|---|---|
| `fileversion` | COMSOL version string (e.g. `2092:COMSOL 6.4.0.429`) | Yes (text) |
| `model.xml` | Minimal XMI model wrapper | Yes (XML) |
| `modelinfo.xml` | Model metadata: version, physics, license, geometry info | Yes (XML) |
| `dmodel.xml` | **Core model definition** — all physics, geometry, materials, studies, results | Yes (XML, can be >5 MB) |
| `smodel.json` | Structured model tree (JSON) — useful for quick parameter/setting lookup | Yes (JSON) |
| `guimodel.xml` | GUI state (current view, selected nodes) | Yes (XML) |
| `auxiliarydatainfo.json` | Auxiliary data file references | Yes (JSON) |
| `usedlicenses.txt` | List of required license modules | Yes (text) |
| `geometry*.mphbin` | Binary geometry data (Parasolid/CAD kernel) | Binary |
| `solution*.mphbin` | Binary solution data | Binary |
| `mesh*.mphbin` | Binary mesh data | Binary |
| `geommanager*.mphbin` | Geometry manager data | Binary |
| `tabledata*.mphbin` | Table data for parametric sweeps | Binary |
| `fileids.xml` | Internal file ID mappings | Yes (XML) |
| `clusterignore.xml` | Cluster computation ignore list | Yes (XML) |

## Pipeline (follow in order)

### Step 1. Copy and rename to .zip
```powershell
$src = "<path_to_model>.mph"
$tmpZip = "C:\Users\N00014~1\AppData\Local\Temp\opencode\comsol_temp.zip"
$extractDir = "C:\Users\N00014~1\AppData\Local\Temp\opencode\comsol_extract"
Copy-Item $src $tmpZip -Force
Expand-Archive -Path $tmpZip -DestinationPath $extractDir -Force
```

### Step 2. Read metadata files (parallel reads)
Read these files simultaneously for quick overview:
- `fileversion` — COMSOL version
- `modelinfo.xml` — model type, physics list, license info, computation history
- `usedlicenses.txt` — required modules
- `guimodel.xml` — GUI state (current study, current view)

### Step 3. Parse `dmodel.xml` for full model details

The `dmodel.xml` is the core file (often 5–60 MB). Parse it section by section:

#### 3a. Global Parameters
Search for `<ModelParam tag="param">` and extract `<expressions>` elements:
- Parameter names, expressions, values
- Parameter groups and descriptions

#### 3b. Physics Interfaces
Search for `<Physics op="...">` tags. Each physics interface has:
- `op` attribute: the physics type (e.g. `InductionCurrents`, `HeatTransferInSolidsAndFluids`, `LaminarFlow`)
- `tag` and `name`: identifier and display name
- `PhysicsFeatureList`: individual features (boundary conditions, sources, material models)
- Key features to look for:
  - **Coil definitions** (`op="Coil"`): coil type (Circular/Numeric),匝數 N, current source, wire properties
  - **Material models** (`op="AmperesLawFluid"`, `op="SolidHeatTransferModel"`): constitutive relations
  - **Boundary conditions**: `NoFlux`, `DiffuseSurface`, `InitialValues`, etc.
  - **Multiphysics couplings**: `<MultiphysicsCoupling op="...">` — electromagnetic heating, radiation coupling

#### 3c. Geometry
Search for `<GeomSequence tag="geom1">`:
- Geometry kernel type (`geomrep`: `cadps` = Parasolid)
- Units (`lengthUnit`, `angularUnit`)
- Bounding box (`boundingBox`)
- Entity counts (`numEntities`: vertices, edges, faces, domains)
- Geometry features (`<GeomFeature op="...">`):
  - `Polygon`, `Circle` — 2D sketch primitives
  - `Revolve`, `Extrude` — 3D operations
  - `Difference`, `Union`, `Intersection` — Boolean operations
  - `Array` — pattern阵列
  - `Extract`, `PartitionEdges` — post-processing
  - `Finalize` — formation of one body
  - `RemoveDetails` — geometry simplification
- Work planes (`<WorkPlaneFeature op="WorkPlane">`): plane orientation (xy/xz/yz)

#### 3d. Materials
Search for `<Material op="Common" tag="mat...">`:
- Material name and identifier
- Property values (thermal conductivity, density, heat capacity, electrical conductivity, etc.)
- Temperature-dependent properties (look for interpolation table data)

#### 3e. Studies
Search for `<StudyList>` → `<Study>`:
- Study types: `CoilCurrentCalculation` (CCC), `Frequency`, `Transient`, `Stationary`, `FrequencyTransient`
- Study parameters: frequency, time range, parametric sweep
- Computation history: time, date, COMSOL version used

#### 3f. Mesh
Search for `<MeshSequence>` or `<mesh>`:
- Mesh type (Free, Swept, Mapped, Tet)
- Element size settings
- Element counts

#### 3g. Results/Plots
Search for `<ResultFeature>`:
- Plot groups (`<PlotGroup>`)
- Surface plots, contour plots, 3D plots
- Data expressions being plotted

### Step 4. Parse `smodel.json` for quick lookup
The JSON file provides a structured tree that's easier to parse than XML for:
- Parameter values (with scalarReal/scalarImag)
- Material names and property values
- Study configuration summaries

### Step 5. Generate Markdown Report

Create a detailed markdown file in the project directory with these sections:

1. **基本資訊** — file name, COMSOL version, model title, units, computation history
2. **所需授權模組** — license modules table
3. **模型概述** — one-paragraph summary of what the model simulates
4. **物理場（Physics Interfaces）** — table of all physics with tags, types, descriptions
5. **多物理耦合** — multiphysics coupling features
6. **線圈定義** (if applicable) — coil types, turns, current sources, wire properties
7. **模型參數** — global parameters table with values and descriptions
8. **3D 幾何** — geometry construction sequence, dimensions, operations
9. **材料** — materials table with names and key properties
10. **研究（Studies）** — study types, settings, computation history
11. **網格（Mesh）** — mesh settings summary
12. **數值求解器觀察** — solver configuration notes
13. **模型檔案結構** — internal .mph file listing with sizes
14. **總結** — comprehensive summary

### Step 6. Cleanup
```powershell
Remove-Item -Path $extractDir -Recurse -Force
Remove-Item -Path $tmpZip -Force
```

## Key XML Patterns Reference

| What to find | XML pattern |
|---|---|
| Physics interface | `<Physics op="..." tag="..." name="...">` |
| Coil definition | `<PhysicsFeature op="Coil" tag="coilN">` |
| Coil type | `<param param="CoilType" value="...">` |
| Coil turns | `<param param="N" value="...">` |
| Coil current | `<param param="ICoil" value="...">` |
| Material | `<Material op="Common" tag="matN" name="...">` |
| Study | `<Study tag="stdN" name="...">` |
| Study type | `<StudyFeature op="...">` (CCC/Frequency/Transient/Stationary) |
| Frequency | `<propertyValue name="p:freq" value="...">` |
| Time range | `<propertyValue name="p:tlist" value="...">` |
| Geometry features | `<GeomFeature op="..." tag="..." name="...">` |
| Bounding box | `<boundingBox>minX,maxX,minY,maxY,minZ,maxZ</boundingBox>` |
| Entity count | `<numEntities>vertices,edges,faces,domains</numEntities>` |
| Multiphysics coupling | `<MultiphysicsCoupling op="..." tag="..." name="...">` |
| Global equations (PID) | `<Physics op="GlobalEquations">` with `<PhysicsFeature op="GlobalEquations">` |
| Rotating frame | `<PhysicsFeature op="RotatingFrameFD">` |

## Environment gotchas
- **`.mph` is a ZIP file** — must rename to `.zip` or use `Copy-Item` + `Expand-Archive` (PowerShell won't expand files with `.mph` extension directly).
- **`dmodel.xml` can be very large** (5–60 MB) — read in chunks using `offset`/`limit` parameters.
- **XML contains Chinese characters** encoded as `&#xHEX;` — decode with `[System.Web.HttpUtility]::HtmlDecode()` or treat as-is for documentation.
- **Binary `.mphbin` files** cannot be read as text — skip them, they contain geometry/solution/mesh binary data.
- **Cleanup temp files** after analysis to avoid disk space issues.

## Deliverables checklist
- [ ] `<model_name>-模型詳細說明.md` in the project directory
- [ ] Temp files cleaned up
