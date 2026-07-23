import cadquery as cq

# Build a flat plate/panel: an extruded rectangle
# Dimensions: length_u = 254.0 mm, width_v = 190.5 mm, extrude distance = 3.175 mm

result = (
    cq.Workplane("XY")
    .rect(254.0, 190.5)
    .extrude(3.175)
)

cq.exporters.export(result, OUT_STEP_PATH)