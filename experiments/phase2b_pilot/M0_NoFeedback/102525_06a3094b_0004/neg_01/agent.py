import cadquery as cq
import os

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M0_NoFeedback\102525_06a3094b_0004\neg_01/generated.step"

os.makedirs(os.path.dirname(OUT_STEP_PATH), exist_ok=True)

# SOP-28 rectangular prism
# Dimensions: length_u = 8.5mm, width_v = 18.0mm, extrude_distance = 2.5mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Origin convention: bbox_min_corner
# Profile rectangle in UV: u spans [-0.425, 0.425], v spans [-0.9, 0.9]
# Extrusion direction: +w (which is +Y in world)

result = (
    cq.Workplane("XZ")
    .transformed(offset=cq.Vector(0, 0, 0), rotate=cq.Vector(0, 0, 0))
    .rect(8.5, 18.0)
    .extrude(2.5)
)

cq.exporters.export(result, OUT_STEP_PATH)
