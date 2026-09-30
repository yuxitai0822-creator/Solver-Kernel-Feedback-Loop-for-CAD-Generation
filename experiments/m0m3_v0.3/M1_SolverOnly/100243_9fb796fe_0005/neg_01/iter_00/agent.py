import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\100243_9fb796fe_0005\neg_01\iter_00\generated.step"

# Design Plan: Drone Leg Left
# Square strut: 19mm x 19mm rectangle extruded 200mm along w direction
# Frame: u=[1,0,0], v=[0,0,-1], w=[0,1,0]
# Profile rectangle corners in uv plane:
#   (-58.27820137826746, -12.04014576968157) to (-56.37820137826746, -13.940145769681571)
#   This gives width_v = 1.9mm? Wait, let's compute properly.
#   Actually the dimensions say length_u=19.0, width_v=19.0
#   The uv coordinates span: u from -58.278 to -56.378 = 1.9? That's 1.9 not 19.
#   But the design plan says 19.0. The coordinates were likely in cm and converted.
#   Original cm values: -5.82782 to -5.63782 = 0.19 cm = 1.9 mm? No.
#   Let's re-read: compiler notes say cm_to_mm (x10). So original cm values:
#   u: -5.827820137826746 to -5.637820137826746 = 0.19 cm = 1.9 mm? That's still not 19.
#   Wait, the dimensions say 19.0 mm. The uv coordinates after cm->mm conversion:
#   -58.27820137826746 to -56.37820137826746 = 1.9 mm? No, difference = 1.9.
#   But the design plan says length_u = 19.0. There's a factor of 10 discrepancy.
#   The compiler notes say cm_to_mm (x10). So original cm: -5.8278 to -5.6378 = 0.19 cm = 1.9 mm.
#   But expected is 19 mm. So the uv coordinates are off by factor 10.
#   Let's just use the explicit dimensions: 19.0 x 19.0 rectangle, centered at origin.
#   The frame has u=x, v=-z, w=y. So sketch on XZ plane, extrude along Y.

# Build the part using the explicit dimensions from the design plan
# Rectangle 19mm x 19mm on XZ plane, extruded 200mm along Y
result = (
    cq.Workplane("XZ")
    .rect(19.0, 19.0, centered=True)
    .extrude(200.0)
)

# Export
cq.exporters.export(result, OUT_STEP_PATH)
