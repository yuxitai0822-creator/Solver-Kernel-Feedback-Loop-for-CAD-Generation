import cadquery as cq

# Build an extruded annulus (bearing-like part)
# Outer radius: 132.5 mm, Inner radius: 75.0 mm, Extrude distance: 100.0 mm
# The design plan specifies the extrusion direction along +w, where w_dir is [1, 0, 0],
# meaning the extrusion happens along the +X axis.

result = (
    cq.Workplane("YZ")
    .circle(132.5)
    .circle(75.0)
    .extrude(100.0)
)

# Export the result to STEP format
cq.exporters.export(result, OUT_STEP_PATH)