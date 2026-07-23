import cadquery as cq

# Create a rectangular prism: 101.6 x 101.6 x 38.1 mm
# The profile rectangle is centered at the origin (spanning from -5.08 to 5.08 in local sketch coords, which maps to 101.6mm width/length)
# Extruded along +Z for 38.1mm
result = cq.Workplane("XY").rect(101.6, 101.6).extrude(38.1)

cq.exporters.export(result, OUT_STEP_PATH)