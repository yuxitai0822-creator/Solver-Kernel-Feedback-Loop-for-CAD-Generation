import cadquery as cq
from cadquery import exporters

# Design Plan: Drone Leg - square strut
# Dimensions: 19.0 x 19.0 x 130.0 mm (rectangle profile extruded)
# The previous script had the rectangle on XY plane, but the design plan specifies:
#   u_dir = [1,0,0] (X), v_dir = [0,0,-1] (negative Z), w_dir = [0,1,0] (Y)
# This means the profile is on the X-Z plane (normal = Y), and extrude is along Y (+w).
# The previous script used XY plane (normal=Z) which swapped Y and Z dimensions.
# We now use XZ plane so that:
#   - u (length_u=19) maps to X
#   - v (width_v=19) maps to Z
#   - w (extrude=130) maps to Y

# Profile rectangle dimensions (from design plan)
length_u = 19.0  # mm (along X)
width_v = 19.0   # mm (along Z)
extrude_distance = 130.0  # mm (along Y)

# Build the part on XZ plane (normal = Y), extrude along Y
result = (cq.Workplane("XZ")
    .rect(length_u, width_v, centered=True)
    .extrude(extrude_distance)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\100243_9fb796fe_0006\neg_01\iter_01/generated.step"
exporters.export(result, OUT_STEP_PATH)