"""Run compiler_v6 on ALL 50 samples and save design_plan_v6_instances.

This is the validation/freeze step: regenerate v6 instances for the full
sanity set regardless of which schema version was used for the original
hand-written Plan. For samples 6-10 (never hand-written), only the compiler
output exists. For samples 11-50, this lets us compare compiler_v6 output
against hand-written plans at various schema versions.
"""
import json
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SANITY = ROOT / "data" / "sanity_set_50"
OUT = ROOT / "compiler" / "instances_v6"

sys.path.insert(0, str(ROOT / "compiler"))
import design_plan_compiler as dpc

OUT.mkdir(exist_ok=True)

IDS = []
m = json.loads((SANITY / "_manifest_lookup.json").read_text(encoding="utf-8")) if (SANITY / "_manifest_lookup.json").exists() else None
if m is None:
    import json as _j
    m = _j.load(open(ROOT / "data/sanity_set_50/manifest.json", encoding="utf-8"))
IDS = [e["id"] for e in m["entries"]]

results = {"compiled_ok": 0, "compiled_fail": 0, "failures": []}
for sid in IDS:
    src = SANITY / f"{sid}.json"
    out_path = OUT / f"{sid}.design_plan.json"
    try:
        plan = dpc.compile_design_plan(src)
        # ensure v0.6 schema version (compiler emits its own; should be v0.6 already)
        if "schema_version" not in plan:
            plan["schema_version"] = "design_plan_v0.6"
        out_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
        results["compiled_ok"] += 1
    except Exception as e:
        results["compiled_fail"] += 1
        results["failures"].append({"sid": sid, "error": str(e), "tb": traceback.format_exc()})

print(f"Compiled OK: {results['compiled_ok']}/50")
print(f"Failed: {results['compiled_fail']}/50")
if results["failures"]:
    print("\nFailures:")
    for f in results["failures"]:
        print(f"  {f['sid']}: {f['error']}")

(OUT / "_summary.json").write_text(json.dumps({"ok": results["compiled_ok"], "fail": results["compiled_fail"]}, indent=2))
