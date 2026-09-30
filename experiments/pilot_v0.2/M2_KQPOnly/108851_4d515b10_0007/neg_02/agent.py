import cadquery as cq

# Build a rectangular profile and extrude it
# Profile dimensions: 279.4 mm (X) x 50.8 mm (Z)
# Extrude direction: +Y, distance: 19.05 mm

result = (
    cq.Workplane("XZ")
    .rect(279.4, 50.8)
    .extrude(19.05)
)

# Export the result to STEP file
cq.exporters.export(result, OUT_STEP_PATH)