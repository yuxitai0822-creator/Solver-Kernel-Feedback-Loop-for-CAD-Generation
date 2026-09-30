import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# The design plan specifies a rectangle of 254.0 mm x 190.5 mm extruded to 3.175 mm
# Note: The profile curves show 25.4 and 19.05 which are 1/10th of the actual dimensions
# This is because the design plan notes unit_conversion_applied: cm_to_mm (x10)
# So the actual dimensions are 254.0 mm x 190.5 mm x 3.175 mm

# Create the rectangle profile
result = (cq.Workplane("XY")
          .rect(254.0, 190.5)
          .extrude(3.175))

# Export to STEP file
cq.exporters.export(result, OUT_STEP_PATH)