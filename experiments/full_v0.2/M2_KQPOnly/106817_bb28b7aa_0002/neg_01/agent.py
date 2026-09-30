import cadquery as cq

# Design Plan: thumb screw (disk)
# Dimensions:
#   radius = 4.87045 mm (from profiles[0].radius.value)
#   extrude distance = 6.8707 mm (from extrude.distance_total.value)
# Note: The profile center_uv is [114.300004, 0.0] but in part-local frame
# we place the circle at the origin (0,0) for simplicity, then extrude.
# The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0).
# We'll build a cylinder along the w direction (y-axis in world).

radius = 4.87045
height = 6.8707

# Build the result: a cylinder (extruded circle)
result = (
    cq.Workplane("XY")
    .circle(radius)
    .extrude(height)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\106817_bb28b7aa_0002\neg_01/generated.step")
