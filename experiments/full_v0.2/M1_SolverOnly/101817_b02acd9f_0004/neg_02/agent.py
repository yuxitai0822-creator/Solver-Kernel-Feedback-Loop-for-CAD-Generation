import cadquery as cq

# Create a rectangular plate with dimensions 1200mm x 600mm x 20mm
# The design plan specifies a rectangle in the uv-plane, then extruded in the +w direction
# The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means: u = x, v = -z, w = y
# The rectangle corners in uv coordinates:
#   start_uv = (127.82976131535646, -66.34402294937294)
#   end_uv = (7.829761315356478, -6.344022949372942)
# The length_u = 120.0 (but note: the dimension says 1200.0 with a note about cm_to_mm x10)
# Actually the dimension says 1200.0, but the uv coordinates span 120.0 in u and 60.0 in v
# The compiler note says cm_to_mm (x10) was applied, so the original was 120cm x 60cm = 1200mm x 600mm
# The uv coordinates are in the original cm scale? Let's check:
# u range: 127.82976 - 7.82976 = 120.0 (cm) -> 1200 mm
# v range: -6.34402 - (-66.34402) = 60.0 (cm) -> 600 mm
# So we need to scale the uv coordinates by 10 to get mm, OR just use the dimensions directly.
# The dimensions are given as 1200.0 and 600.0, so we'll use those directly.
# The extrude distance is 20.0 mm.

# Build the rectangle centered at origin for simplicity, matching the dimensions
length = 1200.0
width = 600.0
thickness = 20.0

# Create the plate
result = (
    cq.Workplane("XY")
    .rect(length, width)
    .extrude(thickness)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\101817_b02acd9f_0004\\neg_02/generated.step")
