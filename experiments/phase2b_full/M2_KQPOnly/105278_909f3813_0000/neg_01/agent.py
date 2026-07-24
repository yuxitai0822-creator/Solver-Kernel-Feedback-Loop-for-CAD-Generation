import cadquery as cq

# Create a rectangular prism with dimensions: length_u=12mm, width_v=60mm, extrude_distance=40mm
# The profile is a rectangle centered at origin in the XY plane, extruded in the Z direction

# Create the rectangle profile (centered at origin)
# From the design plan: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means: u along X, v along -Z, w along Y
# The rectangle spans: u from -6 to 6 (total 12mm), v from -30 to 30 (total 60mm)
# Extrude along w (Y direction) by 40mm

result = (
    cq.Workplane("XY")
    .center(0, 0)
    .rect(12.0, 60.0)
    .extrude(40.0)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\105278_909f3813_0000\\neg_01/generated.step")
