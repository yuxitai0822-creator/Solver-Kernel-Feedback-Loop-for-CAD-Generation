"""KQP for sample 100243_9fb796fe_0005 (1.9x1.9 rectangle, OneSide extrude 20.0).

This Kernel Query Program reads the reconstructed STEP via OpenCascade (OCP) and
issues structured queries that mirror the design intent:

  Step1  sketch on plane normal=(0,1,0)          -> health: solid along that axis
  Step2  1.9 x 1.9 rectangle (4 lines, 1 profile) -> topology: 1 profile / 4 edges
  Step3  horizontal/vertical constraints          -> (verified by geometry orthogonality)
  Step4  driving dims width=height=1.9            -> dimension: bbox in-plane = 1.9 each
  Step5  select closed profile                    -> topology: closed, 1 loop
  Step6  extrude 20.0 along normal, new body      -> dimension: height along normal=20,
                                                     topology: body_count=1

Output: a structured JSON report of every query result. No pass/fail here — the
companion verify script compares these to the JSON GT.
"""
import json
import math
from collections import Counter
from pathlib import Path

from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_FACE, TopAbs_EDGE, TopAbs_VERTEX, TopAbs_SHELL, TopAbs_SOLID, TopAbs_WIRE
from OCP.TopExp import TopExp_Explorer, TopExp
from OCP.TopTools import TopTools_IndexedMapOfShape
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.gp import gp_Pnt
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp

STEP_FILE = Path(__file__).resolve().parent / "100243_9fb796fe_0005.step"
# design intent from the modeling sequence (sketch plane + extrude)
SKETCH_NORMAL = (0.0, 1.0, 0.0)
EXTRUDE_DISTANCE = 20.0
RECT_SIDE = 1.9
EXTENT_TYPE = "OneSideFeatureExtentType"
# STEP internal unit is mm; Fusion JSON properties are in cm -> ratio = 10
MM_TO_CM = 0.1


def load_shape():
    r = STEPControl_Reader()
    status = r.ReadFile(str(STEP_FILE))
    if not status:
        raise RuntimeError(f"STEP read failed (status={status})")
    r.TransferRoots()
    return r.OneShape(), r


def count_topo_unique(shape, t):
    """Count unique (non-shared) sub-shapes of a given type."""
    m = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, t, m)
    return m.Extent()


def bbox(shape):
    b = Bnd_Box()
    BRepBndLib.Add_s(shape, b)
    xmin, ymin, zmin, xmax, ymax, zmax = b.Get()
    return {
        "min": [xmin, ymin, zmin],
        "max": [xmax, ymax, zmax],
        "size": [xmax - xmin, ymax - ymin, zmax - zmin],
    }


def surface_type_map(shape):
    """Map each face's underlying surface to its OpenCascade dynamic type name."""
    types = Counter()
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        f = TopoDS.Face(exp.Current())
        surf = BRep_Tool.Surface_s(f)
        name = surf.DynamicType().Name()  # e.g. 'Geom_Plane' / 'Geom_CylindricalSurface'
        types[name] += 1
        exp.Next()
    return {k.replace("Geom_", ""): v for k, v in types.items()}


def mass_props(shape):
    p = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, p)
    com = p.CentreOfMass()
    return {"volume": p.Mass(), "com": [com.X(), com.Y(), com.Z()]}


def face_area_sum(shape):
    p = GProp_GProps()
    BRepGProp.SurfaceProperties_s(shape, p)
    return p.Mass()


def is_each_face_planar(shape):
    """All faces planar? (rectangle extrude -> 6 planar faces)."""
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    n_planar = 0
    n_total = 0
    while exp.More():
        f = TopoDS.Face(exp.Current())
        adaptor = BRep_Tool.Surface_s(f)
        # a planar face has type Geom_Plane
        if adaptor.DynamicType().Name() == "Geom_Plane":
            n_planar += 1
        n_total += 1
        exp.Next()
    return n_planar, n_total


def euler_characteristic(v, e, f):
    """For a single closed solid: V - E + F = 2."""
    return v - e + f


def main():
    shape, reader = load_shape()

    body = count_topo_unique(shape, TopAbs_SOLID)
    shell = count_topo_unique(shape, TopAbs_SHELL)
    face = count_topo_unique(shape, TopAbs_FACE)
    edge = count_topo_unique(shape, TopAbs_EDGE)
    vertex = count_topo_unique(shape, TopAbs_VERTEX)
    wire = count_topo_unique(shape, TopAbs_WIRE)
    bb = bbox(shape)
    smap = surface_type_map(shape)
    mp = mass_props(shape)
    area = face_area_sum(shape)
    n_planar, n_total = is_each_face_planar(shape)

    # Convert STEP (mm) to cm to match Fusion JSON units
    scale = MM_TO_CM

    # dimension along the sketch-plane normal = the extrude height
    nx, ny, nz = SKETCH_NORMAL
    axis_index = [nx, ny, nz].index(1.0)
    height_along_normal = round(bb["size"][axis_index] * scale, 6)
    # in-plane rectangle side = the two non-extrude dims (should both be 1.9)
    in_plane = [round(s * scale, 6) for i, s in enumerate(bb["size"]) if i != axis_index]

    result = {
        "sample": "100243_9fb796fe_0005",
        "step_file": STEP_FILE.name,
        "step_unit": "mm (converted to cm via *0.1 for GT comparison)",
        "design_intent": {
            "sketch_normal": list(SKETCH_NORMAL),
            "rect_side": RECT_SIDE,
            "extrude_distance": EXTRUDE_DISTANCE,
            "extent_type": EXTENT_TYPE,
        },
        "A_topology": {
            "body_count": body,
            "shell_count": shell,
            "face_count": face,
            "edge_count": edge,
            "vertex_count": vertex,
            "wire_count": wire,
        },
        "B_dimension": {
            "bbox_min_cm": [round(v * scale, 6) for v in bb["min"]],
            "bbox_max_cm": [round(v * scale, 6) for v in bb["max"]],
            "bbox_size_cm": [round(v * scale, 6) for v in bb["size"]],
            "height_along_extrude_normal_cm": height_along_normal,
            "in_plane_sides_cm": in_plane,
            "volume_cm3": round(mp["volume"] * scale**3, 4),
            "surface_area_cm2": round(area * scale**2, 4),
            "center_of_mass_cm": [round(v * scale, 6) for v in mp["com"]],
        },
        "C_feature": {
            "surface_types": smap,
            "all_faces_planar": (n_planar == n_total),
            "planar_face_count": n_planar,
            "total_face_count": n_total,
            "cylinder_face_count": smap.get("CylindricalSurface", 0),
        },
        "D_health": {
            "is_solid": body >= 1,
            "euler_V_E_F": [vertex, edge, face],
            "euler_characteristic": euler_characteristic(vertex, edge, face),
            "expected_euler_for_closed_solid": 2,
        },
    }

    out = Path(__file__).resolve().parent / "kqp_result.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("\nKQP result written to", out.name)


if __name__ == "__main__":
    main()
