"""Print concrete (non-schema) examples of the key semantic objects in the
sanity set, so the KQP report can cite exact JSON shapes:
- a SketchCircle curve (where is radius / center?)
- a SketchArc curve
- a SketchLine curve
- a constraint of each kind
- a dimension of each kind with its parameter.value
- a profile with multiple loops
- the extrude extent_one.distance.value (the extrusion height)
- the top-level properties block (the GT answer source)
"""
import json
from pathlib import Path

SET = Path(__file__).resolve().parent / "sanity_set_50"


def main():
    seen = set()
    circle = arc = line = None
    cons = {}
    dims = {}
    multi_loop_profile = None
    extrude_dist = None
    props_example = None

    for fp in sorted(SET.glob("*.json")):
        if fp.name == "manifest.json":
            continue
        d = json.loads(fp.read_text(encoding="utf-8"))
        ents = d.get("entities", {})
        if props_example is None and isinstance(d.get("properties"), dict):
            props_example = (fp.stem, d["properties"])

        for s in ents.values():
            if not (isinstance(s, dict) and s.get("type") == "Sketch"):
                continue
            for c in s.get("curves", {}).values():
                if not isinstance(c, dict):
                    continue
                t = c.get("type")
                if t == "SketchCircle" and circle is None:
                    circle = c
                elif t == "SketchArc" and arc is None:
                    arc = c
                elif t == "SketchLine" and line is None:
                    line = c
            for c in s.get("constraints", {}).values():
                if isinstance(c, dict):
                    cons.setdefault(c.get("type"), c)
            for dd in s.get("dimensions", {}).values():
                if isinstance(dd, dict):
                    dims.setdefault(dd.get("type"), dd)
            for p in s.get("profiles", {}).values():
                if isinstance(p, dict) and isinstance(p.get("loops"), list) and len(p["loops"]) >= 2 and multi_loop_profile is None:
                    multi_loop_profile = p
        for e in ents.values():
            if isinstance(e, dict) and e.get("type") == "ExtrudeFeature" and extrude_dist is None:
                d1 = e.get("extent_one", {}).get("distance", {})
                if isinstance(d1, dict):
                    extrude_dist = (fp.stem, d1, e.get("extent_type"), e.get("extent_one", {}).get("taper_angle"))
        if all([circle, arc, line, multi_loop_profile, extrude_dist, props_example]) and len(cons) >= 5 and len(dims) >= 4:
            break

    def show(title, obj):
        print("=" * 60)
        print(title)
        print("=" * 60)
        print(json.dumps(obj, indent=2, ensure_ascii=False, default=str)[:2000])
        print()

    show("SketchCircle curve (radius / center source)", circle)
    show("SketchArc curve", arc)
    show("SketchLine curve", line)
    show("one example of EACH constraint type", cons)
    show("one example of EACH dimension type (note parameter.value, is_driving)", dims)
    show("profile with >=2 loops (multi-contour)", multi_loop_profile)
    show("extrude extent_one.distance (= extrusion height)", extrude_dist)
    show("top-level properties (Kernel Query GT source)", props_example)


if __name__ == "__main__":
    main()
