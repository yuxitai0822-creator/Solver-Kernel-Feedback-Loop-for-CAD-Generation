import cadquery as cq

# Design Plan: extruded rectangular frame
# Outer rectangle: u from -2.5 to 195.5, v from -2.5 to 57.5
# Inner rectangle: u from 0.0 to 193.0, v from 0.0 to 55.0
# Extrude in +w direction by 25.0 mm

# Create the outer rectangle
outer = cq.Workplane("XY").rect(198.0, 60.0).extrude(25.0)

# Create the inner rectangle (to be subtracted)
inner = cq.Workplane("XY").rect(193.0, 55.0).extrude(25.0)

# Position inner rectangle centered within outer
# Outer center: (96.5, 27.5)  (since rect centers at origin by default, we need to shift)
# Actually, using rect() centers at origin, so we need to position properly.
# Better approach: build the frame as a single sketch with two rectangles.

# Let's rebuild using a single workplane with two rectangles (outer and inner)
result = (
    cq.Workplane("XY")
    .rect(198.0, 60.0)  # outer: u from -99 to 99, v from -30 to 30
    .extrude(25.0)
)

# Now cut the inner rectangle
result = (
    result
    .faces(">Z")
    .workplane()
    .rect(193.0, 55.0)
    .cutThruAll()
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
