import cadquery as cq

# Design Plan: rectangular prism (SOP-28 body)
# Dimensions: length_u = 11.3 mm, width_v = 21.0 mm, extrude_distance = 3.0 mm
# Frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# Profile rectangle centered at origin in uv-plane, then extruded along +w (y-axis)

# Build the rectangle profile on the XY plane (u=x, v=z, w=y)
# The rectangle spans from -5.65 to 5.65 in u (x) and -10.5 to 10.5 in v (z)
result = (
    cq.Workplane("XY")
    .center(0, 0)
    .rect(11.3, 21.0)
    .extrude(3.0)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\102525_06a3094b_0006\\neg_02/generated.step")
