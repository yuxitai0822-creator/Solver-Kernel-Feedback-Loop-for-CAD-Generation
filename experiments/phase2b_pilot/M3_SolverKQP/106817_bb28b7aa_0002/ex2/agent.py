import cadquery as cq

# Design Plan: extruded_circle (thumb screw disk)
# Radius: 4.87045 mm, Extrude distance: 6.8707 mm
# Origin convention: bbox_min_corner

radius = 4.87045
extrude_dist = 6.8707

result = (cq.Workplane("XY")
          .circle(radius)
          .extrude(extrude_dist))

cq.exporters.export(result, OUT_STEP_PATH)