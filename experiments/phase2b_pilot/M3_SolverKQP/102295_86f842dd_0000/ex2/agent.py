import cadquery as cq

# Stadium profile parameters (in mm, converted from cm)
straight_length = 28.0
radius = 10.0
extrude_distance = 4.0

# Build the stadium profile using two semicircles and two lines
# The frame maps u -> X, v -> -Z, w -> Y
# In the XZ plane (u, -v), the stadium spans from X=0 to X=48, Z=-20 to Z=0
# Origin is at bbox_min_corner (0, 0, -20) in the XZ plane

result = (
    cq.Workplane("XZ")
    .semicircle(radius, 0)  # Left semicircle centered at (10, 0)
    .lineTo(straight_length, 0)  # Top line to right semicircle start
    .semicircle(radius, 180)  # Right semicircle centered at (38, 0)
    .lineTo(0, 0)  # Bottom line back to left semicircle start
    .close()
    .extrude(extrude_distance)  # Extrude along +Y (which is +w)
)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M3_SolverKQP\102295_86f842dd_0000\ex2/generated.step"
cq.exporters.export(result, OUT_STEP_PATH)