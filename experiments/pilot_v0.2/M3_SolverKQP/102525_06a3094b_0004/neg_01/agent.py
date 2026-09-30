import cadquery as cq

# Design Plan: SOP-28 (1) rectangular prism
# Dimensions: length_u = 8.5 mm, width_v = 18.0 mm, extrude_distance = 2.5 mm
# Frame: u_dir = [1, 0, 0], v_dir = [0, 0, -1], w_dir = [0, 1, 0]
# Origin convention: bbox_min_corner

# The profile rectangle spans from u=-0.425 to u=0.425 (length 8.5mm) and v=-0.9 to v=0.9 (width 18.0mm).
# In CadQuery, we sketch on the XZ plane (u=X, v=Z) centered at origin, then extrude along Y (w_dir).
# Since v_dir is [0, 0, -1], the Z axis in CadQuery maps to -v. 
# To ensure the bbox_min_corner is at the origin, we shift the sketch by half the dimensions in the positive Z direction.

result = (
    cq.Workplane("XZ")
    .center(0, 9.0)  # Shift center up by half width (18.0/2 = 9.0) so bbox Z_min is 0
    .rect(8.5, 18.0)  # Length along X (u), Width along Z (v)
    .extrude(2.5)     # Extrude along +Y (w_dir)
)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M3_SolverKQP\102525_06a3094b_0004\neg_01/generated.step"
cq.exporters.export(result, OUT_STEP_PATH)
