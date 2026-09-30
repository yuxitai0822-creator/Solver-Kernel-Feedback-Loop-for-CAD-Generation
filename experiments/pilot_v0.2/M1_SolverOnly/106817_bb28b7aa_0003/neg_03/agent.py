import cadquery as cq

# Build the extruded circle (cylinder) based on the design plan.
# The dimensions section specifies the radius as 4.7117 mm and the extrude distance as 12.192 mm.
# The origin convention is bbox_min_corner, so we offset the circle center by its radius to place the bounding box min at (0,0,0).

radius = 4.7117
extrude_distance = 12.192

result = (cq.Workplane("XY")
          .circle(radius)
          .extrude(extrude_distance))

# Export the result to the specified STEP file path
cq.exporters.export(result, OUT_STEP_PATH)