import cadquery as cq
from cadquery import exporters
import math

# Design Plan parameters
# Rectangle profile in UV frame (u along X, v along -Z, w along Y)
# UV coordinates from design plan curves (scaled from cm to mm by x10)
# Start/end points in UV: 
#   (121.17356129030935, 31.299551148092803) -> (-0.7464387096940412, 31.299551148092803)
#   (121.17356129030935, 290.379551148076) -> (121.17356129030935, 31.299551148092803)
#   (-0.7464387096940412, 290.379551148076) -> (121.17356129030935, 290.379551148076)
#   (-0.7464387096940412, 31.299551148092803) -> (-0.7464387096940412, 290.379551148076)
# These define a rectangle in UV space.
# The frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# So UV (u,v) maps to world (x, y, z) as: x = u, y = 0 (base plane), z = -v
# Extrude along +w = +Y direction by 44.45 mm (original design intent, but perturbation says 66.675 mm?)
# The perturbation description says: operator=E2_extrude_depth; original=4.445; perturbed=6.6675 (cm)
# So perturbed depth = 6.6675 cm = 66.675 mm. The previous script used 66.675 mm.
# But the design plan says distance_total = 44.45 mm (original). 
# Since this is iteration 0 and the perturbation is applied, we use the perturbed value: 66.675 mm.

# However, the design plan's validation_intents expect span_w = 44.45 mm.
# The perturbation is meant to introduce an error. So we should use the perturbed value (66.675 mm)
# to match the "negative CAD code" intent.

# Let's build the rectangle in the XZ plane (since v_dir is -Z, the sketch plane is XZ)
# Actually, the frame: u_dir=X, v_dir=-Z, w_dir=Y. The sketch plane is spanned by u and v, i.e., XZ plane.
# The rectangle in UV coordinates:
#   u range: [-0.7464387096940412, 121.17356129030935]
#   v range: [31.299551148092803, 290.379551148076]
# In world coordinates (x, y, z):
#   x = u
#   z = -v  (since v_dir = -Z)
#   y = 0 (base plane)
# So:
#   x range: [-0.7464387096940412, 121.17356129030935]
#   z range: [-290.379551148076, -31.299551148092803]
# Width in x: 121.17356129030935 - (-0.7464387096940412) = 121.92
# Width in z: -31.299551148092803 - (-290.379551148076) = 259.08
# These match the expected dimensions: length_u=1219.2 mm, width_v=2590.8 mm? No, those are 10x larger.
# Wait, the design plan says length_u = 1219.2 mm, width_v = 2590.8 mm.
# But the UV coordinates are 121.92 and 259.08. There's a factor of 10 discrepancy.
# The compiler notes say "unit_conversion_applied: cm_to_mm (x10)". 
# So the UV coordinates in the design plan are in cm? No, they are in mm after conversion.
# Actually, the curves start_uv values are 121.173... and 31.299... which are ~121.2 and ~31.3.
# The dimensions are 1219.2 and 2590.8. So the UV coordinates are 1/10 of the dimensions.
# This suggests the UV coordinates are in cm, and the dimensions are in mm.
# But the design plan says unit=mm. This is confusing.
# Let's just use the dimensions directly: length_u=1219.2 mm, width_v=2590.8 mm.
# The rectangle center is at (length_u/2, width_v/2) in UV space, but offset by the min corner.
# Actually, the UV coordinates define the rectangle corners. The span in u is 121.92, in v is 259.08.
# But the expected dimensions are 1219.2 and 2590.8. So we need to scale by 10.
# The compiler note says "cm_to_mm (x10)", meaning the original was in cm and multiplied by 10 to get mm.
# So the UV coordinates are already in mm? 121.92 mm vs 1219.2 mm expected. That's still off by 10.
# Let's re-examine: the curves start_uv values are like 121.17356129030935. 
# The expected length_u is 1219.2. The difference between max and min u is 121.92. 
# 121.92 * 10 = 1219.2. So the UV coordinates are in cm, and we need to multiply by 10 to get mm.
# But the design plan says unit=mm. This is inconsistent.
# To match the validation_intents, we need the final part to have span_u=1219.2 mm, span_v=2590.8 mm, span_w=44.45 mm.
# So we'll build the rectangle with dimensions 1219.2 mm x 2590.8 mm.

# Extrude depth: perturbed = 66.675 mm (from perturbation description).
# But validation expects 44.45 mm. We'll use the perturbed value to introduce the error.

EXT_DEPTH = 66.675  # mm (perturbed)

# Build the rectangle in the XZ plane (since v_dir = -Z, the sketch plane normal is Y)
# The rectangle will be centered at the origin for simplicity, then we can position it.
# Actually, the design plan doesn't specify absolute position, only relative dimensions.
# We'll center the rectangle at (0, 0, 0) in the XZ plane.

result = (
    cq.Workplane("XZ")
    .rect(1219.2, 2590.8, centered=True)
    .extrude(EXT_DEPTH)
)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\108244_329b1876_0000\neg_01\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)
