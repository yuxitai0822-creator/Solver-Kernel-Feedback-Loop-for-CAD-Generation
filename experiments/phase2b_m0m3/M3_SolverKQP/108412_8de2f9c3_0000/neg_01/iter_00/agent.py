import cadquery as cq
from cadquery import exporters

# Design Plan: flat plate/panel, extruded rectangle
# Dimensions: length_u = 2438.4 mm, width_v = 1219.2 mm, extrude_distance = 12.7 mm
# The previous script used 19.05 mm (1.905 cm * 10) which is the perturbed value.
# We must use the original design plan value: 12.7 mm

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\108412_8de2f9c3_0000\neg_01\iter_00/generated.step"

# Build the rectangle on the XY plane
# The profile coordinates from the design plan are in UV space:
#   start_uv: [121.92, -60.96] to [121.92, 60.96] etc.
# But the dimensions say length_u = 2438.4, width_v = 1219.2
# The UV coordinates given are 1/20th scale? Let's check:
#   From curves: x ranges from -121.92 to 121.92 => width = 243.84
#   y ranges from -60.96 to 60.96 => height = 121.92
# But the design plan says length_u = 2438.4, width_v = 1219.2
# This is a factor of 10 difference. The compiler notes say "cm_to_mm (x10)"
# So the UV coordinates are in cm? Actually 121.92 cm = 1219.2 mm, 60.96 cm = 609.6 mm
# Wait: 121.92 * 10 = 1219.2, 60.96 * 10 = 609.6
# So the rectangle should be 2438.4 mm x 1219.2 mm
# Let's just use the explicit dimensions from the design plan.

# Create a workplane and draw the rectangle centered at origin
result = (
    cq.Workplane("XY")
    .rect(2438.4, 1219.2, centered=True)
    .extrude(12.7)
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
