import cadquery as cq

# Build the stadium profile (rounded rectangle with semicircular ends)
# The stadium has straight length 500 mm and radius 50 mm (from dimensions)
# But the profile curves use radius 5 and straight length 50 (scaled?)
# The design plan shows curves with radius 5 and straight length 50 in UV space.
# However dimensions say straight_length=500, radius=50.
# The UV coordinates in curves: center_uv (0,0) radius 5, line from (0,-5) to (50,-5), etc.
# This suggests a 10x50 rectangle with semicircular ends of radius 5.
# But the dimensions say 500 and 50. Likely the UV is a unit representation scaled by 10.
# We'll use the explicit curve data: radius 5, straight length 50 -> overall width = 50+5+5=60, height=10.
# But the validation expects span_u=600, span_v=100, span_w=100.
# So scaling factor = 10. So we build with radius=50, straight_length=500.

# Build the stadium profile using CadQuery's 2D primitives
# We'll create a workplane and draw the shape

result = (
    cq.Workplane("XY")
    .center(0, 0)
    .moveTo(0, -50)  # start at bottom-left of straight section
    .lineTo(500, -50)  # bottom straight
    .threePointArc((500 + 50, 0), (500, 50))  # right semicircle (radius 50)
    .lineTo(0, 50)  # top straight
    .threePointArc((-50, 0), (0, -50))  # left semicircle (radius 50)
    .close()
    .extrude(100.0)  # extrude along Z (w direction) by 100 mm
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M3_SolverKQP\104453_aba0f2d1_0002\neg_03/generated.step")