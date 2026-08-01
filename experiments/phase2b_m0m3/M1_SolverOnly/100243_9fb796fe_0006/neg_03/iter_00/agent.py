import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\100243_9fb796fe_0006\neg_03\iter_00/generated.step"

# Design Plan: extruded rectangle (square strut)
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile: rectangle in uv-plane, centered at origin
# Rectangle dimensions: length_u=19.0, width_v=19.0
# Extrude distance: 130.0 mm along +w (y-axis)

# Build on XY plane, then rotate to match frame orientation
# Frame: u=x, v=-z, w=y
# So we sketch on XZ plane (u,v) and extrude along Y (w)

# Rectangle corners in uv coordinates (from design plan curves):
# u range: [-58.27820137826746, -56.37820137826746] -> width = 1.9? Wait, that's 1.9 not 19.0
# Actually the design plan says length_u=19.0, width_v=19.0
# The curves show a small rectangle: width = -56.378 - (-58.278) = 1.9, height = -12.04 - (-13.94) = 1.9
# But the dimensions say 19.0. The perturbation changed 1.9 to 1.52 (20% reduction)
# The original was 1.9 cm = 19 mm, perturbed to 1.52 cm = 15.2 mm
# So we use 15.2 mm for both sides

# Let's center the rectangle at origin for simplicity
# The frame says u_dir=[1,0,0], v_dir=[0,0,-1], so sketch on XZ plane
# Rectangle centered at origin, size 15.2 x 15.2

size = 15.2  # mm (perturbed from 19.0)
extrude_dist = 130.0  # mm

# Build on XZ plane (cq.Workplane("XZ"))
# rect() creates rectangle centered at current point
result = (cq.Workplane("XZ")
          .rect(size, size)
          .extrude(extrude_dist))

# The extrusion direction is along Y (normal to XZ plane), which matches w_dir=[0,1,0]
# The rectangle is centered at origin, which is fine

exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")