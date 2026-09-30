import cadquery as cq
import os

# Dimensions from design plan (unit conversion cm->mm applied)
length_u = 209.55  # span along u (x-axis)
width_v = 57.912   # span along v (z-axis, mapped to y in CadQuery default)
extrude_w = 19.05  # span along w (y-axis, mapped to z in CadQuery default)

# Build the extruded rectangle
# The design plan frame maps u->X, v->-Z, w->Y.
# In CadQuery's default coordinate system (X=right, Y=forward, Z=up),
# we sketch on the XZ plane (u=X, v=Z) and extrude along Y (w=Y).
result = (
    cq.Workplane("XZ")
    .rect(length_u, width_v)
    .extrude(extrude_w)
)

# Ensure output directory exists
out_dir = os.path.dirname(OUT_STEP_PATH)
if out_dir:
    os.makedirs(out_dir, exist_ok=True)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
