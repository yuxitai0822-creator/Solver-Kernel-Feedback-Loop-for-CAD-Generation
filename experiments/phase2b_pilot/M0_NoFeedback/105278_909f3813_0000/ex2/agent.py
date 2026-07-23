import cadquery as cq

# Build a rectangular prism with dimensions 12.0 x 60.0 x 40.0 mm
# The design plan specifies an extruded rectangle with length_u=12.0, width_v=60.0, and extrude_distance=40.0
# The frame maps u->X, v->-Z, w->Y, so the dimensions correspond to X=12, Z=60, Y=40

result = cq.Workplane("XY").rect(12.0, 60.0).extrude(40.0)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M0_NoFeedback\105278_909f3813_0000\ex2/generated.step"
cq.exporters.export(result, OUT_STEP_PATH)