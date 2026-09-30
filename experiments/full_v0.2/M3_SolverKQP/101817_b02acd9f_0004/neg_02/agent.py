import cadquery as cq

# Design Plan: extruded rectangle (flat plate)
# Dimensions: length_u = 1200 mm, width_v = 600 mm, extrude_distance = 20 mm
# The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# The rectangle profile in UV coordinates:
#   start_uv = (127.82976131535646, -66.34402294937294)
#   end_uv = (7.829761315356478, -66.34402294937294)  -> line along u
#   start_uv = (127.82976131535646, -6.344022949372942)
#   end_uv = (127.82976131535646, -66.34402294937294)  -> line along v
#   start_uv = (7.829761315356478, -6.344022949372942)
#   end_uv = (127.82976131535646, -6.344022949372942)  -> line along u
#   start_uv = (7.829761315356478, -66.34402294937294)
#   end_uv = (7.829761315356478, -6.344022949372942)  -> line along v
# The rectangle spans from u=7.83 to u=127.83 (delta = 120.0) and v=-66.34 to v=-6.34 (delta = 60.0)
# But the dimensions say length_u=1200, width_v=600, so the UV coordinates are in cm (converted to mm by factor 10).
# Indeed compiler notes say cm_to_mm (x10). So the UV values are in cm, we must scale by 10 to get mm.
# Alternatively, we can just build the rectangle with the given dimensions directly.
# To match the exact UV coordinates (scaled by 10):
#   u_min = 7.829761315356478 * 10 = 78.29761315356478
#   u_max = 127.82976131535646 * 10 = 1278.2976131535646
#   v_min = -66.34402294937294 * 10 = -663.4402294937294
#   v_max = -6.344022949372942 * 10 = -63.44022949372942
# But the dimensions say 1200 x 600, so the delta is 1200 and 600. The UV values give delta_u = 120.0 cm = 1200 mm, delta_v = 60.0 cm = 600 mm. So scaling by 10 works.
# However, the frame has v_dir = (0,0,-1), meaning v axis points in -Z direction.
# w_dir = (0,1,0) means extrusion is along +Y.
# So the rectangle lies in the XZ plane (u along X, v along -Z).
# We'll build the rectangle in the XZ plane, then extrude in Y direction.

# Build the rectangle profile in the XZ plane (u -> X, v -> -Z)
# Use the scaled UV coordinates:
scale = 10.0
u_min = 7.829761315356478 * scale
u_max = 127.82976131535646 * scale
v_min = -66.34402294937294 * scale
v_max = -6.344022949372942 * scale

# Create the rectangle as a wire in the XZ plane
# Points: (u, 0, -v) because v_dir = (0,0,-1) so v maps to -Z
pts = [
    (u_min, 0, -v_min),  # (u_min, 0, -v_min) -> top-left in XZ
    (u_max, 0, -v_min),  # top-right
    (u_max, 0, -v_max),  # bottom-right
    (u_min, 0, -v_max),  # bottom-left
]

# Build the rectangle wire and make a face
rect = (
    cq.Workplane("XZ")
    .moveTo(pts[0][0], pts[0][2])
    .lineTo(pts[1][0], pts[1][2])
    .lineTo(pts[2][0], pts[2][2])
    .lineTo(pts[3][0], pts[3][2])
    .close()
    .extrude(20.0)  # extrude along Y (positive Y is w_dir)
)

result = rect

import cadquery as cq
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\101817_b02acd9f_0004\\neg_02/generated.step")