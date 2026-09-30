import cadquery as cq
from cadquery import exporters

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\100243_9fb796fe_0006\neg_03\iter_02\generated.step"

# Design Plan: extruded rectangle (square strut)
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile: rectangle in uv-plane
# Rectangle dimensions: length_u=19.0, width_v=19.0 (original)
# Perturbation: 20% reduction -> 15.2 mm
# Extrude distance: 130.0 mm along +w (y-axis)

# The frame defines:
#   u = x-axis
#   v = -z-axis (negative z)
#   w = y-axis
# So we sketch on the XZ plane (u,v) and extrude along Y (w)

# The rectangle corners from the design plan curves:
# u range: [-58.27820137826746, -56.37820137826746] -> width = 1.9
# v range: [-12.04014576968157, -13.940145769681571] -> height = 1.9
# These are in cm (original 1.9 cm = 19 mm, perturbed 1.52 cm = 15.2 mm)
# The rectangle is not centered at origin; it's offset in uv space

# To match the exact position from the design plan, we need to place the rectangle
# at the correct uv coordinates. The center of the rectangle in uv space:
# u_center = (-58.27820137826746 + -56.37820137826746) / 2 = -57.32820137826746
# v_center = (-12.04014576968157 + -13.940145769681571) / 2 = -12.99014576968157

# Convert to mm (multiply by 10 since original was in cm)
# But wait - the perturbation says original=1.9, perturbed=1.52
# So the rectangle size is 15.2 mm (perturbed from 19 mm)
# The center coordinates should also be scaled? No, the center position is absolute.
# The curves show the rectangle at specific uv coordinates.
# Since the original was 1.9 cm = 19 mm, and the coordinates are in mm,
# the center is at (-57.3282, -12.9901) in mm.

# However, the design plan dimensions say length_u=19.0, width_v=19.0
# and the perturbation changed this to 15.2 mm.
# The center coordinates remain the same as they define position, not size.

size = 15.2  # mm (perturbed from 19.0)
extrude_dist = 130.0  # mm

# Center of rectangle in uv coordinates (from design plan curves)
u_center = -57.32820137826746  # mm
v_center = -12.99014576968157  # mm

# Build on XZ plane (cq.Workplane("XZ"))
# Move to the center position, then create rectangle
result = (cq.Workplane("XZ")
          .center(u_center, v_center)
          .rect(size, size)
          .extrude(extrude_dist))

# The extrusion direction is along Y (normal to XZ plane), which matches w_dir=[0,1,0]

exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")