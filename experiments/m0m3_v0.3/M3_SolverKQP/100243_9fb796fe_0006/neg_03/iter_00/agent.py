import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\100243_9fb796fe_0006\neg_03\iter_00/generated.step"

# Design Plan: extruded rectangle (square strut)
# Profile: rectangle 19.0 x 19.0 mm (in UV plane)
# Extrude: 130.0 mm along +W direction
# Frame: U = (1,0,0), V = (0,0,-1), W = (0,1,0)
# Origin at bbox_min_corner convention: we place rectangle so that its min corner is at origin

# Rectangle dimensions from design plan
length_u = 19.0  # along U axis (X)
width_v = 19.0   # along V axis (Z, negative direction)
extrude_distance = 130.0  # along W axis (Y)

# Build the rectangle on the XZ plane (since U=X, V=-Z, W=Y)
# We want the rectangle to span from (0,0) to (19,19) in UV coordinates
# In world: U = X, V = -Z, so:
#   point (u,v) -> (u, 0, -v)
# Rectangle corners in UV: (0,0), (19,0), (19,19), (0,19)
# In world: (0,0,0), (19,0,0), (19,0,-19), (0,0,-19)

# Create workplane on XZ plane (Y=0)
wp = cq.Workplane("XZ")

# Build the rectangle centered at (9.5, -9.5) in XZ coordinates
# rect() takes width (X) and height (Z), centered by default
result = wp.center(9.5, -9.5).rect(length_u, width_v).extrude(extrude_distance)

# Export
importers.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")
