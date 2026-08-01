import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\108850_0dcd5ef1_0002\neg_03\iter_00/generated.step"

# Design plan: extruded rectangle, 171.45 x 38.1 mm, extrude 6.35 mm
# Perturbation: original v-span 38.1 -> perturbed to 30.48 (3.81 -> 3.048 in uv? Actually original 3.81 -> 3.048, but that's the v-coordinate offset?)
# The design plan says: original=3.81; perturbed=3.048. This likely refers to the v-coordinate of the rectangle's lower edge.
# In the profile curves, start_uv and end_uv show v coordinates: 0.0 and 3.81. So the rectangle spans v from 0 to 3.81 (width_v = 38.1 mm after scaling? Wait: dimensions say width_v = 38.1, but uv coordinates show 3.81. There's a factor of 10: uv coords are in cm? Actually the design plan says unit_conversion_applied: cm_to_mm (x10). So uv coords are in cm? The rectangle in uv: u from 0 to 17.145, v from 0 to 3.81. After scaling by 10, that's 171.45 x 38.1 mm. So the perturbation changes the v-coordinate from 3.81 to 3.048 (cm), which after scaling gives 30.48 mm. So the rectangle should be 171.45 x 30.48 mm.
# Let's build the rectangle with these dimensions.

# Build the base rectangle on XZ plane (as per previous script's WORKPLANE = 'XZ')
# But the design plan's frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]. So u is X, v is -Z, w is Y.
# So the profile lies in the X-Z plane (u-v plane), extrude along Y (w).
# We'll use Workplane("XZ") and draw rectangle centered at origin.

length_u = 171.45  # mm
width_v = 30.48    # mm (perturbed: 3.048 cm * 10 = 30.48 mm)
extrude_dist = 6.35  # mm

# Create workplane on XZ
wp = cq.Workplane("XZ")

# Draw rectangle centered at origin
result = wp.rect(length_u, width_v).extrude(extrude_dist)

# Export
import os
os.makedirs(os.path.dirname(OUT_STEP_PATH), exist_ok=True)
exporters.export(result, OUT_STEP_PATH)
