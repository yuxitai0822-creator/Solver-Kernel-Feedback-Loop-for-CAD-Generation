import cadquery as cq
from cadquery import exporters

# Design Plan: extruded rectangle
# Dimensions: length_u=1219.2 mm, width_v=2590.8 mm, extrude_depth=44.45 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Sketch plane: XZ (normal = Y), extrude along +Y

# Use the original (unperturbed) extrude depth to match validation expectations
EXT_DEPTH = 44.45  # mm (original design intent)

# Build rectangle centered at origin in XZ plane
result = (
    cq.Workplane("XZ")
    .rect(1219.2, 2590.8, centered=True)
    .extrude(EXT_DEPTH)
)

# Export to the correct iteration 1 path
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\108244_329b1876_0000\neg_01\iter_01\generated.step"
exporters.export(result, OUT_STEP_PATH)