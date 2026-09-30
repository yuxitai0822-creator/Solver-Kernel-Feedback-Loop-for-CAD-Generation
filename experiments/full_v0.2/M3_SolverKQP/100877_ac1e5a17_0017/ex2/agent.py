import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# The design plan specifies a rectangle of 254.0 mm x 190.5 mm extruded to 3.175 mm
# Note: The profile curves in the design plan show coordinates in cm (25.4 x 19.05)
# but the dimensions section says 254.0 x 190.5 mm, so we use the mm values directly.

# Create the rectangle profile
result = (
    cq.Workplane("XY")
    .rect(254.0, 190.5)
    .extrude(3.175)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
