import cadquery as cq
from cadquery import exporters

# Design Plan: extruded rectangle
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Rectangle in UV (cm): u=[-0.7464, 121.1736], v=[31.2996, 290.3796]
# After cm->mm: u=[-7.464, 1211.736], v=[312.996, 2903.796]
# Origin at bbox_min_corner: shift X by +7.464, shift Z by +2903.796
# Result: X=[0, 1219.2], Z=[0, 2590.8]
# Perturbation: v span reduced from 2590.8 to 2072.64 mm
# So Z=[0, 2072.64]
# Extrude along Y by 44.45 mm

result = (
    cq.Workplane("XZ")
    .rect(1219.2, 2072.64, centered=False)
    .extrude(44.45)
)

# Export to the required path
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\108244_329b1876_0000\neg_03\iter_01\generated.step"
exporters.export(result, OUT_STEP_PATH)