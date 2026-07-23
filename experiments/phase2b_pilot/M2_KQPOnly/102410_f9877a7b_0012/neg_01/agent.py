import cadquery as cq

# Build an extruded annulus (bearing cross-section)
# Outer radius = 6.0 mm, Inner radius = 4.25 mm, Extrude distance = 12.0 mm
# The design plan specifies the extrusion direction as +w, where w_dir is [0, 1, 0],
# meaning extrusion is along the Y axis. The annulus profile lies in the XZ plane.

result = (
    cq.Workplane("XZ")
    .circle(6.0)
    .circle(4.25)
    .extrude(12.0)
)

# Export the result to STEP format
cq.exporters.export(result, OUT_STEP_PATH)