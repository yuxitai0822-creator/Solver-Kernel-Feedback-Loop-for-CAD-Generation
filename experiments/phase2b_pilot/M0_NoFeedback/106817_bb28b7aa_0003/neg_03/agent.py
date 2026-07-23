import cadquery as cq

# Design Plan: extruded_circle (ruler holder w/screw)
# The dimensions section provides the authoritative, scaled values:
#   radius = 4.7117 mm (from explicit_dimension, unit_conversion_applied: cm_to_mm)
#   center_uv = [50.800002, 63.500002] mm
#   extrude_distance = 12.192 mm
# The frame maps u->X, v->-Z, w->Y, so the extrusion goes along +Y.
# The origin_convention is bbox_min_corner, so we offset the cylinder center
# so that the bounding box minimum aligns with the origin.

radius = 4.7117
center_u = 50.800002
center_v = 63.500002
extrude_dist = 12.192

# In the part_local frame (X, Y, Z):
# u_dir = [1, 0, 0] -> X axis
# v_dir = [0, 0, -1] -> -Z axis
# w_dir = [0, 1, 0] -> Y axis
# The circle lies in the u-v plane (X, -Z), centered at (center_u, center_v).
# Extrusion is along +w (+Y) by extrude_dist.

# To satisfy the bbox_min_corner origin convention:
# Bounding box ranges:
#   X: [center_u - radius, center_u + radius]
#   Y: [0, extrude_dist]
#   Z: [center_v - radius, center_v + radius] (since v maps to -Z)
# We shift the center so that bbox_min is at (0, 0, 0):
#   X_shift = -(center_u - radius) = radius - center_u
#   Z_shift = -(center_v - radius) = radius - center_v

x_shift = radius - center_u
z_shift = radius - center_v

# Build the cylinder
result = (
    cq.Workplane("XZ")
    .center(x_shift, z_shift)
    .circle(radius)
    .extrude(extrude_dist)
)

cq.exporters.export(result, OUT_STEP_PATH)