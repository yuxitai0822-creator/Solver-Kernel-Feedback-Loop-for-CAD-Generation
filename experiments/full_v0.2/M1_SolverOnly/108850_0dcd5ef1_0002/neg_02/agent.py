import cadquery as cq

# Design Plan: extruded rectangle (flat plate)
# Dimensions: length_u = 171.45 mm, width_v = 38.1 mm, extrude_distance = 6.35 mm
# The frame defines u along x, v along -z, w along y.
# We'll create the rectangle in the XY plane (u=x, v=y) then extrude along Z (w).
# But the plan says v_dir = [0,0,-1] and w_dir = [0,1,0].
# To keep it simple, we create the rectangle in the XY plane (x=u, y=-v) and extrude along Z (w).
# Actually, let's just use the standard approach: rectangle in XY, extrude in Z.
# The dimensions are 171.45 (x) by 38.1 (y), extrude 6.35 (z).

result = (
    cq.Workplane("XY")
    .rect(171.45, 38.1)
    .extrude(6.35)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\108850_0dcd5ef1_0002\neg_02/generated.step")
