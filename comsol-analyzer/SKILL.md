---
name: comsol-analyzer
description: Analyze COMSOL Multiphysics .mph model files — structure/metadata via ZIP+XML/JSON parsing (no COMSOL needed), and numeric result comparison via comsolbatch + Java API temp-field/probe extraction. Covers model metadata, parameters, physics, geometry, materials, studies, mesh, and numerical validation of temperature fields between model versions.
license: MIT
compatibility: opencode
metadata:
  audience: opencode agents
  workflow: comsol-analysis
  languages: zh-TW
---

# comsol-analyzer — COMSOL .mph 模型分析與數值比對

Two complementary workflows for COMSOL `.mph` files:

1. **結構分析（ZIP/XML，免安裝 COMSOL）** — parse the internal XML/JSON to document metadata, parameters, physics, geometry, materials, studies, mesh.
2. **數值比對（comsolbatch + Java API）** — with COMSOL installed, extract temperature fields / probe histories and compare model versions numerically.

---

## PART A — 結構分析（免 COMSOL，ZIP/XML）

### When to use
- 分析 COMSOL 模型 / 說明 .mph 檔案 / COMSOL 模型結構 / comsol model analysis, or to document a `.mph` file's physics, geometry, materials, studies.

### Prerequisites
- **No COMSOL required** — `.mph` is a standard ZIP archive.
- **No extra Python packages** — standard lib `zipfile`/`xml.etree`/`json`. Windows: PowerShell 5.1 + `Expand-Archive`.

### .mph File Structure
| File | Content | Readable? |
|---|---|---|
| `fileversion` | COMSOL version (e.g. `2092:COMSOL 6.4.0.429`) | Yes (text) |
| `modelinfo.xml` | Metadata: version, physics, license, geometry | Yes (XML) |
| `dmodel.xml` | **Core model definition** (can be >5 MB) | Yes (XML) |
| `smodel.json` | Structured model tree | Yes (JSON) |
| `guimodel.xml` | GUI state | Yes (XML) |
| `usedlicenses.txt` | Required license modules | Yes (text) |
| `geometry*.mphbin` | Binary geometry (Parasolid) | Binary |
| `solution*.mphbin` | Binary solution data | Binary |
| `mesh*.mphbin` | Binary mesh data | Binary |

### Pipeline (structure)
1. Copy `.mph` → `.zip` and `Expand-Archive` into a temp dir.
2. Read `fileversion`, `modelinfo.xml`, `usedlicenses.txt`, `guimodel.xml` (parallel).
3. Parse `dmodel.xml` sections: `ModelParam tag="param"` (global params), `<Physics op=...>` (interfaces + features incl. `Coil`), `<GeomSequence tag="geom1">` (features: Polygon/Circle/Revolve/Difference/Array/Extract/Finalize; `boundingBox`; `numEntities`=vertices,edges,faces,domains), `<Material op="Common">`, `<StudyList>`→`<Study>` (+StudyFeature: CCC/Frequency/Transient/Stationary; `p:freq`, `p:tlist`), mesh, `<ResultFeature>` plots.
4. Parse `smodel.json` for quick parameter/material/study lookup.
5. Generate markdown report (sections: 基本資訊 / 所需授權模組 / 模型概述 / 物理場 / 多物理耦合 / 線圈定義 / 模型參數 / 3D 幾何 / 材料 / 研究 / 網格 / 求解器觀察 / 總結).
6. Cleanup temp files.

### Key XML Patterns
| What | Pattern |
|---|---|
| Physics interface | `<Physics op="..." tag="..." name="...">` |
| Coil definition | `<PhysicsFeature op="Coil" tag="coilN">` |
| Coil type/current | `<param param="CoilType"...>` / `<param param="ICoil"...>` |
| Material | `<Material op="Common" tag="matN"...>` |
| Study type | `<StudyFeature op="...">` |
| Geometry features | `<GeomFeature op="..." tag="..." name="...">` |
| Bounding box | `<boundingBox>minX,maxX,minY,maxY,minZ,maxZ</boundingBox>` |
| Entity count | `<numEntities>vertices,edges,faces,domains</numEntities>` |
| Global equations (PID) | `<Physics op="GlobalEquations">` |

### Gotchas
- `.mph` is a ZIP — rename to `.zip` before expanding.
- `dmodel.xml` up to 60 MB — read in chunks with offset/limit.
- Chinese chars may be `&#xHEX;` — decode with `[System.Web.HttpUtility]::HtmlDecode()`.
- Binary `.mphbin` cannot be read as text.

---

## PART B — 數值比對（comsolbatch + Java API）

### Environment (this machine)
| Item | Value |
|------|-------|
| COMSOL version | 6.4.0.293 (build 293; loads 6.4.0.429 models — verified) |
| comsolbatch | `C:\Program Files\COMSOL\COMSOL64\Multiphysics\bin\win64\comsolbatch.exe` |
| comsolcompile | `...\bin\win64\comsolcompile.exe` |
| Working dir | `C:\Users\N000149839\AppData\Local\Temp\opencode\probe\` |
| Python | `py` (3.13) |

### Important notes
- **Sandbox**: comsolbatch blocks Java file I/O (FilePermission). Solution: hardcode mph path in Java constant, print results to stdout, capture via `-batchlogout`.
- **UTF-16LE output**: comsolbatch stdout is UTF-16LE (BOM `\xff\xfe`). Decode with `.decode('utf-16')`.
- **Large models** (5+ GB) need memory; start with small model to validate, then run the big one.
- mph built with 6.4.0.429 loads under 6.4.0.293.

### Java extraction script template (`ProbeTemp.java`)
```java
import com.comsol.model.*;
import com.comsol.model.util.*;
import java.util.*;

public class ProbeTemp {
    static final String MTAG = "m1";
    static final String IN_MPH = "PATH_TO_MODEL.mph";   // EDIT THIS

    public static void main(String[] args) { run(); }

    public static Model run() {
        Model m = null;
        try {
            m = ModelUtil.load(MTAG, IN_MPH);
            System.out.println("HEADER,loaded," + m.name() + ",comsol=" + ModelUtil.getComsolVersion());
            String[] all = m.result().dataset().tags();
            Arrays.sort(all);
            System.out.println("HEADER,datasets," + Arrays.toString(all));
            for (String ds : all) processDataset(m, ds);
            System.err.println("DONE OK");
        } catch (Throwable t) {
            System.err.println("EXCEPTION " + t);
        } finally {
            try { ModelUtil.remove(MTAG); } catch (Throwable t2) { }
        }
        return null;
    }

    static void processDataset(Model m, String ds) {
        String tT = "evT_" + ds, tt = "evt_" + ds;
        double[][] T = null;
        try {
            m.result().numerical().create(tT, "EvalPoint");
            m.result().numerical(tT).set("data", ds);
            m.result().numerical(tT).set("expr", new String[]{"T"});
            m.result().numerical(tT).set("unit", new String[]{"K"});
            try { m.result().numerical(tT).selection().all(); } catch (Throwable t) {}
            T = m.result().numerical(tT).getReal();
        } catch (Throwable t) {
            System.err.println("FAIL evT " + ds + " : " + t.getMessage());
        }
        if (T == null) { clean(m, tT); clean(m, tt); return; }

        double[] times = null;
        try {
            m.result().numerical().create(tt, "EvalPoint");
            m.result().numerical(tt).set("data", ds);
            m.result().numerical(tt).set("expr", new String[]{"t"});
            m.result().numerical(tt).set("unit", new String[]{"s"});
            try { m.result().numerical(tt).selection().all(); } catch (Throwable t) {}
            double[][] tr = m.result().numerical(tt).getReal();
            times = tr[0];
        } catch (Throwable t) {
            System.err.println("FAIL time " + ds + " : " + t.getMessage());
        }

        double[] cr = coord(m, ds, "r");
        double[] cz = coord(m, ds, "z");

        int nPt = T.length;
        int nS = nPt > 0 ? (T[0] != null ? T[0].length : 0) : 0;
        System.err.println("SUM " + ds + " points=" + nPt + " sols=" + nS);

        for (int i = 0; i < nPt; i++) {
            double r = (cr != null && i < cr.length) ? cr[i] : Double.NaN;
            double z = (cz != null && i < cz.length) ? cz[i] : Double.NaN;
            for (int s = 0; s < nS; s++) {
                double t = (times != null && s < times.length) ? times[s] : s;
                double v = (T[i] != null && s < T[i].length) ? T[i][s] : Double.NaN;
                System.out.println("PDATA," + ds + "," + s + "," + fmt(t) + "," + fmt(r) + "," + fmt(z) + "," + fmt(v));
            }
        }
        clean(m, tT); clean(m, tt);
    }

    static double[] coord(Model m, String ds, String expr) {
        String c = "evc_" + ds + "_" + expr;
        try {
            m.result().numerical().create(c, "EvalPoint");
            m.result().numerical(c).set("data", ds);
            m.result().numerical(c).set("expr", new String[]{expr});
            try { m.result().numerical(c).selection().all(); } catch (Throwable t) {}
            double[][] v = m.result().numerical(c).getReal();
            double[] out = new double[v.length];
            for (int i = 0; i < v.length; i++) out[i] = (v[i] != null && v[i].length > 0) ? v[i][0] : Double.NaN;
            return out;
        } catch (Throwable t) {
            System.err.println("NOCOORD " + ds + " " + expr + " : " + t.getMessage());
            return null;
        } finally {
            try { m.result().numerical().remove(c); } catch (Throwable t) { }
        }
    }

    static void clean(Model m, String tag) {
        try { m.result().numerical().remove(tag); } catch (Throwable t) { }
    }

    static String fmt(double v) {
        if (Double.isNaN(v) || Double.isInfinite(v)) return "NaN";
        return String.format(java.util.Locale.US, "%.6g", v);
    }
}
```

### Compile & run
```powershell
$w="C:\Users\N000149839\AppData\Local\Temp\opencode\probe"
$cc="C:\Program Files\COMSOL\COMSOL64\Multiphysics\bin\win64\comsolcompile.exe"
$cb="C:\Program Files\COMSOL\COMSOL64\Multiphysics\bin\win64\comsolbatch.exe"
Push-Location $w
& $cc ProbeTemp.java 2>&1 | Select-Object -Last 3   # must exit 0
& $cb -inputfile ProbeTemp.class -batchlogout 1> probe_raw.txt 2> probe_err.txt
Pop-Location
```

### Parse UTF-16 → CSV
```python
raw = open('probe_raw.txt', 'rb').read().decode('utf-16')
rows = [l[len('PDATA,'):] for l in raw.splitlines() if l.startswith('PDATA,')]
open('probe.csv', 'w', encoding='utf-8').write('dataset,solIndex,t,r,z,T\n' + '\n'.join(rows) + '\n')
```

### Comparison logic
- CSV columns: `dataset,solIndex,t,r,z,T`.
- Probe point: `dataset=='avh1'` (控溫點; check its r,z).
- Geometry solution dataset typically `dset5`/`dset6` (identical); evaluate all geometry vertices via `selection().all()` → 193 points, entity order matches across versions (same topology).
- Match time by A's time points interpolating B (`bisect`), compute per-vertex dT.
- Filter NaNs and outliers (T<200 or T>5000 K) before stats.
- Compute probe min/max/mean dT + relative %, full-field per-step max/mean dT, and z-band spatial breakdown.

### Report structure (numeric comparison)
Overview table (file, steps, vertices, axisym coords) → probe comparison table → full-field stats → spatial (z-band) breakdown → key findings (e.g. geometry-shift effect at bottom band, numerical blow-up at outer radius) → conclusion.

### Tips
- Validate on small model (1–2 GB) first, then big (5+ GB).
- `selection().all()` returns geometry vertices in topological order — 1:1 match if topology identical.
- Watch for numerical blow-up (values ~1e39) in one version → investigate stability.
- Probe point agreement validates methodology; band-wise differences localize physical changes.

---

## Joint output convention
- Structure-analysis report: `<model_name>-模型詳細說明.md`
- Numeric-compare report: append a "溫度場數值比對" section, or a `...-V2.md` report.
- Always clean up temp zip/extract dirs and note analysis method + limitations.
