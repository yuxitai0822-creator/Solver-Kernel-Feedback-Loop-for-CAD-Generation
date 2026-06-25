"""KQP for sample 100243_9fb796fe_0005 (1.9x1.9 rectangle, OneSide extrude 20.0).

This Kernel Query Program reads the reconstructed STEP via OpenCascade (OCP) and
issues structured queries that mirror the design intent:

  Step1  sketch on plane normal=(0,1,0), u=(0,0,1), v=(1,0,0)
          -> D_health: BRepCheck_Analyzer validity
  Step2  1.9 x 1.9 rectangle (4 lines, 1 profile)
          -> A_topology: unique topo counts; B_dimension: aligned bbox
  Step3  horizontal/vertical constraints
          -> E_constraint: edge-level direction dot-product orthogonality check
  Step4  driving dims width=height=1.9
          -> B_dimension: vertex projection onto u/v/normal axes
  Step5  select closed profile
          -> A_topology: 1 body, 1 shell, 1 wire per face loop
  Step6  extrude 20.0 along normal, new body
          -> B_dimension: height along normal via vertex projection

Output: a structured JSON report of every query result. No pass/fail here — the
companion verify script compares these to the JSON GT.

Key design choices (from exp01 lessons):
  - TopTools_IndexedMapOfShape for unique (non-shared) sub-shape counting
  - STEP internal unit mm; JSON GT unit cm; conversion factor 0.1
  - Vertex projection onto normal/u/v basis for arbitrary-axis robust dimensions
  - Edge-level direction dot products for constraint orthogonality verification
  - BRepCheck_Analyzer for formal OCCT shape validity
"""
import json
import math
from collections import Counter
from pathlib import Path

from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import (TopAbs_FACE, TopAbs_EDGE, TopAbs_VERTEX,
                         TopAbs_SHELL, TopAbs_SOLID, TopAbs_WIRE)
from OCP.TopExp import TopExp_Explorer, TopExp
from OCP.TopTools import TopTools_IndexedMapOfShape
from OCP.TopoDS import TopoDS, TopoDS_Vertex
from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.gp import gp_Pnt, gp_Dir, gp_Vec
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.GeomAbs import GeomAbs_Line

STEP_FILE = Path(__file__).resolve().parent / "100243_9fb796fe_0005.step"

# Design intent from the modeling sequence
SKETCH_NORMAL = (0.0, 1.0, 0.0)   # plane normal (拉伸方向)
SKETCH_U_DIR  = (0.0, 0.0, 1.0)   # plane u basis vector
SKETCH_V_DIR  = (1.0, 0.0, 0.0)   # plane v basis vector
EXTRUDE_DISTANCE = 20.0
RECT_SIDE = 1.9
EXTENT_TYPE = "OneSideFeatureExtentType"

# STEP internal unit is mm; Fusion JSON properties are in cm
MM_TO_CM = 0.1


# ---------------------------------------------------------------------------
# 0. helpers
# ---------------------------------------------------------------------------

def vec_len(v):
    return math.sqrt(sum(c * c for c in v))


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def normalize(v):
    l = vec_len(v)
    return [c / l for c in v] if l > 1e-12 else v


def proj_along(point, axis):
    """Scalar projection of a 3D point onto a unit-direction axis."""
    return dot(point, axis)


# ---------------------------------------------------------------------------
# A. topology queries (unique sub-shape counting)
# ---------------------------------------------------------------------------

def load_shape():
    """Read STEP -> OCCT TopoDS_Shape.  Returns (shape, reader)."""
    r = STEPControl_Reader()
    status = r.ReadFile(str(STEP_FILE))
    if not status:
        raise RuntimeError(f"STEP read failed (status={status})")
    r.TransferRoots()
    return r.OneShape(), r


def count_topo_unique(shape, t):
    """Count unique (non-shared) sub-shapes of type *t*.

    Uses TopTools_IndexedMapOfShape so shared edges/vertices are counted
    only once — matching Fusion's ``*_count`` semantics.
    """
    m = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, t, m)
    return m.Extent()


# ---------------------------------------------------------------------------
# B. dimension queries (vertex-projection based, works for any normal)
# ---------------------------------------------------------------------------

def bbox_axis_aligned(shape):
    """AABB (axis-aligned bounding box).  Kept as reference; NOT used for
    the primary height/in-plane-size queries (those use vertex projection)."""
    b = Bnd_Box()
    BRepBndLib.Add_s(shape, b)
    xmin, ymin, zmin, xmax, ymax, zmax = b.Get()
    return {
        "min": [xmin, ymin, zmin],
        "max": [xmax, ymax, zmax],
        "size": [xmax - xmin, ymax - ymin, zmax - zmin],
    }


def collect_vertices(shape):
    """Return list of (x, y, z) for every unique vertex."""
    m = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, TopAbs_VERTEX, m)
    pts = []
    for i in range(1, m.Extent() + 1):
        vt = TopoDS.Vertex(m.FindKey(i))
        p = BRep_Tool.Pnt_s(vt)
        pts.append((p.X(), p.Y(), p.Z()))
    return pts


def oriented_dimensions(vertices, normal, u_dir, v_dir):
    """Project all vertices onto the three sketch-frame axes and compute
    the span (max projection − min projection) along each axis.

    This works for **arbitrary** sketch normals (not just axis-aligned).

    Returns:
        dict with 'height_along_normal', 'span_u', 'span_v'  (in STEP mm).
    """
    n = normalize(normal)
    u = normalize(u_dir)
    v = normalize(v_dir)

    proj_n = [proj_along(p, n) for p in vertices]
    proj_u = [proj_along(p, u) for p in vertices]
    proj_v = [proj_along(p, v) for p in vertices]

    return {
        "height_along_normal_mm": max(proj_n) - min(proj_n),
        "span_u_mm":               max(proj_u) - min(proj_u),
        "span_v_mm":               max(proj_v) - min(proj_v),
    }


# ---------------------------------------------------------------------------
# C. feature / surface-type queries
# ---------------------------------------------------------------------------

def surface_type_map(shape):
    """Map each face's underlying surface to its OCCT dynamic type name."""
    types = Counter()
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        f = TopoDS.Face(exp.Current())
        surf = BRep_Tool.Surface_s(f)
        name = surf.DynamicType().Name()
        types[name] += 1
        exp.Next()
    return {k.replace("Geom_", ""): v for k, v in types.items()}


def is_each_face_planar(shape):
    """Count planar vs total faces (Geom_Plane)."""
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    n_planar, n_total = 0, 0
    while exp.More():
        f = TopoDS.Face(exp.Current())
        surf = BRep_Tool.Surface_s(f)
        if surf.DynamicType().Name() == "Geom_Plane":
            n_planar += 1
        n_total += 1
        exp.Next()
    return n_planar, n_total


# ---------------------------------------------------------------------------
# D. health queries
# ---------------------------------------------------------------------------

def occt_validity(shape):
    """Use BRepCheck_Analyzer for formal OCCT shape validity."""
    analyzer = BRepCheck_Analyzer(shape)
    return {"is_valid": analyzer.IsValid()}


def euler_characteristic(v, e, f):
    """V - E + F for a closed solid should be 2."""
    return v - e + f


# ---------------------------------------------------------------------------
# E. constraint queries (edge-level direction analysis)
# ---------------------------------------------------------------------------

def edge_direction_map(shape):
    """For every unique edge whose underlying curve is a Geom_Line,
    extract a unit direction vector.

    Returns list of {'edge_index': int, 'direction': [dx,dy,dz]}.
    Non-line edges (arcs, splines) are skipped.
    """
    m = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, TopAbs_EDGE, m)
    lines = []
    for i in range(1, m.Extent() + 1):
        e = TopoDS.Edge(m.FindKey(i))
        adaptor = BRepAdaptor_Curve(e)
        if adaptor.GetType() != GeomAbs_Line:
            continue
        u1, u2 = adaptor.FirstParameter(), adaptor.LastParameter()
        p1 = adaptor.Value(u1)
        p2 = adaptor.Value(u2)
        d = gp_Vec(p1, p2)
        length = d.Magnitude()
        if length < 1e-12:
            continue
        d = gp_Vec(d.XYZ() / length)
        lines.append({
            "edge_index": i,
            "direction": [d.X(), d.Y(), d.Z()],
        })
    return lines


def check_edge_orthogonality(edge_dirs, tol=1e-6):
    """Check pairwise dot products among all straight-edge directions.

    Returns:
        parallel_pairs:   list of (i,j,|dot|) where |dot| ≈ 1
        perpendicular_pairs: list of (i,j,|dot|) where |dot| ≈ 0
    """
    parallel = []
    perp = []
    for a in range(len(edge_dirs)):
        da = edge_dirs[a]["direction"]
        for b in range(a + 1, len(edge_dirs)):
            db = edge_dirs[b]["direction"]
            d = abs(dot(da, db))
            if abs(d - 1.0) < tol:
                parallel.append((a, b, round(d, 6)))
            elif abs(d) < tol:
                perp.append((a, b, round(d, 6)))
    return {"parallel_pairs": parallel, "perpendicular_pairs": perp}


# ---------------------------------------------------------------------------
# mass properties
# ---------------------------------------------------------------------------

def mass_props(shape):
    p = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, p)
    com = p.CentreOfMass()
    return {"volume_mm3": p.Mass(), "com_mm": [com.X(), com.Y(), com.Z()]}


def face_area_sum(shape):
    p = GProp_GProps()
    BRepGProp.SurfaceProperties_s(shape, p)
    return p.Mass()


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    shape, reader = load_shape()

    # --- A: topology (unique counts) ---
    body   = count_topo_unique(shape, TopAbs_SOLID)
    shell  = count_topo_unique(shape, TopAbs_SHELL)
    face   = count_topo_unique(shape, TopAbs_FACE)
    edge   = count_topo_unique(shape, TopAbs_EDGE)
    vertex = count_topo_unique(shape, TopAbs_VERTEX)
    wire   = count_topo_unique(shape, TopAbs_WIRE)

    # --- B: dimensions ---
    bb_axis = bbox_axis_aligned(shape)                    # axis-aligned (reference only)
    vertices = collect_vertices(shape)
    oriented = oriented_dimensions(                      # projection-based (robust)
        vertices, SKETCH_NORMAL, SKETCH_U_DIR, SKETCH_V_DIR
    )
    mp = mass_props(shape)
    area = face_area_sum(shape)
    scale = MM_TO_CM

    # --- C: feature ---
    smap = surface_type_map(shape)
    n_planar, n_total = is_each_face_planar(shape)

    # --- D: health ---
    validity = occt_validity(shape)
    euler = euler_characteristic(vertex, edge, face)

    # --- E: constraint (edge orthogonality) ---
    edge_dirs = edge_direction_map(shape)
    ortho = check_edge_orthogonality(edge_dirs)

    # ---------- assemble result ----------
    result = {
        "sample": "100243_9fb796fe_0005",
        "step_file": STEP_FILE.name,
        "step_unit": "mm (converted to cm via *0.1 for GT comparison)",

        "design_intent": {
            "sketch_normal": list(SKETCH_NORMAL),
            "sketch_u_dir":  list(SKETCH_U_DIR),
            "sketch_v_dir":  list(SKETCH_V_DIR),
            "rect_side": RECT_SIDE,
            "extrude_distance": EXTRUDE_DISTANCE,
            "extent_type": EXTENT_TYPE,
        },

        "A_topology": {
            "body_count":   body,
            "shell_count":  shell,
            "face_count":   face,
            "edge_count":   edge,
            "vertex_count": vertex,
            "wire_count":   wire,
        },

        "B_dimension": {
            # axis-aligned bbox (for reference / debug)
            "bbox_axis_aligned_mm": bb_axis,
            "bbox_axis_aligned_cm": {
                "min":  [round(v * scale, 6) for v in bb_axis["min"]],
                "max":  [round(v * scale, 6) for v in bb_axis["max"]],
                "size": [round(v * scale, 6) for v in bb_axis["size"]],
            },
            # projection-based (robust for arbitrary normals)
            "height_along_normal_cm": round(oriented["height_along_normal_mm"] * scale, 6),
            "span_u_cm":               round(oriented["span_u_mm"] * scale, 6),
            "span_v_cm":               round(oriented["span_v_mm"] * scale, 6),
            "volume_cm3":              round(mp["volume_mm3"] * scale**3, 4),
            "surface_area_cm2":        round(area * scale**2, 4),
            "center_of_mass_cm":       [round(v * scale, 6) for v in mp["com_mm"]],
        },

        "C_feature": {
            "surface_types": smap,
            "all_faces_planar": (n_planar == n_total),
            "planar_face_count": n_planar,
            "total_face_count": n_total,
            "cylinder_face_count": smap.get("CylindricalSurface", 0),
        },

        "D_health": {
            "occt_is_valid":           validity["is_valid"],
            "is_solid":                body >= 1,
            "euler_V_E_F":             [vertex, edge, face],
            "euler_characteristic":    euler,
            "expected_euler_solid":   2,
        },

        "E_constraint": {
            "straight_edge_count":    len(edge_dirs),
            "straight_edge_directions": edge_dirs,
            "parallel_pairs":          ortho["parallel_pairs"],
            "perpendicular_pairs":     ortho["perpendicular_pairs"],
            "total_parallel":          len(ortho["parallel_pairs"]),
            "total_perpendicular":     len(ortho["perpendicular_pairs"]),
        },
    }

    out = Path(__file__).resolve().parent / "kqp_result.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("\nKQP result written to", out.name)


if __name__ == "__main__":
    main()
