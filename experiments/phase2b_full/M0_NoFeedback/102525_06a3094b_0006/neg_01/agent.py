import cadquery as cq

# Design Plan: rectangular prism with dimensions 11.3mm x 21.0mm x 3.0mm
# The profile is centered on the sketch plane, extruded in +w direction (which is +Y in world)
# Frame: u_dir = X, v_dir = -Z, w_dir = Y
# So sketch is on XZ plane (normal = Y), rectangle centered at origin

# Rectangle dimensions from design plan
length_u = 11.3  # along X
width_v = 21.0   # along Z (but v_dir is -Z, so width is along Z)
extrude_distance = 3.0  # along Y

# Create the rectangle centered at origin on the XZ plane
# The profile coordinates in UV: u from -5.65 to 5.65, v from -10.5 to 10.5
# But v_dir = -Z, so v maps to -Z. To get positive Z extent, we use negative v values.
# Actually simpler: just create rectangle on XZ plane centered at origin
result = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(length_u, width_v)
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\102525_06a3094b_0006\\neg_01/generated.step")
