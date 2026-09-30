import cadquery as cq

# Create a rectangular plate with dimensions 1200mm x 600mm x 20mm
# The design plan specifies a flat plate/panel with extruded rectangle profile
# Profile rectangle corners from curves (reordered to form proper closed loop):
# Points in UV frame: (7.83, -66.34), (127.83, -66.34), (127.83, -6.34), (7.83, -6.34)
# These are in the local frame where u=x, v=-z, w=y
# The dimensions are length_u=1200, width_v=600, extrude_distance=20

# Build the rectangle in the XY plane (default workplane)
# The profile coordinates appear to be in a local UV frame, but the actual dimensions
# are 1200 x 600. The UV coordinates given seem to be scaled differently (possibly
# from a different coordinate system). We use the explicit dimensions from the plan.

result = (
    cq.Workplane("XY")
    .rect(1200, 600)
    .extrude(20)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\101817_b02acd9f_0004\\neg_03/generated.step")
