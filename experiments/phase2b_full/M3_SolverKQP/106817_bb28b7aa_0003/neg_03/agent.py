import cadquery as cq

# Design Plan: extruded circle (disk)
# Dimensions:
#   radius = 4.7117 mm (from profile radius, note: the center_uv is given as [50.800002, 63.500002] but that is in sketch plane coordinates)
#   extrude distance = 12.192 mm
# The profile circle center_uv is [5.080000162124634, 6.350000202655792] in the local frame (u,v).
# The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0].
# So the sketch plane is XZ (u along X, v along -Z), extrude along +w = +Y.
# We'll create a circle centered at (5.08, 6.35) in the XZ plane, then extrude in Y direction.

# Build the result
result = (
    cq.Workplane("XZ")
    .circle(4.7117)
    .extrude(12.192)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\106817_bb28b7aa_0003\\neg_03/generated.step")
