import cadquery as cq

# Design Plan: extruded_rectangle (flat_plate_or_panel)
# Dimensions: length_u = 1219.2 mm, width_v = 2590.8 mm, extrude_distance = 44.45 mm
# Frame: u_dir = [1, 0, 0], v_dir = [0, 0, -1], w_dir = [0, 1, 0]
# Origin convention: bbox_min_corner

# In the part local frame (origin at bbox_min_corner, axes X, Y, Z):
# The u-axis maps to X, the v-axis maps to -Z, and the w-axis maps to Y.
# To create the rectangle at the bbox_min_corner (0, 0, 0) with the correct spans:
# - Along u (X): 0 to 1219.2
# - Along v (-Z): 0 to -2590.8 (which means Z goes from 2590.8 down to 0)
# - Along w (Y): 0 to 44.45

# We define the rectangle in the XY plane of the local workplane.
# X corresponds to u (length 1219.2).
# Y corresponds to -v (length 2590.8).
# The extrusion direction is +w, which maps to +Z in the local frame.

result = (
    cq.Workplane("XY")
    .rect(1219.2, 2590.8)
    .extrude(44.45)
)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M2_KQPOnly\108244_329b1876_0000\ex2/generated.step"
cq.exporters.export(result, OUT_STEP_PATH)