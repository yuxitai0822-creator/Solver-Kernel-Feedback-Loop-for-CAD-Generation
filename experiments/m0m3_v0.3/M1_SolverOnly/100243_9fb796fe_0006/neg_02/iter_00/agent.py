import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\100243_9fb796fe_0006\neg_02\iter_00\generated.step"

# Design Plan: extruded rectangle (square strut)
# Profile: rectangle 19.0mm x 19.0mm (in UV plane)
# Extrude: 130.0mm along W direction
# Frame: U=[1,0,0], V=[0,0,-1], W=[0,1,0]
# The rectangle corners in UV space (from design plan curves):
#   (-58.2782, -12.0401) to (-56.3782, -13.9401) -> width=1.9, height=1.9
# But dimensions say 19.0mm x 19.0mm. The UV coords are in cm (converted to mm by *10).
# Actually the original coords are in cm: -58.2782 cm = -582.782 mm, etc.
# The rectangle width = (-56.3782 - (-58.2782)) = 1.9 cm = 19.0 mm. Height = (-12.0401 - (-13.9401)) = 1.9 cm = 19.0 mm.
# So we can just build a 19x19 rectangle centered at the midpoint of these corners.

# Midpoint in UV (cm): u_center = (-58.2782 + -56.3782)/2 = -57.3282 cm = -573.282 mm
# v_center = (-12.0401 + -13.9401)/2 = -12.9901 cm = -129.901 mm
# But we can also just build the rectangle at origin and translate.

# Simpler: build rectangle 19x19 on XZ plane (since U=X, V=-Z, W=Y)
# Then translate to the correct position.

# Create workplane on XZ (since U=X, V=-Z means sketch on XZ plane)
wp = cq.Workplane("XZ")

# Build rectangle 19mm x 19mm centered at origin
rect = wp.rect(19.0, 19.0).extrude(130.0)

# The rectangle needs to be positioned correctly.
# From the design plan, the rectangle in UV space has center at:
# u_center = (-58.27820137826746 + -56.37820137826746)/2 = -57.32820137826746 cm = -573.2820137826746 mm
# v_center = (-12.04014576968157 + -13.940145769681571)/2 = -12.99014576968157 cm = -129.9014576968157 mm
# In world coords: X = u_center, Z = -v_center (since V = -Z), Y = 0 (since W=Y, extrude along Y)
# So translate: x=-573.282, z=129.901, y=0

result = rect.translate(( -573.2820137826746, 0, 129.9014576968157 ))

# Verify: the resulting body should span:
# X: from -573.282 - 9.5 = -582.782 to -573.282 + 9.5 = -563.782 (matches -58.2782cm to -56.3782cm *10)
# Z: from 129.901 - 9.5 = 120.401 to 129.901 + 9.5 = 139.401 (matches -12.0401cm to -13.9401cm * -1 + offset)
# Y: from 0 to 130.0

# Export
importers.export(result, OUT_STEP_PATH)