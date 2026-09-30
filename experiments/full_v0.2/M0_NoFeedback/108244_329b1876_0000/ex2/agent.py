import cadquery as cq

# Design Plan: extruded rectangle (flat plate/panel)
# Dimensions: length_u = 1219.2 mm, width_v = 2590.8 mm, extrude_distance = 44.45 mm
# The profile is a rectangle in the UV plane, then extruded along +W direction.
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# The rectangle corners in UV: 
#   start_uv = (121.17356129030935, 31.299551148092803)
#   end_uv = (-0.7464387096940412, 290.379551148076)
# So width in U = 121.17356129030935 - (-0.7464387096940412) = 121.92 cm = 1219.2 mm
# Height in V = 290.379551148076 - 31.299551148092803 = 259.08 cm = 2590.8 mm
# The rectangle is defined by 4 lines forming a closed loop.
# We'll create a workplane on the XY plane (since u_dir = X, v_dir = -Z, w_dir = Y)
# Actually: u_dir = X, v_dir = -Z, w_dir = Y means the profile lies in the X-Z plane (with v reversed).
# To simplify, we'll create the rectangle in the XY plane and then rotate/translate as needed.
# But the simplest approach: create a box centered at origin with the given dimensions, then translate.
# The rectangle corners in UV: (121.17356129030935, 31.299551148092803) and (-0.7464387096940412, 290.379551148076)
# Center in UV: ((121.17356129030935 + (-0.7464387096940412))/2, (31.299551148092803 + 290.379551148076)/2)
# = (60.213561290307654, 160.8395511480844)
# Size in U: 121.92, Size in V: 259.08
# Since v_dir = (0,0,-1), the V coordinate maps to -Z.
# So the rectangle in 3D: center at (60.213561290307654, 0, -160.8395511480844) with size (121.92, 259.08) in X and Z.
# Then extrude along Y (w_dir) by 44.45 mm.

# Build the result
result = (
    cq.Workplane("XY")
    .center(60.213561290307654, 0)
    .rect(121.92, 259.08)
    .extrude(44.45)
)

# Export to STEP
cq.exporters.export(result, "D:\\\\PythonProgramming\\\\CAD Generation\\\\Constraint-grounded agentic CAD generation\\\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\\\experiments\\\\phase2b_full\\\\M0_NoFeedback\\\\108244_329b1876_0000\\\\ex2/generated.step")
