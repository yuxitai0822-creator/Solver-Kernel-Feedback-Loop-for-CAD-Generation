import cadquery as cq

# SOIC-8 package body: rectangular prism
# Dimensions from design plan (converted cm->mm already noted):
# length_u (along X) = 3.9 mm
# width_v (along Z, mapped from -v_dir) = 4.9 mm
# extrude_distance (along Y, mapped from +w_dir) = 1.55 mm

result = (
    cq.Workplane("XZ")
    .rect(3.9, 4.9)
    .extrude(1.55)
)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M3_SolverKQP\102525_06a3094b_0000\ex2/generated.step"
cq.exporters.export(result, OUT_STEP_PATH)
