"""geometry_backend.py — low-level OCCT geometry queries.

Each function takes a TopoDS_Shape (or face/edge) and returns a primitive
value (int, float, bool, list). These are the atomic building blocks used
by query_dispatcher.

OCCT/OCP conventions (OCP 7.8.x, cadquery 2.8.x):
  - TopTools_IndexedMapOfShape for dedup counting (TopExp_Explorer double-counts)
  - BRepBndLib.Add_s for axis-aligned bbox
  - BRepAdaptor_Surface for surface type / cylinder radius
  - BRepGProp.VolumeProperties_s(S, GProp_GProps) for volume + centroid
  - BRepCheck_Analyzer for shape validity
"""
from __future__ import annotations
import math
from typing import Optional

from OCP.TopoDS import TopoDS, TopoDS_Shape, TopoDS_Solid, TopoDS_Face
from OCP.TopTools import TopTools_IndexedMapOfShape
from OCP.TopAbs import (
    TopAbs_SOLID, TopAbs_FACE, TopAbs_EDGE, TopAbs_VERTEX,
    TopAbs_WIRE, TopAbs_SHELL, TopAbs_SHAPE,
)
from OCP.TopExp import TopExp_Explorer
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder, GeomAbs_Sphere, GeomAbs_Cone, GeomAbs_Torus
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.gp import gp_Pnt, gp_Vec, gp_Dir, gp_Ax1, gp_Pln


# ---------------------------------------------------------------------------
# Shape counting helpers
# ---------------------------------------------------------------------------

def count_subshapes(shape: TopoDS_Shape, shape_type) -> int:
    """Count unique sub-shapes of a given type using IndexedMapOfShape (dedup)."""
    m = TopTools_IndexedMapOfShape()
    ex = TopExp_Explorer(shape, shape_type)
    while ex.More():
        m.Add(ex.Current())
        ex.Next()
    return m.Size()


def get_solid_count(shape: TopoDS_Shape) -> int:
    return count_subshapes(shape, TopAbs_SOLID)


def get_face_count(shape: TopoDS_Shape) -> int:
    return count_subshapes(shape, TopAbs_FACE)


def get_edge_count(shape: TopoDS_Shape) -> int:
    return count_subshapes(shape, TopAbs_EDGE)


def get_vertex_count(shape: TopoDS_Shape) -> int:
    return count_subshapes(shape, TopAbs_VERTEX)


def get_shell_count(shape: TopoDS_Shape) -> int:
    return count_subshapes(shape, TopAbs_SHELL)


def get_wire_count(shape: TopoDS_Shape) -> int:
    return count_subshapes(shape, TopAbs_WIRE)


# ---------------------------------------------------------------------------
# Bounding box
# ---------------------------------------------------------------------------

def get_axis_aligned_bbox(shape: TopoDS_Shape) -> tuple:
    """Return (xmin, ymin, zmin, xmax, ymax, zmax) in shape's native units."""
    bb = Bnd_Box()
    BRepBndLib.Add_s(shape, bb)
    return bb.Get()


def get_bbox_size_along_world_axis(shape: TopoDS_Shape, axis: str) -> float:
    """Get bbox span along a world axis ('x', 'y', or 'z')."""
    xmin, ymin, zmin, xmax, ymax, zmax = get_axis_aligned_bbox(shape)
    if axis == "x":
        return xmax - xmin
    if axis == "y":
        return ymax - ymin
    if axis == "z":
        return zmax - zmin
    raise ValueError(f"Unknown axis: {axis}")


def get_bbox_size_along_frame_axis(
    shape: TopoDS_Shape, frame_axis: str,
    u_dir: list, v_dir: list, w_dir: list
) -> float:
    """Get bbox span along a body-frame axis ('u', 'v', or 'w').

    Uses BBOX CORNER projection: take the 8 corners of the axis-aligned
    bounding box, project each onto the frame direction, return max-min.

    This is more robust than vertex projection for curved surfaces (circles,
    cylinders) where the actual vertices lie on the axis, not on the perimeter.
    For axis-aligned frames, this reduces to the world-axis bbox span.
    """
    axis_map = {"u": u_dir, "v": v_dir, "w": w_dir}
    if frame_axis not in axis_map:
        raise ValueError(f"Unknown frame axis: {frame_axis}")
    direction = axis_map[frame_axis]
    dir_vec = (direction[0], direction[1], direction[2])

    # Get axis-aligned bbox
    xmin, ymin, zmin, xmax, ymax, zmax = get_axis_aligned_bbox(shape)

    # Project all 8 bbox corners onto the frame direction
    projections = []
    for x in (xmin, xmax):
        for y in (ymin, ymax):
            for z in (zmin, zmax):
                proj = x * dir_vec[0] + y * dir_vec[1] + z * dir_vec[2]
                projections.append(proj)

    return max(projections) - min(projections)


# ---------------------------------------------------------------------------
# Surface types and cylinder radius
# ---------------------------------------------------------------------------

def get_surface_types(shape: TopoDS_Shape) -> list[str]:
    """Return a list of surface type names for each face."""
    m = TopTools_IndexedMapOfShape()
    ex = TopExp_Explorer(shape, TopAbs_FACE)
    while ex.More():
        m.Add(ex.Current())
        ex.Next()

    names = []
    for i in range(1, m.Size() + 1):
        f = TopoDS.Face(m.FindKey(i))
        adaptor = BRepAdaptor_Surface(f, True)
        t = adaptor.GetType()
        names.append(str(t).split(".")[-1])  # e.g. 'GeomAbs_Plane' -> 'Plane'
    return names


def get_cylinder_radii(shape: TopoDS_Shape) -> list[float]:
    """Return a sorted list of unique cylinder face radii."""
    m = TopTools_IndexedMapOfShape()
    ex = TopExp_Explorer(shape, TopAbs_FACE)
    while ex.More():
        m.Add(ex.Current())
        ex.Next()

    radii = []
    for i in range(1, m.Size() + 1):
        f = TopoDS.Face(m.FindKey(i))
        adaptor = BRepAdaptor_Surface(f, True)
        t = adaptor.GetType()
        if t == GeomAbs_Cylinder:
            cyl = adaptor.Cylinder()
            radii.append(cyl.Radius())
    return sorted(set(round(r, 6) for r in radii))


def get_cylinder_radius_by_selector(shape: TopoDS_Shape, selector: str) -> Optional[float]:
    """Get cylinder radius by selector: 'outer' = largest, 'inner' = smallest."""
    radii = get_cylinder_radii(shape)
    if not radii:
        return None
    if selector == "outer":
        return max(radii)
    if selector == "inner":
        return min(radii)
    if selector == "" or selector is None:
        # single cylinder: return the only radius
        if len(radii) == 1:
            return radii[0]
        # multiple: return smallest (conservative)
        return min(radii)
    raise ValueError(f"Unknown selector: {selector}")


# ---------------------------------------------------------------------------
# Through-void count
# ---------------------------------------------------------------------------

def get_through_void_count(shape: TopoDS_Shape) -> int:
    """Estimate the number of through-voids (holes) in the solid.

    Heuristic: count total wires across all faces, subtract the number of faces
    (each face has at least 1 outer wire), divide by 2 (each through-void has
    2 inner wires: one on each end cap).

    For a rectangle (no holes): faces=6, total_wires=6 -> (6-6)/2 = 0
    For an annulus (1 hole): faces=4, total_wires=6 -> (6-4)/2 = 1
    For stadium+2holes: faces=?, total_wires=? -> should give 2

    Note: this heuristic works for extrusion-based solids where through-voids
    are created by inner profile rings. May need refinement for other cases.
    """
    m_f = TopTools_IndexedMapOfShape()
    ex = TopExp_Explorer(shape, TopAbs_FACE)
    while ex.More():
        m_f.Add(ex.Current())
        ex.Next()

    num_faces = m_f.Size()
    if num_faces == 0:
        return 0

    total_wires = 0
    for i in range(1, num_faces + 1):
        f = TopoDS.Face(m_f.FindKey(i))
        m_w = TopTools_IndexedMapOfShape()
        ex_w = TopExp_Explorer(f, TopAbs_WIRE)
        while ex_w.More():
            m_w.Add(ex_w.Current())
            ex_w.Next()
        total_wires += m_w.Size()

    extra_wires = total_wires - num_faces
    if extra_wires < 0:
        return 0
    return extra_wires // 2


# ---------------------------------------------------------------------------
# Validity and solid checks
# ---------------------------------------------------------------------------

def is_solid_shape(shape: TopoDS_Shape) -> bool:
    """True if the top-level shape is a TopAbs_SOLID."""
    return shape.ShapeType() == TopAbs_SOLID


def is_occt_valid(shape: TopoDS_Shape) -> bool:
    """Run BRepCheck_Analyzer and return IsValid()."""
    checker = BRepCheck_Analyzer(shape, True)
    return checker.IsValid()


def are_all_faces_planar(shape: TopoDS_Shape) -> bool:
    """True if every face surface is a Geom_Plane."""
    m = TopTools_IndexedMapOfShape()
    ex = TopExp_Explorer(shape, TopAbs_FACE)
    while ex.More():
        m.Add(ex.Current())
        ex.Next()
    for i in range(1, m.Size() + 1):
        f = TopoDS.Face(m.FindKey(i))
        adaptor = BRepAdaptor_Surface(f, True)
        if adaptor.GetType() != GeomAbs_Plane:
            return False
    return True


# ---------------------------------------------------------------------------
# Volume and centroid
# ---------------------------------------------------------------------------

def get_volume(shape: TopoDS_Shape) -> float:
    """Volume of the solid (0 if not a closed solid)."""
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props, True, True)
    return props.Mass()


def get_centroid(shape: TopoDS_Shape) -> tuple:
    """Return (x, y, z) centroid of the solid."""
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props, True, True)
    com = props.CentreOfMass()
    return (com.X(), com.Y(), com.Z())


def is_symmetric_about_plane(
    shape: TopoDS_Shape,
    plane_normal: list,
    plane_origin: list,
    tol: float = 0.01
) -> bool:
    """Check if body centroid lies on the given plane (within tolerance).

    For symmetric extrudes (extent_type=symmetric), the body should straddle
    the sketch plane, so its centroid should be ON the plane.
    """
    cx, cy, cz = get_centroid(shape)
    # Distance from point to plane: |dot(centroid - origin, normal)|
    dx = cx - plane_origin[0]
    dy = cy - plane_origin[1]
    dz = cz - plane_origin[2]
    dist = abs(dx * plane_normal[0] + dy * plane_normal[1] + dz * plane_normal[2])
    return dist < tol


# ---------------------------------------------------------------------------
# Euler characteristic
# ---------------------------------------------------------------------------

def get_euler_characteristic(shape: TopoDS_Shape) -> int:
    """V - E + F for the shape."""
    v = get_vertex_count(shape)
    e = get_edge_count(shape)
    f = get_face_count(shape)
    return v - e + f
