import cadquery as cq

# Build an extruded circle (cylinder) based on the design plan.
# The plan specifies a unit conversion of cm_to_mm (x10) was applied.
# The dimensions section provides the final mm values:
#   radius = 4.7117 mm
#   extrude distance = 12.192 mm
# The origin convention is bbox_min_corner, so we offset the center by the radius.

radius = 4.7117
extrude_distance = 12.192

# Create the circle profile offset so the bounding box min corner is at (0, 0)
result = (cq.Workplane("XY")
           .circle(radius)
           .extrude(extrude_distance))

# Export the result to STEP file
cq.exporters.export(result, OUT_STEP_PATH)