import cadquery as cq
import os

# Ensure output directory exists
OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-SolverKernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M3_SolverKQP\108244_329b1876_0000\ex2"
OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")
os.makedirs(OUT_DIR, exist_ok=True)

# Design Plan Parameters:
# Primitive: extruded_rectangle
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile dimensions: length_u = 1219.2 mm, width_v = 2590.8 mm
# Extrude distance: 44.45 mm along +w direction

# In CadQuery's default XY plane, X aligns with u_dir=[1,0,0] and Y aligns with v_dir=[0,0,-1].
# To correctly orient the rectangle so that Y spans 2590.8 mm in the negative global Z direction,
# we construct the rectangle with a negative height in the Y axis.

result = (
    cq.Workplane("XY")
    .rect(1219.2, -2590.8)
    .extrude(44.45)
)

# Export the result to STEP format
cq.exporters.export(result, OUT_STEP_PATH)
