import cadquery as cq
from cadquery import exporters

# Design Plan: extruded rectangle
# Dimensions: length_u=1200.0 mm, width_v=600.0 mm, extrude_distance=20.0 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile rectangle in UV plane: u from 7.82976 to 127.82976, v from -66.34402 to -6.34402
# Note: The profile coordinates in the design plan are in UV space.
# The rectangle width in U = 127.82976 - 7.82976 = 120.0 (but expected 1200.0)
# The rectangle height in V = -6.34402 - (-66.34402) = 60.0 (but expected 600.0)
# This suggests the UV coordinates are scaled by 0.1 (cm to mm conversion already applied?)
# Actually the design plan says unit conversion cm_to_mm (x10) was applied.
# The original dimensions are 1200mm x 600mm x 20mm.
# The profile coordinates in UV: width=120.0, height=60.0, which is 1/10 of expected.
# This is likely because the UV coordinates are in cm (before conversion) or the frame scaling is different.
# To match the expected spans (1200, 600, 20), we use the explicit dimensions from the design plan.

# Build the rectangle on the XZ plane (since v_dir is [0,0,-1], the sketch plane is XZ)
# w_dir is [0,1,0] so extrusion is along Y axis.

result = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(1200.0, 600.0, centered=True)
    .extrude(20.0)
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\101817_b02acd9f_0004\neg_02\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)