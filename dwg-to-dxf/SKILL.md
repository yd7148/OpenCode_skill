---
name: dwg-to-dxf
description: Convert AutoCAD DWG files to DXF format using ODA File Converter, then perform detailed geometric and metadata analysis using Python ezdxf library. Produces a comprehensive Traditional Chinese markdown report covering layers, entities, dimensions, geometry, blocks, hatches, and text content. Use when asked to "轉換 DWG", "DWG 轉 DXF", "分析 DWG 檔案", "dwg to dxf conversion", "DWG 幾何分析", or to examine a .dwg/.dxf engineering drawing file.
license: MIT
compatibility: opencode
metadata:
  audience: opencode agents
  workflow: dwg-conversion-analysis
  languages: zh-TW
---

# dwg-to-dxf — DWG 轉 DXF 與詳細解析

Convert an AutoCAD `.dwg` file to `.dxf` format using ODA File Converter, then perform
comprehensive geometric and metadata analysis using Python `ezdxf` library. Produces a
detailed Traditional Chinese markdown documentation report.

## When to use
- User says 轉換 DWG / DWG 轉 DXF / 分析 DWG 檔案 / dwg to dxf conversion / DWG 幾何分析, or hands you a `.dwg` file to analyze.
- Also use when the user asks about layers, dimensions, geometry, blocks, or any content in an AutoCAD drawing file.

## Prerequisites
- **ODA File Converter** — installed at `C:\Program Files\ODA\ODAFileConverter 27.1.0\ODAFileConverter.exe`
  - If not installed, download from: https://www.opendesign.com/guestfiles/oda_file_converter
  - Windows MSI: `ODAFileConverter_QT6_vc16_amd64dll_27.1.msi`
  - Install silently: `msiexec /i "<path>.msi" /qn`
- **Python ezdxf** — `py -3 -m pip install ezdxf`
- **PowerShell 5.1** (built-in on Windows)
- Working temp directory: `C:\Users\N00014~1\AppData\Local\Temp\opencode`

## Pipeline (follow in order)

### Step 1. Verify ODA File Converter Installation

Check if ODA File Converter is installed:
```powershell
$odaPath = "C:\Program Files\ODA\ODAFileConverter 27.1.0\ODAFileConverter.exe"
if (Test-Path $odaPath) { Write-Host "ODA installed" } else { Write-Host "Need install" }
```

If not installed, download and install:
```powershell
$msiUrl = "https://www.opendesign.com/guestfiles/get?filename=ODAFileConverter_QT6_vc16_amd64dll_27.1.msi"
$msiPath = "C:\Users\N00014~1\AppData\Local\Temp\opencode\ODAFileConverter.msi"
Invoke-WebRequest -Uri $msiUrl -OutFile $msiPath
msiexec /i $msiPath /qn
```

### Step 2. Prepare directories and copy DWG

```powershell
$dwgSource = "<path_to_dwg_file>"
$inputDir = "C:\Users\N00014~1\AppData\Local\Temp\opencode\dwg_input"
$outputDir = "C:\Users\N00014~1\AppData\Local\Temp\opencode\dxf_output"
New-Item -ItemType Directory -Force -Path $inputDir
New-Item -ItemType Directory -Force -Path $outputDir
Copy-Item -LiteralPath $dwgSource -Destination "$inputDir\"
```

### Step 3. Convert DWG → DXF using ODA File Converter

```powershell
& "C:\Program Files\ODA\ODAFileConverter 27.1.0\ODAFileConverter.exe" `
    $inputDir $outputDir ACAD2018 DXF 0 1
```

Parameters:
- `ACAD2018` — output DXF version (most compatible with ezdxf)
- `DXF` — output format
- `0` — no recursive
- `1` — audit/repair before conversion

Verify output:
```powershell
Get-ChildItem $outputDir | Select-Object Name, Length
```

### Step 4. Install ezdxf (if needed)

```powershell
py -3 -m pip install ezdxf
```

### Step 5. Write and run analysis script

Create a Python script that performs the following analyses:

#### 5a. Basic file information
- DXF version (`doc.dxfversion`)
- Header variables (`$ACADVER`, `$INSUNITS`, `$EXTMIN`, `$EXTMAX`, `$LTSCALE`, `$DIMSCALE`)

#### 5b. Layer analysis
- List all layers with color, linetype, visibility
- Count entities per layer

#### 5c. Entity statistics
- Count by type: LWPOLYLINE, LINE, CIRCLE, ARC, HATCH, DIMENSION, MTEXT, TEXT, INSERT, etc.

#### 5d. Dimension analysis
- Extract all DIMENSION entities
- Get `actual_measurement`, `defpoint`, `defpoint2`, `dimtype`, `angle`
- Group by approximate position (top/bottom sections)

#### 5e. Geometry analysis
- Bounding box calculation (manual iteration over all entities)
- LWPOLYLINE vertices listing (center, width, height, closed status)
- LINE start/end coordinates and lengths
- Circle centers and radii (from blocks too)

#### 5f. Hatch analysis
- Pattern names and layer assignments

#### 5g. Text/Block analysis
- MTEXT and TEXT content
- Block definitions and their contents
- Image references

#### 5h. Layout analysis
- List all layouts (Model, Paper spaces)
- Viewport entities in paper space

### Step 6. Generate Markdown Report

Write a comprehensive markdown file in the project directory with these sections:

1. **檔案基本資訊** — file name, size, DWG/DXF version, software used, units
2. **圖層結構** — complete layer table with colors, linetypes, visibility
3. **實體統計** — entity count by type
4. **尺寸標註分析** — all dimensions with measured values, grouped by position
5. **幾何結構** — bounding box, polyline details, line segments
6. **填充圖案** — hatch patterns and their distribution
7. **文字物件** — text content from MTEXT/TEXT entities
8. **圖塊** — block definitions and contents
9. **版面配置** — layout information
10. **總結** — comprehensive summary of the drawing

### Step 7. Cleanup

```powershell
Remove-Item -Path $inputDir -Recurse -Force
Remove-Item -Path $outputDir -Recurse -Force
```

## Key ezdxf API Reference

| What to get | Code |
|---|---|
| Open file | `doc = ezdxf.readfile(path)` |
| Model space | `msp = doc.modelspace()` |
| All layers | `doc.layers` |
| All blocks | `doc.blocks` |
| Entity type | `entity.dxftype()` |
| Entity layer | `entity.dxf.layer` |
| LWPOLYLINE points | `entity.get_points()` |
| LINE start/end | `entity.dxf.start`, `entity.dxf.end` |
| CIRCLE center/radius | `entity.dxf.center`, `entity.dxf.radius` |
| DIMENSION measurement | `entity.dxf.actual_measurement` |
| DIMENSION defpoints | `entity.dxf.defpoint`, `entity.dxf.defpoint2` |
| MTEXT content | `entity.text` |
| TEXT content | `entity.dxf.text` |
| Header variable | `doc.header['$VARIABLE']` |
| Layout list | `doc.layouts` |

## Common DXF Entity Types

| Type | Description | Key attributes |
|---|---|---|
| LWPOLYLINE | Lightweight polyline | vertices, closed |
| LINE | Straight line segment | start, end |
| CIRCLE | Circle | center, radius |
| ARC | Arc segment | center, radius, start/end angle |
| HATCH | Fill pattern | pattern_name, layer |
| DIMENSION | Dimension annotation | actual_measurement, defpoint, defpoint2 |
| MTEXT | Multi-line text | text (content) |
| TEXT | Single-line text | dxf.text (content) |
| INSERT | Block reference | block_name, insert point |
| SOLID | 2D solid fill | 3-4 corner points |
| ELLIPSE | Ellipse | center, major_axis, ratio |
| SPLINE | B-spline curve | control_points, knots |

## Environment gotchas

- **ODA File Converter needs input/output directories** — cannot process single files directly; must place files in a directory.
- **ODA command line syntax**: `ODAFileConverter.exe <input_dir> <output_dir> <version> <format> <recurse> <audit>`
- **ezdxf cannot read DWG directly** — must convert to DXF first.
- **DXF text encoding** — use `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')` for Chinese characters.
- **Bounding box** — `ezdxf.bbox` may fail on some entities; manual iteration is more reliable.
- **Dimension text** — may be empty if using automatic measurement; check `actual_measurement` attribute.
- **Large files** — read in chunks if needed; DXF can be much larger than DWG.

## Deliverables checklist
- [ ] `<drawing_name>.dxf` in temp output directory
- [ ] `<drawing_name>-圖面詳細說明.md` in the project directory
- [ ] Temp files cleaned up
