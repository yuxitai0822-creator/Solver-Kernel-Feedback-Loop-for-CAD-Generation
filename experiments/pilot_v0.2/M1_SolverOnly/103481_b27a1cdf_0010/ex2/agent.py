import cadquery as cq

# Build a rectangular prism: 101.6 x 101.6 x 38.1 mm
# The profile is centered at origin in the XY plane, spanning from -5.08 to 5.08 in both X and Y.
# Wait, the design plan says the rectangle spans from -5.08 to 5.08, which is 10.16 x 10.16.
# But the dimensions specify length_u = 101.6 and width_v = 101.6.
# The compiler notes indicate a unit conversion of cm_to_mm (x10) was applied.
# So the original sketch coordinates (5.08 cm) were converted to 50.8 mm.
# However, the design plan still lists the UV coordinates as 5.08 (which must be interpreted as 50.8 mm after conversion).
# To match the validation intents (span_u = 101.6, span_v = 101.6), we use the explicit dimensions.

length_u = 101.6
width_v = 101.6
extrude_distance = 38.1

result = cq.Workplane("XY").rect(length_u, width_v).extrude(extrude_distance)

cq.exporters.export(result, OUT_STEP_PATH)