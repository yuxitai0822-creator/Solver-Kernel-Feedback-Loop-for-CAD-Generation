import cadquery as cq

# Create a rectangular flat plate extruded along the Z axis
# Dimensions: 254.0 mm (X) x 190.5 mm (Y) x 3.175 mm (Z)
result = cq.Workplane("XY").rect(254.0, 190.5).extrude(3.175)

# Export the result to STEP format
cq.exporters.export(result, OUT_STEP_PATH)