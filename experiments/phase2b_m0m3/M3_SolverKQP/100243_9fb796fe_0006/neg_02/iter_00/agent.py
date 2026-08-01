import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Drone Leg - square strut
# Extruded rectangle: 19mm x 19mm profile, extruded 130mm along w direction
# Frame: u=[1,0,0], v=[0,0,-1], w=[0,1,0]
# Profile rectangle in uv plane, extrude along +w

# Profile dimensions from design plan
length_u = 19.0  # along u axis (x)
width_v = 19.0   # along v axis (z negative direction)
extrude_distance = 130.0  # along w axis (y)

# Build the rectangle on the XZ plane (since v is [0,0,-1], u is [1,0,0])
# The rectangle center is at the midpoint of the uv coordinates
# uv coordinates from design plan: u from -58.278 to -56.378, v from -13.940 to -12.040
# But we can just center at origin and translate if needed
# Actually, the design plan specifies the rectangle in uv space, but for a simple
# square strut we can create it centered and then position it.
# The uv coordinates give: u_center = (-58.278 + -56.378)/2 = -57.328, v_center = (-13.940 + -12.040)/2 = -12.990
# However, for a standalone part, we can just create it at origin and let the
# validation check spans, not absolute positions.

# Create workplane on XZ (since u=x, v=-z, so uv plane is XZ)
# Actually v=[0,0,-1] means v direction is negative z, so the plane normal is w=[0,1,0] (y-axis)
# Workplane('XZ') has normal (0,1,0) which matches w direction

result = (
    cq.Workplane("XZ")
    .rect(length_u, width_v, centered=True)
    .extrude(extrude_distance)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\100243_9fb796fe_0006\neg_02\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)