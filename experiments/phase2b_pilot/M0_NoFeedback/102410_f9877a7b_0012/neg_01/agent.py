import cadquery as cq

# Build an extruded annulus (bearing-like shape)
# Outer radius: 6.0 mm, Inner radius: 4.25 mm, Extrude distance: 12.0 mm
# Frame: u=(1,0,0), v=(0,0,-1), w=(0,1,0) -> extrude along +Y
# Origin at bbox_min_corner -> start extrude at Y=0

result = (
    cq.Workplane("XZ")
    .circle(6.0)
    .circle(4.25)
    .extrude(12.0)
)

cq.exporters.export(result, OUT_STEP_PATH)