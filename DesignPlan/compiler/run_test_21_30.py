"""Run the design plan compiler on samples 21-30 and compare to hand-written v4 Plans.

Reports per-sample: compile success, profile.type match, key dimension match.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SANITY = ROOT / "data" / "sanity_set_50"
V4_HAND = ROOT / "DesignPlan" / "samples" / "v4"
COMPILER_OUT = ROOT / "compiler" / "out"

sys.path.insert(0, str(ROOT / "compiler"))
import design_plan_compiler as dpc

IDS = [
    "102760_26430589_0037",
    "103284_e25015aa_0003",
    "103284_e25015aa_0004",
    "103481_b27a1cdf_0010",
    "103552_c3a389ed_0003",
    "104283_e5646f96_0000",
    "104283_e5646f96_0001",
    "104453_aba0f2d1_0002",
    "104453_aba0f2d1_0006",
    "104524_f829aab2_0001",
]

COMPILER_OUT.mkdir(exist_ok=True)


def get_handwritten(sid):
    p = V4_HAND / f"{sid}.design_plan.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def get_compiled(sid):
    p = SANITY / f"{sid}.json"
    return dpc.compile_design_plan(p)


def dim_val(d, *path, default=None):
    """Drill into nested dict/list by path keys; return value or default.
    Path elements can be str (dict key) or int (list index)."""
    cur = d
    for k in path:
        if isinstance(cur, dict) and isinstance(k, str):
            cur = cur.get(k)
        elif isinstance(cur, list) and isinstance(k, int):
            cur = cur[k] if 0 <= k < len(cur) else None
        else:
            return default
        if cur is None:
            return default
    if isinstance(cur, dict):
        return cur.get("value", default)
    return cur


def compare(sid):
    hand = get_handwritten(sid)
    try:
        comp = get_compiled(sid)
    except Exception as e:
        return {"sid": sid, "status": "COMPILE_ERROR", "error": str(e)}

    out = {"sid": sid, "status": "OK", "checks": []}

    # profile type
    hptype = hand["solid_bodies"][0]["profiles"][0]["type"]
    cptype = comp["solid_bodies"][0]["profiles"][0]["type"]
    out["checks"].append(("profile.type", hptype, cptype, hptype == cptype))

    # extrude distance
    hd = hand["solid_bodies"][0]["dimensions"]["extrude_distance"]["value"]
    cd = comp["solid_bodies"][0]["dimensions"]["extrude_distance"]["value"]
    out["checks"].append(("extrude_distance", hd, cd, abs(hd - cd) < 0.02))

    # direction
    hdir = hand["solid_bodies"][0]["extrude"]["direction"]
    cdir = comp["solid_bodies"][0]["extrude"]["direction"]
    out["checks"].append(("direction", hdir, cdir, hdir == cdir))

    # key profile dim
    if hptype == "circle":
        hr = dim_val(hand, "solid_bodies", 0, "dimensions", "profiles", 0, "radius")
        cr = dim_val(comp, "solid_bodies", 0, "dimensions", "profiles", 0, "radius")
        out["checks"].append(("radius", hr, cr, abs(hr - cr) < 0.02 if hr and cr else False))
    elif hptype == "rectangle":
        hl = dim_val(hand, "solid_bodies", 0, "dimensions", "profiles", 0, "length_u")
        cl = dim_val(comp, "solid_bodies", 0, "dimensions", "profiles", 0, "length_u")
        hw = dim_val(hand, "solid_bodies", 0, "dimensions", "profiles", 0, "width_v")
        cw = dim_val(comp, "solid_bodies", 0, "dimensions", "profiles", 0, "width_v")
        out["checks"].append(("length_u", hl, cl, abs(hl - cl) < 0.02 if hl and cl else False))
        out["checks"].append(("width_v", hw, cw, abs(hw - cw) < 0.02 if hw and cw else False))
    elif hptype == "stadium":
        hs = dim_val(hand, "solid_bodies", 0, "dimensions", "profiles", 0, "straight_length")
        cs = dim_val(comp, "solid_bodies", 0, "dimensions", "profiles", 0, "straight_length")
        hr = dim_val(hand, "solid_bodies", 0, "dimensions", "profiles", 0, "radius")
        cr = dim_val(comp, "solid_bodies", 0, "dimensions", "profiles", 0, "radius")
        out["checks"].append(("straight_length", hs, cs, abs(hs - cs) < 0.02 if hs and cs else False))
        out["checks"].append(("radius", hr, cr, abs(hr - cr) < 0.02 if hr and cr else False))
    elif hptype == "annulus":
        ho = dim_val(hand, "solid_bodies", 0, "dimensions", "profiles", 0, "outer_radius")
        co = dim_val(comp, "solid_bodies", 0, "dimensions", "profiles", 0, "outer_radius")
        hi = dim_val(hand, "solid_bodies", 0, "dimensions", "profiles", 0, "inner_radius")
        ci = dim_val(comp, "solid_bodies", 0, "dimensions", "profiles", 0, "inner_radius")
        out["checks"].append(("outer_radius", ho, co, abs(ho - co) < 0.02 if ho and co else False))
        out["checks"].append(("inner_radius", hi, ci, abs(hi - ci) < 0.02 if hi and ci else False))
    elif hptype == "rectangular_frame":
        hol = dim_val(hand, "solid_bodies", 0, "dimensions", "profiles", 0, "outer_length_u")
        col = dim_val(comp, "solid_bodies", 0, "dimensions", "profiles", 0, "outer_length_u")
        out["checks"].append(("outer_length_u", hol, col, abs(hol - col) < 0.02 if hol and col else False))

    # save compiled
    (COMPILER_OUT / f"{sid}.design_plan.json").write_text(
        json.dumps(comp, indent=2, ensure_ascii=False), encoding="utf-8")

    return out


def main():
    results = []
    for sid in IDS:
        r = compare(sid)
        results.append(r)
        if r["status"] != "OK":
            print(f"{sid}: {r['status']} - {r.get('error')}")
            continue
        print(f"\n=== {sid} ===")
        for name, h, c, ok in r["checks"]:
            mark = "✓" if ok else "✗"
            print(f"  {mark} {name}: hand={h} comp={c}")
    # summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    total_ok = 0
    total_checks = 0
    for r in results:
        if r["status"] != "OK":
            continue
        for _, _, _, ok in r["checks"]:
            total_checks += 1
            if ok:
                total_ok += 1
    print(f"  Checks passed: {total_ok}/{total_checks}")
    # also dump full results
    (ROOT / "compiler" / "comparison_report.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"  Full report: compiler/comparison_report.json")


if __name__ == "__main__":
    main()
