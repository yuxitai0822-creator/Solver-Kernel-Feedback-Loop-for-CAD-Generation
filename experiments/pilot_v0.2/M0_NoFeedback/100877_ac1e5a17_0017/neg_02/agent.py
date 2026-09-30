import cadquery as cq

# Build an extruded rectangle (flat plate/panel)
# Dimensions: 254.0 mm (u) x 190.5 mm (v) x 3.175 mm (w)
# Origin at bbox_min_corner

result = (
    cq.Workplane("XY")
    .rect(254.0, 190.5)
    .extrude(3.175)
)

cq.exporters.export(result, OUT_STEP_PATH)