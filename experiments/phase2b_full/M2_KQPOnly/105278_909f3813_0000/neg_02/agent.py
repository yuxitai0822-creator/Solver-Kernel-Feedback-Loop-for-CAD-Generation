import cadquery as cq

# Create a rectangular prism with dimensions: length_u=12mm, width_v=60mm, extrude_distance=40mm
# The profile is a rectangle centered at origin in the XY plane, extruded in the +Z direction

# Define the rectangle dimensions
length_u = 12.0  # along X axis
width_v = 60.0   # along Y axis (since v_dir is [0,0,-1], but we'll use standard orientation)
extrude_distance = 40.0  # along Z axis

# Create the rectangular profile centered at origin
result = (
    cq.Workplane("XY")
    .rect(length_u, width_v)
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\105278_909f3813_0000\\neg_02/generated.step")
