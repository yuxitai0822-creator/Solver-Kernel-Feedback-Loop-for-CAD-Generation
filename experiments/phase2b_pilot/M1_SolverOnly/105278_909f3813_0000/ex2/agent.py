import cadquery as cq

# Design Plan: rectangular_prism_generic
# Dimensions: length_u = 12.0 mm, width_v = 60.0 mm, extrude_distance = 40.0 mm
# Frame: u_dir = [1, 0, 0], v_dir = [0, 0, -1], w_dir = [0, 1, 0]
# Profile rectangle spans from u=-0.6 to u=0.6 and v=-3.0 to v=3.0
# Extrusion direction: +w (which is +Y in world coordinates)

result = (
    cq.Workplane("XZ")
    .transformed(offset=(0, 0, 0), rotate=(0, 0, 0))
    .rect(1.2, 6.0)  # length_u=1.2, width_v=6.0
    .extrude(40.0)    # extrude_distance=40.0 along +Y
)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M1_SolverOnly\105278_909f3813_0000\ex2/generated.step"

cq.exporters.export(result, OUT_STEP_PATH)