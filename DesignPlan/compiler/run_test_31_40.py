"""Run the EXISTING (v0.4-era) design plan compiler on samples 31-40 and compare
to hand-written v5 Plans. Used to identify compiler weaknesses for the v0.5 update.

Reports per-sample: compile success, profile.type match, key dimension match,
direction match, extent_type match.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SANITY = ROOT / "data" / "sanity_set_50"
V5_HAND = ROOT / "DesignPlan" / "samples" / "v5"
COMPILER_OUT = ROOT / "compiler" / "out_v5"

sys.path.insert(0, str(ROOT / "compiler"))
import design_plan_compiler as dpc

IDS = [
    "105278_909f3813_0000",
    "106323_77f22d29_0004",
    "106817_bb28b7aa_0002",
    "106817_bb28b7aa_0003",
    "106817_bb28b7aa_0004",
    "107055_0500fdd1_0027",
    "107075_beb19139_0000",
    "107466_72cd4ce9_0002",
    "107467_a8afc51d_0000",
    "107467_a8afc51d_0002",
]

COMPILER_OUT.mkdir(exist_ok=True)


def get_handwritten(sid):
    p = V5_HAND / f"{sid}.design_plan.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def dim_val(d, *path, default=None):
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
        comp = dpc.compile_design_plan(SANITY / f"{sid}.json")
    except Exception as e:
        return {"sid": sid, "status": "COMPILE_ERROR", "error": str(e)}

    out = {"sid": sid, "status": "OK", "checks": []}
    hb = hand["solid_bodies"][0]
    cb = comp["solid_bodies"][0]

    # profile type
    hptype = hb["profiles"][0]["type"]
    cptype = cb["profiles"][0]["type"]
    out["checks"].append(("profile.type", hptype, cptype, hptype == cptype))

    # extrude distance
    hd = hb["dimensions"]["extrude_distance"]["value"]
    cd = cb["dimensions"]["extrude_distance"]["value"]
    out["checks"].append(("extrude_distance", hd, cd, abs(hd - cd) < 0.05))

    # extent_type
    het = hb["extrude"]["extent_type"]
    cet = cb["extrude"]["extent_type"]
    out["checks"].append(("extent_type", het, cet, het == cet))

    # direction
    hdir = hb["extrude"]["direction"]
    cdir = cb["extrude"]["direction"]
    out["checks"].append(("direction", hdir, cdir, hdir == cdir))

    # key profile dim
    if hptype == "circle":
        hr = dim_val(hand, "solid_bodies", 0, "dimensions", "profiles", 0, "radius")
        cr = dim_val(comp, "solid_bodies", 0, "dimensions", "profiles", 0, "radius")
        out["checks"].append(("radius", hr, cr, abs(hr - cr) < 0.05 if hr and cr else False))
    elif hptype == "annulus":
        ho = dim_val(hand, "solid_bodies", 0, "dimensions", "profiles", 0, "outer_radius")
        co = dim_val(comp, "solid_bodies", 0, "dimensions", "profiles", 0, "outer_radius")
        hi = dim_val(hand, "solid_bodies", 0, "dimensions", "profiles", 0, "inner_radius")
        ci = dim_val(comp, "solid_bodies", 0, "dimensions", "profiles", 0, "inner_radius")
        out["checks"].append(("outer_radius", ho, co, abs(ho - co) < 0.05 if ho and co else False))
        out["checks"].append(("inner_radius", hi, ci, abs(hi - ci) < 0.05 if hi and ci else False))
    elif hptype == "rectangle":
        hl = dim_val(hand, "solid_bodies", 0, "dimensions", "profiles", 0, "length_u")
        cl = dim_val(comp, "solid_bodies", 0, "dimensions", "profiles", 0, "length_u")
        hw = dim_val(hand, "solid_bodies", 0, "dimensions", "profiles", 0, "width_v")
        cw = dim_val(comp, "solid_bodies", 0, "dimensions", "profiles", 0, "width_v")
        out["checks"].append(("length_u", hl, cl, abs(hl - cl) < 0.05 if hl and cl else False))
        out["checks"].append(("width_v", hw, cw, abs(hw - cw) < 0.05 if hw and cw else False))
    elif hptype == "stadium":
        hs = dim_val(hand, "solid_bodies", 0, "dimensions", "profiles", 0, "straight_length")
        cs = dim_val(comp, "solid_bodies", 0, "dimensions", "profiles", 0, "straight_length")
        hr = dim_val(hand, "solid_bodies", 0, "dimensions", "profiles", 0, "radius")
        cr = dim_val(comp, "solid_bodies", 0, "dimensions", "profiles", 0, "radius")
        out["checks"].append(("straight_length", hs, cs, abs(hs - cs) < 0.05 if hs and cs else False))
        out["checks"].append(("radius", hr, cr, abs(hr - cr) < 0.05 if hr and cr else False))
    elif hptype == "arbitrary_closed":
        # check arc_radii count
        har = dim_val(hand, "solid_bodies", 0, "dimensions", "profiles", 0, "arc_radii")
        car = dim_val(comp, "solid_bodies", 0, "dimensions", "profiles", 0, "arc_radii")
        out["checks"].append(("arc_radii_present", har is not None, car is not None, (har is not None) == (car is not None)))

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
    print("\n" + "=" * 60)
    print("SUMMARY")
    total_ok = total_checks = 0
    for r in results:
        if r["status"] != "OK":
            continue
        for _, _, _, ok in r["checks"]:
            total_checks += 1
            if ok:
                total_ok += 1
    print(f"  Checks passed: {total_ok}/{total_checks}")
    (ROOT / "compiler" / "comparison_report_v5.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"  Full report: compiler/comparison_report_v5.json")


if __name__ == "__main__":
    main()
