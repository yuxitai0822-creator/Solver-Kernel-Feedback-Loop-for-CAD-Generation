import cadquery as cq

# Create a rectangular plate with dimensions 1200mm x 600mm x 20mm
# The design plan specifies a flat plate/panel with extruded rectangle profile
# Profile rectangle corners from curves (reordered to form closed loop):
#   (7.83, -66.34) -> (127.83, -66.34) -> (127.83, -6.34) -> (7.83, -6.34)
# This gives length_u = 120.0, width_v = 60.0 in the uv frame
# But dimensions say length_u=1200, width_v=600, extrude=20
# The uv coordinates appear to be scaled by 0.1 (cm to mm conversion factor 10)
# So we use the explicit dimensions: 1200 x 600 x 20 mm

# Build the plate centered at origin for simplicity
result = (
    cq.Workplane("XY")
    .rect(1200, 600)
    .extrude(20)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\101817_b02acd9f_0004\\ex2/generated.step")
