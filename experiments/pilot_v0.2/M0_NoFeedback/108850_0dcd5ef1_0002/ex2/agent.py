import cadquery as cq

# Build a flat plate/panel: extruded rectangle
# Profile dimensions: length_u = 171.45 mm, width_v = 38.1 mm
# Extrude distance: 6.35 mm

result = (
    cq.Workplane("XY")
    .rect(171.45, 38.1)
    .extrude(6.35)
)

cq.exporters.export(result, OUT_STEP_PATH)