import cadquery as cq
import os

# Ensure output directory exists
OUT_DIR = r'D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M0_NoFeedback\100243_9fb796fe_0005\neg_03'
OUT_STEP_PATH = os.path.join(OUT_DIR, 'generated.step')

os.makedirs(OUT_DIR, exist_ok=True)

# Design Plan Parameters:
# - Primitive: extruded_rectangle
# - Profile dimensions: length_u = 19.0 mm, width_v = 19.0 mm
# - Extrude distance: 200.0 mm
# - Extrude direction: +w (which maps to +Y in CadQuery's default coordinate system)
# - Profile origin in local frame: u = -58.27820137826746, v = -13.940145769681571

# In CadQuery, the default workplane (XY plane) extrudes along the Z axis.
# To map the design plan's +w direction to CadQuery's extrusion axis, we construct the geometry on the XZ plane.
# This aligns: u -> X, v -> Z, w(+Y) -> Y.

# Calculate the center of the rectangle in the XZ plane
u_min = -58.27820137826746
u_max = -56.37820137826746
v_min = -13.940145769681571
v_max = -12.04014576968157

center_x = (u_min + u_max) / 2.0  # -57.32820137826746
center_z = (v_min + v_max) / 2.0  # -12.99014576968157

# Build the rectangular profile on the XZ plane centered at the computed coordinates
result = (
    cq.Workplane("XZ")
    .center(center_x, center_z)
    .rect(19.0, 19.0)
    .extrude(200.0)
)

# Export the result to STEP format
cq.exporters.export(result, OUT_STEP_PATH)
