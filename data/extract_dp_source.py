"""Extract a compact summary of the first 5 sanity samples' modeling-history
JSON, as source material for hand-writing Design Plans.

Schema (per Fusion360 Gallery sequence JSON):
  metadata      : parent_project, component_name, component_index
  timeline      : list of {index, entity}  (entity = UUID into entities dict)
  entities      : dict[UUID -> entity]
                   Sketch      : name, type, points, curves, constraints,
                                  dimensions, profiles, transform, reference_plane
                   ExtrudeFeat : name, type, profiles, operation, start_extent,
                                  extent_type, extent_one{distance,taper},
                                  faces, bodies, extrude_bodies
  properties    : final GT (topology counts, bbox, volume, area, surface_types)
  sequence      : ...
"""
import json
from pathlib import Path

SANITY_DIR = Path(__file__).resolve().parent / "sanity_set_50"
IDS = [
    "100243_9fb796fe_0005",
    "100243_9fb796fe_0006",
    "100877_ac1e5a17_0001",
    "100877_ac1e5a17_0017",
    "101269_f084ba14_0023",
]


def show_sketch(eid, e, out):
    out.append(f"  [SKETCH]  id={eid}  name={e.get('name')}")
    rp = e.get("reference_plane", {})
    plane = rp.get("plane", {})
    n = plane.get("normal", {})
    u = plane.get("u_direction", {})
    v = plane.get("v_direction", {})
    o = plane.get("origin", {})
    out.append(f"    plane: name={rp.get('name')}  origin=({o.get('x')},{o.get('y')},{o.get('z')})")
    out.append(f"           normal=({n.get('x')},{n.get('y')},{n.get('z')})  "
               f"u=({u.get('x')},{u.get('y')},{u.get('z')})  v=({v.get('x')},{v.get('y')},{v.get('z')})")
    # points
    pts = e.get("points", {})
    out.append(f"    points ({len(pts)}):")
    for pid, p in pts.items():
        out.append(f"       {pid[:8]}: ({p.get('x')},{p.get('y')},{p.get('z')})")
    # curves
    crvs = e.get("curves", {})
    out.append(f"    curves ({len(crvs)}):")
    for cid, c in crvs.items():
        ct = c.get("type")
        if ct == "SketchLine":
            sp, ep = c.get("start_point","")[:8], c.get("end_point","")[:8]
            out.append(f"       {cid[:8]}: {ct}  {sp} -> {ep}")
        elif ct in ("SketchCircle","SketchArc"):
            out.append(f"       {cid[:8]}: {ct}  center={str(c.get('center_point',''))[:8]}  "
                       f"radius={c.get('radius')}  start={c.get('start_angle')}  end={c.get('end_angle')}")
        else:
            s = json.dumps(c, ensure_ascii=False)
            out.append(f"       {cid[:8]}: {s[:200]}")
    # constraints
    cons = e.get("constraints", {})
    out.append(f"    constraints ({len(cons)}):")
    for coid, co in cons.items():
        out.append(f"       {co.get('type')}: {json.dumps({k:v for k,v in co.items() if k!='type'}, ensure_ascii=False)[:120]}")
    # dimensions
    dims = e.get("dimensions", {})
    out.append(f"    dimensions ({len(dims)}):")
    for did, di in dims.items():
        para = di.get("parameter", {})
        val = para.get("value")
        driving = di.get("is_driving")
        e1 = str(di.get("entity_one",""))[:8]
        e2 = str(di.get("entity_two",""))[:8]
        orient = di.get("orientation")
        out.append(f"       {para.get('name')}: type={para.get('role')}  value={val}  driving={driving}  "
                   f"e1={e1} e2={e2} orient={orient}")
    # profiles
    profs = e.get("profiles", {})
    out.append(f"    profiles ({len(profs)}):")
    for pid, pr in profs.items():
        loops = pr.get("loops", [])
        n_curves = sum(len(L.get("profile_curves", [])) for L in loops)
        out.append(f"       {pid[:8]}: loops={len(loops)}  total_curves={n_curves}  "
                   f"outer_loops={sum(1 for L in loops if L.get('is_outer'))}")


def show_extrude(eid, e, out):
    out.append(f"  [EXTRUDE]  id={eid}  name={e.get('name')}")
    out.append(f"    operation: {e.get('operation')}")
    out.append(f"    extent_type: {e.get('extent_type')}")
    out.append(f"    start_extent: {e.get('start_extent')}")
    eo = e.get("extent_one", {})
    dist = eo.get("distance", {})
    taper = eo.get("taper_angle", {})
    out.append(f"    extent_one: distance={dist.get('value')}  taper={taper.get('value')}  type={eo.get('type')}")
    etwo = e.get("extent_two", {})
    if etwo:
        d2 = etwo.get("distance", {})
        out.append(f"    extent_two: distance={d2.get('value')}  type={etwo.get('type')}")
    # profiles
    profs = e.get("profiles", [])
    out.append(f"    input profiles ({len(profs)}):")
    for pr in profs:
        out.append(f"       sketch={str(pr.get('sketch',''))[:8]}  profile={str(pr.get('profile',''))[:8]}")
    # bodies
    bodies = e.get("bodies", {})
    out.append(f"    bodies produced ({len(bodies)}):")
    for bid, b in bodies.items():
        out.append(f"       {b.get('name')}: faces={[f[:8] for f in b.get('faces', [])]}")


def summarize(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    out = []
    out.append("=" * 90)
    out.append(f"FILE: {path.name}")
    md = data.get("metadata", {})
    out.append(f"metadata: project={md.get('parent_project')}  component={md.get('component_name')}  index={md.get('component_index')}")
    out.append("")
    ents = data.get("entities", {})
    tl = data.get("timeline", [])
    out.append(f"timeline: {len(tl)} ops;  entities: {len(ents)}")
    # Walk timeline in order
    for ev in tl:
        eid = ev.get("entity")
        e = ents.get(eid, {})
        etype = e.get("type", "?")
        out.append("")
        if etype == "Sketch":
            show_sketch(eid, e, out)
        elif etype == "ExtrudeFeature":
            show_extrude(eid, e, out)
        else:
            out.append(f"  [{etype}]  id={eid}")
            out.append(f"     {json.dumps(e, ensure_ascii=False)[:400]}")
    # properties
    out.append("")
    out.append("[properties]  (final GT)")
    out.append(json.dumps(data.get("properties", {}), indent=2, ensure_ascii=False))
    return "\n".join(out)


def main():
    big_out = []
    for sid in IDS:
        p = SANITY_DIR / f"{sid}.json"
        if not p.exists():
            big_out.append("MISSING: " + str(p))
            continue
        big_out.append(summarize(p))
    out_path = Path(__file__).resolve().parent / "dp_source_summary.txt"
    out_path.write_text("\n\n".join(big_out), encoding="utf-8")
    print("Wrote", out_path)


if __name__ == "__main__":
    main()
