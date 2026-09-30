import cadquery as cq

# Build an extruded annulus (bearing/wheel)
# Outer radius: 132.5 mm, Inner radius: 75.0 mm, Extrude distance: 100.0 mm
# The design plan specifies the extrusion direction along +w, which maps to +X in the part local frame.
# We construct the annulus on the YZ plane and extrude along X to match the frame axes.

result = (
    cq.Workplane("YZ")
    .circle(132.5)
    .circle(75.0)
    .extrude(100.0)
)

# Export the result to STEP file
cq.exporters.export(result, OUT_STEP_PATH)