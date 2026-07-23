import cadquery as cq

# Build a rectangular profile and extrude it
# Profile dimensions: length_u = 209.55 mm, width_v = 57.912 mm
# Extrude distance along +Y axis: 19.05 mm

result = (
    cq.Workplane("XZ")
    .rect(209.55, 57.912)
    .extrude(19.05)
)

# Export the result to STEP file
cq.exporters.export(result, OUT_STEP_PATH)