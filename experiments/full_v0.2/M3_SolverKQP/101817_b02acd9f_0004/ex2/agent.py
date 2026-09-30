import cadquery as cq

# Create a rectangular plate with dimensions 1200mm x 600mm x 20mm
# The design plan specifies a flat plate/panel with extruded rectangle profile
# The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means: u = x-axis, v = -z axis, w = y-axis
# The rectangle is defined in UV space with corners at:
# (7.82976, -66.3440) to (127.82976, -6.3440)
# These UV coordinates are scaled to match the actual dimensions

# The dimensions from the plan:
# length_u = 1200.0 mm (along x-axis)
# width_v = 600.0 mm (along z-axis, but v_dir is (0,0,-1) so width is along -z)
# extrude_distance = 20.0 mm (along y-axis, w_dir = (0,1,0))

# Create the rectangle profile in the XY plane (since we'll extrude along Y)
# The UV coordinates given are: u from 7.83 to 127.83, v from -66.34 to -6.34
# These are offset from origin; we'll center the rectangle at origin for simplicity
# and then translate to match the design intent

# Actually, let's use the exact UV coordinates from the design plan
# The rectangle corners in UV space:
# (127.82976, -66.34402), (7.82976, -66.34402)
# (127.82976, -6.34402), (7.82976, -6.34402)
# 
# But the actual dimensions should be 1200 x 600, so these UV values are scaled
# The span in u: 127.82976 - 7.82976 = 120.0
# The span in v: -6.34402 - (-66.34402) = 60.0
# So the scaling factor is 10 (120*10=1200, 60*10=600)
# This matches the compiler note: cm_to_mm (x10)

# So we'll create the rectangle with the scaled dimensions
# Center the rectangle at origin for simplicity

# Create the base rectangle
result = (
    cq.Workplane("XY")
    .rect(1200.0, 600.0, centered=True)
    .extrude(20.0)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\101817_b02acd9f_0004\\ex2/generated.step")
