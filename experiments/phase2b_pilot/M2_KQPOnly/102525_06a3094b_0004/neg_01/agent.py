import cadquery as cq

# Design Plan: SOP-28 (1) rectangular prism
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Origin: bbox_min_corner
# Profile rectangle in uv-plane: u spans 8.5mm, v spans 18.0mm
# Extrude along +w direction by 2.5mm

# In the part-local coordinate system (x,y,z):
#   x corresponds to u_dir = [1, 0, 0]
#   y corresponds to w_dir = [0, 1, 0]
#   z corresponds to -v_dir = [0, 0, 1] (since v_dir = [0, 0, -1])
# Thus the rectangle spans 8.5mm along x and 18.0mm along z.
# Extrusion is 2.5mm along +y.

# Origin is at bbox_min_corner, so the rectangle starts at (0, 0, 0)
# and extends to (8.5, 2.5, 18.0).

result = cq.Workplane("XY").rect(8.5, 18.0).extrude(2.5)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M2_KQPOnly\102525_06a3094b_0004\neg_01/generated.step"
cq.exporters.export(result, OUT_STEP_PATH)
