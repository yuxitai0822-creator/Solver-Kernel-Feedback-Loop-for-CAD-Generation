import cadquery as cq

# Design Plan: extruded rectangle (flat plate/panel)
# Dimensions: length_u = 1219.2 mm, width_v = 2590.8 mm, extrude_distance = 44.45 mm
# The frame defines u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# The rectangle profile in UV space has corners:
#   (121.17356129030935, 31.299551148092803) -> (-0.7464387096940412, 31.299551148092803)
#   (121.17356129030935, 290.379551148076) -> (-0.7464387096940412, 290.379551148076)
# The span in U is ~121.92, but the inferred length_u is 1219.2 mm (scale factor 10 from cm->mm).
# The span in V is ~259.08, inferred width_v is 2590.8 mm.
# We'll create a rectangle centered at origin with those dimensions, then extrude along w_dir (Y axis).

# Create the rectangle profile on the XY plane (since u_dir = X, v_dir = Z negative, w_dir = Y)
# Actually, to match the frame: u along X, v along -Z, w along Y.
# So the profile lies in the X-Z plane (with v along -Z).
# We'll create a workplane on the XZ plane, draw rectangle, then extrude along Y.

length_u = 1219.2  # mm
width_v = 2590.8   # mm
extrude_dist = 44.45  # mm

# Build the rectangle centered at origin, aligned with X and Z axes
result = (cq.Workplane("XZ")
          .rect(length_u, width_v, centered=True)
          .extrude(extrude_dist))

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
