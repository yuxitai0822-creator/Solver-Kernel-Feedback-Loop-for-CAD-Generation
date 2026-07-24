import cadquery as cq

# Create a rectangular plate with dimensions 1200mm x 600mm x 20mm
# The design plan specifies a flat plate/panel with extruded rectangle profile
# Profile rectangle corners in UV space:
#   (127.82976131535646, -66.34402294937294) -> (7.829761315356478, -66.34402294937294)
#   (127.82976131535646, -6.344022949372942) -> (127.82976131535646, -66.34402294937294)
#   (7.829761315356478, -6.344022949372942) -> (127.82976131535646, -6.344022949372942)
#   (7.829761315356478, -66.34402294937294) -> (7.829761315356478, -6.344022949372942)
# The rectangle spans from u=7.83 to u=127.83 (delta = 120.0) and v=-66.34 to v=-6.34 (delta = 60.0)
# But the dimensions say length_u=1200.0, width_v=600.0, extrude_distance=20.0
# The UV coordinates appear to be scaled by 0.1 (cm to mm conversion factor of 10 applied)
# So we use the explicit dimensions: 1200 x 600 x 20 mm

# Build the plate centered at origin for simplicity
result = (
    cq.Workplane("XY")
    .rect(1200, 600)
    .extrude(20)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\101817_b02acd9f_0004\\ex2/generated.step")
