import cadquery as cq

# SOIC-8 package body: rectangular prism
# Dimensions from design plan (after cm->mm conversion):
#   length_u (along X) = 3.9 mm
#   width_v (along Z) = 4.9 mm
#   extrude_distance (along Y) = 1.55 mm

# The design plan specifies the local frame as:
#   u_dir = [1, 0, 0]  (X)
#   v_dir = [0, 0, -1] (Z)
#   w_dir = [0, 1, 0]  (Y)
# The profile is drawn in the u-v plane (XZ), and extruded along +w (+Y).
# Origin convention: bbox_min_corner.

# Profile rectangle in XZ plane:
#   u ranges from -0.195 to 0.195 -> span = 0.39 cm = 3.9 mm
#   v ranges from -0.245 to 0.245 -> span = 0.49 cm = 4.9 mm
# Since v_dir is -Z, the v coordinate maps to -Z.
#   v = -0.245 -> Z = 0.245 (max Z)
#   v = 0.245  -> Z = -0.245 (min Z)
# To place bbox_min_corner at origin (X=0, Y=0, Z=0):
#   shift X by +0.195 (from -0.195 to 0)
#   shift Z by +0.245 (from -0.245 to 0)

result = (
    cq.Workplane("XZ")
    .transformed(offset=(0.195, 0, 0.245))
    .rect(3.9, 4.9)
    .extrude(1.55)
)

cq.exporters.export(result, OUT_STEP_PATH)