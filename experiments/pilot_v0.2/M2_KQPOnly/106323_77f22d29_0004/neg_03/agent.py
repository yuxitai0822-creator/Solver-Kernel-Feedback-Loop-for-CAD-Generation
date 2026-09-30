import cadquery as cq

# Create an extruded annulus (bearing cross-section)
# Outer radius: 17.5 mm, Inner radius: 12.5 mm
# Extrude distance: 10.0 mm, symmetric about the XY plane
result = (
    cq.Workplane("XY")
    .circle(17.5)
    .circle(12.5)
    .extrude(10.0 / 2.0, both=True)
)

# Export the result to STEP file
cq.exporters.export(result, OUT_STEP_PATH)