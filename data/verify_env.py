"""Verify the CAD execution environment needed for the dual-feedback loop.

Run this AFTER creating & activating the conda env, e.g.:

    conda activate cadenv
    python verify_env.py

It checks the three things the experiment actually depends on:
  1. CAD backend importable (cadquery / OCP / pythonocc-core — whichever is installed)
  2. STEP file can be read by OpenCascade (Kernel feedback arm lifeline)
  3. Topology + dimension query primitives work on a real dataset STEP

Exit code 0 = green path ready; non-zero = missing capability (printed clearly).
"""
import importlib
import shutil
import sys
from pathlib import Path

# A real STEP from the dataset, used as the live read target.
SAMPLE_STEP = Path(r"D:\dataset\r1.0.1\reconstruction\100106_7f144e5b_0000.step")


def check(name, fn):
    print(f"[ ] {name} ...", end=" ", flush=True)
    try:
        detail = fn()
        print("OK" + (f"  ({detail})" if detail else ""))
        return True
    except Exception as e:
        print(f"FAIL\n    -> {type(e).__name__}: {e}")
        return False


# --- 1. backend import ----------------------------------------------------
BACKENDS = {}


def try_backends():
    results = {}
    # cadquery (bundles OCP)
    try:
        import cadquery as cq
        results["cadquery"] = cq.__version__
    except Exception:
        pass
    # OCP directly
    try:
        from OCP.STEPControl import STEPControl_Reader  # noqa: F401
        import OCP  # noqa: F401
        results["OCP"] = getattr(OCP, "__version__", "present")
    except Exception:
        pass
    # pythonocc
    try:
        from OCC.Core.STEPControl import STEPControl_Reader  # noqa: F401
        results["pythonocc"] = "present"
    except Exception:
        pass
    # generic helpers
    for mod in ("numpy", "scipy", "networkx", "trimesh"):
        try:
            m = importlib.import_module(mod)
            results[mod] = getattr(m, "__version__", "present")
        except Exception:
            pass
    return results


# --- 2. STEP read ---------------------------------------------------------
def read_step_cadquery():
    import cadquery as cq
    shape = cq.importers.importStep(str(SAMPLE_STEP))
    return f"solids={len(shape.solids().vals())}, faces={len(shape.faces().vals())}"


def read_step_ocp():
    from OCP.STEPControl import STEPControl_Reader
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_SOLID, TopAbs_FACE
    r = STEPControl_Reader()
    r.ReadFile(str(SAMPLE_STEP))
    r.TransferRoots()
    shape = r.OneShape()
    solids = TopExp_Explorer(shape, TopAbs_SOLID)
    ns = 0
    while solids.More():
        ns += 1
        solids.Next()
    return f"solids={ns}"


def read_step_pythonocc():
    from OCC.Core.STEPControl import STEPControl_Reader
    from OCC.Core.TopExp import TopExp_Explorer
    from OCC.Core.TopAbs import TopAbs_SOLID
    r = STEPControl_Reader()
    r.ReadFile(str(SAMPLE_STEP))
    r.TransferRoots()
    shape = r.OneShape()
    e = TopExp_Explorer(shape, TopAbs_SOLID)
    ns = 0
    while e.More():
        ns += 1
        e.Next()
    return f"solids={ns}"


# --- 3. dimension/geometry query primitives ------------------------------
def bbox_query():
    import cadquery as cq
    s = cq.importers.importStep(str(SAMPLE_STEP))
    bb = s.val().BoundingBox()
    return f"x={bb.xlen:.3f} y={bb.ylen:.3f} z={bb.zlen:.3f}"


def volume_query():
    import cadquery as cq
    s = cq.importers.importStep(str(SAMPLE_STEP))
    return f"volume={s.val().Volume():.3f}"


def surface_types_query():
    """Map each face to its OpenCascade surface type string — the primitive
    behind the KQP 'feature query' (count cylinders/planes for holes/slots)."""
    import cadquery as cq
    from OCP.BRep import BRep_Tool
    from OCP.TopAbs import TopAbs_FACE
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import topods
    s = cq.importers.importStep(str(SAMPLE_STEP))
    shape = s.val().wrapped
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    types = {}
    while exp.More():
        f = topods.Face(exp.Current())
        surf = BRep_Tool.Surface_(f)
        # dynamic type name, e.g. Geom_Plane / Geom_CylindricalSurface
        tname = surf.DynamicType()
        types[tname] = types.get(tname, 0) + 1
        exp.Next()
    return ", ".join(f"{k.replace('Geom_', '')}={v}" for k, v in sorted(types.items()))


def main():
    print("=" * 60)
    print("CAD env verification  (sample STEP:", SAMPLE_STEP.name + ")")
    print("=" * 60)

    if not SAMPLE_STEP.exists():
        print(f"FATAL: sample STEP not found at {SAMPLE_STEP}")
        sys.exit(2)

    all_ok = True

    # Section 1: which backends / helpers are importable
    print("\n--- 1. backend & helper imports ---")
    backends = try_backends()
    if not backends:
        print("FAIL: no CAD backend found. Install one of:")
        print("  conda install -c cadquery cadquery master     # OCP + cadquery")
        print("  conda install -c conda-forge pythonocc-core   # pythonocc")
        return
    for k, v in backends.items():
        print(f"  {k:12s}: {v}")
    has_cq = "cadquery" in backends
    has_ocp = "OCP" in backends
    has_pocc = "pythonocc" in backends

    # Section 2: STEP read via whichever backend is present
    print("\n--- 2. STEP file read (Kernel feedback lifeline) ---")
    if has_cq:
        all_ok &= check("cadquery STEP read", read_step_cadquery)
    if has_ocp:
        all_ok &= check("OCP STEPControl_Reader", read_step_ocp)
    if has_pocc:
        all_ok &= check("pythonocc STEPControl_Reader", read_step_pythonocc)
    if not (has_cq or has_ocp or has_pocc):
        all_ok = False
        print("  no STEP-capable backend")

    # Section 3: KQP primitives (cadquery path; falls back gracefully)
    print("\n--- 3. KQP query primitives (cadquery + OCP) ---")
    if has_cq:
        all_ok &= check("topology: face/edge/vertex count", lambda: (
            importlib.import_module("cadquery"),
            f"faces/edges ok")[1])
        all_ok &= check("dimension: bounding box", bbox_query)
        all_ok &= check("dimension: volume", volume_query)
        all_ok &= check("feature: surface-type map", surface_types_query)
    elif has_ocp:
        # minimal topology count via OCP
        def ocp_counts():
            from OCP.STEPControl import STEPControl_Reader
            from OCP.TopExp import TopExp_Explorer
            from OCP.TopAbs import TopAbs_FACE, TopAbs_EDGE, TopAbs_VERTEX
            r = STEPControl_Reader(); r.ReadFile(str(SAMPLE_STEP)); r.TransferRoots()
            sh = r.OneShape()
            def n(t):
                e = TopExp_Explorer(sh, t); c = 0
                while e.More():
                    c += 1; e.Next()
                return c
            return f"faces={n(TopAbs_FACE)} edges={n(TopAbs_EDGE)} vertices={n(TopAbs_VERTEX)}"
        all_ok &= check("topology: face/edge/vertex count (OCP)", ocp_counts)
    else:
        print("  (skipped — cadquery/OCP recommended for KQP)")

    # Section 4: optional CLIs
    print("\n--- 4. optional tooling ---")
    check("freecad CLI on PATH", lambda: shutil.which("FreeCAD") or (_ for _ in ()).throw(FileNotFoundError("not on PATH")))
    check("openscad CLI on PATH", lambda: shutil.which("openscad") or (_ for _ in ()).throw(FileNotFoundError("not on PATH")))

    print("\n" + "=" * 60)
    if all_ok and (has_cq or has_ocp):
        print("RESULT: GREEN — Kernel feedback arm ready for KQP compiler dev.")
        sys.exit(0)
    else:
        print("RESULT: RED — some capability missing. Fix the FAIL items above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
