import cadquery as cq
from cadquery import exporters
import math

# Design Plan parameters
# Rectangle profile in UV frame:
#   u: [1,0,0], v: [0,0,-1], w: [0,1,0]
#   rectangle corners in UV: 
#     start_uv = (121.17356129030935, 31.299551148092803)
#     end_uv = (-0.7464387096940412, 31.299551148092803)  (line along u)
#     start_uv = (121.17356129030935, 290.379551148076)  (line along v)
#     end_uv = (-0.7464387096940412, 290.379551148076)  (line along v)
#   So u range: [-0.7464, 121.1736] -> width = 121.92
#   v range: [31.2996, 290.3796] -> height = 259.08
#   But dimensions say length_u = 1219.2, width_v = 2590.8 (10x larger)
#   This is because unit conversion cm->mm was applied (x10).
#   The UV coordinates in the design plan are in cm, so multiply by 10.
#   Actually the design plan says unit_conversion_applied: cm_to_mm (x10)
#   So the raw UV values are in cm, we need to multiply by 10 to get mm.
#   Let's verify: 121.1736 * 10 = 1211.736, matches previous script.
#   Similarly: 31.2996 * 10 = 312.996, 290.3796 * 10 = 2903.796
#   But previous script had y range 572.0755 to 2644.7155, which is different.
#   Let's re-examine: the design plan says frame u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
#   So in the sketch plane (XZ), u maps to X, v maps to -Z.
#   The UV coordinates: u from -0.7464 to 121.1736, v from 31.2996 to 290.3796
#   After cm->mm: u from -7.464 to 1211.736, v from 312.996 to 2903.796
#   But the previous script had y (which is v) from 572.0755 to 2644.7155
#   That's a different range. Let's check the curves more carefully.
#   Curves:
#     1: start_uv=(121.1736, 31.2996), end_uv=(-0.7464, 31.2996)  -> horizontal in u direction
#     2: start_uv=(121.1736, 290.3796), end_uv=(121.1736, 31.2996)  -> vertical in v direction
#     3: start_uv=(-0.7464, 290.3796), end_uv=(121.1736, 290.3796)  -> horizontal in u direction
#     4: start_uv=(-0.7464, 31.2996), end_uv=(-0.7464, 290.3796)  -> vertical in v direction
#   So the rectangle corners in UV are:
#     (-0.7464, 31.2996), (121.1736, 31.2996), (121.1736, 290.3796), (-0.7464, 290.3796)
#   After cm->mm: 
#     (-7.464, 312.996), (1211.736, 312.996), (1211.736, 2903.796), (-7.464, 2903.796)
#   But the previous script had y from 572.0755 to 2644.7155
#   That's different. Let me check the previous script's numbers:
#     start: (1211.7356129030936, 572.0755114809111)
#     end: (-7.4643870969404125, 572.0755114809111)
#   So x matches (1211.736 vs 1211.736, -7.464 vs -7.464)
#   But y is 572.0755 instead of 312.996
#   This suggests the v coordinate might have been transformed differently.
#   Actually, looking at the frame: v_dir = [0,0,-1], so v maps to -Z.
#   The design plan says origin_convention: bbox_min_corner
#   So the origin is at the minimum corner of the bounding box.
#   The previous script used WORKPLANE='XZ' and y coordinates directly.
#   In the XZ plane, y is the Z coordinate. So v maps to -Z.
#   If v ranges from 31.2996 to 290.3796, then Z ranges from -290.3796 to -31.2996
#   After cm->mm: Z from -2903.796 to -312.996
#   But the previous script had positive y values (572 to 2644).
#   This is confusing. Let me just use the previous script's coordinates
#   since they produced a valid model.
#   Actually, the previous script had a bug: it used WORKPLANE='XZ' but
#   the coordinates were in XY plane. Let me re-examine.
#   The previous script's coordinates:
#     x: -7.464 to 1211.736
#     y: 572.0755 to 2644.7155
#   These are in the XY plane. The extrude direction was [0,1,0] (Y axis).
#   So the rectangle is in XZ plane? No, if WORKPLANE='XZ', then
#   the sketch is in XZ plane, and extrude is along Y.
#   But the coordinates given are (x, y) where x is X and y is Z.
#   So the rectangle is in XZ plane with:
#     X: -7.464 to 1211.736
#     Z: 572.0755 to 2644.7155
#   Extrude along Y by 44.45 mm.
#   This matches the design plan: u->X, v->-Z, w->Y
#   But v ranges from 31.2996 to 290.3796, so -v ranges from -290.3796 to -31.2996
#   After cm->mm: -v from -2903.796 to -312.996
#   But the previous script has Z from 572 to 2644, which is positive.
#   This suggests the v coordinate was transformed differently.
#   Let me just use the previous script's coordinates directly since
#   they are known to work. The perturbation description says
#   "original=259.0799999999832; perturbed=207.2639999999866"
#   This might affect one of the dimensions. Let me check:
#   The original v span is 290.3796 - 31.2996 = 259.08
#   After cm->mm: 2590.8 mm
#   The perturbed value is 207.264, which is 20% less.
#   So the v span should be reduced by 20%.
#   Original v span: 259.08 cm = 2590.8 mm
#   Perturbed v span: 207.264 cm = 2072.64 mm
#   So the new v range should be:
#     v_min = 31.2996
#     v_max = v_min + 207.264 = 238.5636
#   After cm->mm: v_min = 312.996, v_max = 2385.636
#   But the previous script had y from 572.0755 to 2644.7155
#   That's a different baseline. Let me check if there's an offset.
#   572.0755 - 312.996 = 259.0795 (which is the original v span)
#   So the previous script added the v span to the v_min.
#   Actually: 312.996 + 259.08 = 572.076, which matches.
#   So the previous script's y coordinates are:
#     y_min = v_min_mm + original_v_span_mm? No, that doesn't make sense.
#   Let me recalculate: v_min_mm = 31.2996 * 10 = 312.996
#   v_max_mm = 290.3796 * 10 = 2903.796
#   But previous script has y_min = 572.0755, y_max = 2644.7155
#   572.0755 - 312.996 = 259.0795 (original v span)
#   2644.7155 - 2903.796 = -259.0805 (negative of original v span)
#   So it seems like the previous script shifted the coordinates:
#     y_min = v_min_mm + original_v_span = 312.996 + 259.08 = 572.076
#     y_max = v_max_mm - original_v_span = 2903.796 - 259.08 = 2644.716
#   This is a weird transformation. Let me just use the design plan
#   coordinates directly without the shift.
#   Actually, I think the previous script might have had a bug.
#   Let me just use the design plan coordinates correctly.
#   The design plan says:
#     u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
#     origin_convention: bbox_min_corner
#   So the origin is at the minimum corner of the bounding box.
#   The rectangle in UV coordinates:
#     u: [-0.7464, 121.1736]  (width = 121.92 cm = 1219.2 mm)
#     v: [31.2996, 290.3796]  (height = 259.08 cm = 2590.8 mm)
#   In XYZ coordinates (after cm->mm):
#     X = u * 10: [-7.464, 1211.736]
#     Z = -v * 10: [-2903.796, -312.996]
#   But the origin is at bbox_min_corner, so we need to shift so that
#   the minimum corner is at (0,0,0).
#   Actually, the design plan says the coordinates are already in the
#   part_local frame with origin at bbox_min_corner.
#   So the rectangle should be placed such that its minimum corner is at origin.
#   The minimum corner in UV is (-0.7464, 31.2996)
#   After cm->mm: (-7.464, 312.996)
#   In XYZ: X = -7.464, Z = -312.996
#   To make this the origin, we shift by (+7.464, +312.996)
#   So the rectangle in XYZ:
#     X: [0, 1219.2]
#     Z: [0, -2590.8]  (since v goes from 31.2996 to 290.3796, -v goes from -312.996 to -2903.796)
#   Wait, that gives negative Z. Let me reconsider.
#   The v_dir is [0,0,-1], so v maps to -Z.
#   v_min = 31.2996 cm = 312.996 mm -> Z_min = -312.996 mm
#   v_max = 290.3796 cm = 2903.796 mm -> Z_max = -2903.796 mm
#   So Z ranges from -2903.796 to -312.996 (negative values)
#   The bbox_min_corner in Z is -2903.796
#   To shift origin to bbox_min_corner, we add 2903.796 to all Z coordinates.
#   So Z becomes: [0, 2590.8]
#   Similarly for X: X_min = -7.464, X_max = 1211.736
#   bbox_min_corner in X is -7.464
#   Shift: add 7.464 -> X: [0, 1219.2]
#   So the rectangle in XYZ (with origin at bbox_min_corner):
#     X: [0, 1219.2]
#     Z: [0, 2590.8]
#   This matches the dimensions: length_u = 1219.2, width_v = 2590.8
#   And the extrude is along w_dir = [0,1,0] (Y axis) by 44.45 mm.
#   So the final box is:
#     X: [0, 1219.2]
#     Y: [0, 44.45]
#     Z: [0, 2590.8]
#   This is a flat plate/panel.
#   Now, the perturbation: "original=259.0799999999832; perturbed=207.2639999999866"
#   This is the v span (height). Original: 259.08 cm = 2590.8 mm
#   Perturbed: 207.264 cm = 2072.64 mm
#   So the new Z span should be 2072.64 mm instead of 2590.8 mm.
#   The new Z range: [0, 2072.64]
#   Let me build this.

# Build the rectangle in the XZ plane
# The rectangle spans X: [0, 1219.2], Z: [0, 2072.64] (perturbed)
# Extrude along Y by 44.45 mm

result = (
    cq.Workplane("XZ")
    .rect(1219.2, 2072.64, centered=False)
    .extrude(44.45)
)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\108244_329b1876_0000\neg_03\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)
