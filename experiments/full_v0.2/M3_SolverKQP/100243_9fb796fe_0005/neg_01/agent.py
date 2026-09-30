import cadquery as cq

# Create a rectangular profile in the UV plane
# From the design plan:
#   u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
#   rectangle corners in UV: (-58.2782, -12.0401) to (-56.3782, -13.9401)
#   This gives a 19.0 x 19.0 mm square (since 58.2782-56.3782 = 1.9? Wait, check: 58.2782-56.3782 = 1.9? Actually 58.2782-56.3782 = 1.9, but dimensions say 19.0. 
#   The coordinates are in cm originally, converted to mm by x10 factor. So original cm: (-5.82782, -1.20401) to (-5.63782, -1.39401) -> width = 0.19 cm = 1.9 mm? No, 0.19 cm = 1.9 mm, but expected is 19.0 mm.
#   Let's re-check: The compiler note says "unit_conversion_applied: cm_to_mm (x10)". So the UV values are already in mm after conversion? 
#   Actually the values in the plan are -58.2782 etc. If these are mm, then width = 1.9 mm, not 19.0. But dimensions say 19.0 mm.
#   Let's compute: 58.2782 - 56.3782 = 1.9. That's 1.9 mm, not 19.0. 
#   But the dimensions say length_u = 19.0, width_v = 19.0. 
#   The compiler note says cm_to_mm (x10). So original cm values were -5.82782 and -5.63782, difference = 0.19 cm = 1.9 mm. After x10 conversion, that becomes 19.0 mm. 
#   So the UV coordinates in the plan are already in mm after conversion? Actually 0.19 cm * 10 = 1.9 mm, not 19.0. 
#   Wait: 0.19 cm = 1.9 mm. Multiply by 10 gives 19 mm. So the plan values are already the converted mm values? 
#   Let's check: -58.2782 / 10 = -5.82782 cm. -56.3782 / 10 = -5.63782 cm. Difference = 0.19 cm = 1.9 mm. Then *10 = 19 mm. 
#   So the plan values are already in mm after conversion. The difference is 1.9, but expected is 19.0. There's a factor of 10 discrepancy.
#   Actually, looking more carefully: the compiler note says "cm_to_mm (x10)". The original sketch was in cm, and the values were multiplied by 10 to get mm. 
#   So original cm: (-5.82782, -1.20401) to (-5.63782, -1.39401). Width in cm = 0.19 cm = 1.9 mm. After x10: 19 mm. 
#   But the plan values are -58.2782 which is -5.82782 * 10 = -58.2782? No, -5.82782 * 10 = -58.2782. Yes! So the plan values are already the converted mm values.
#   Then width = 58.2782 - 56.3782 = 1.9 mm. But expected is 19.0 mm. 
#   Something is off. Let's re-read: "length_u: 19.0, width_v: 19.0". The UV coordinates span from -58.2782 to -56.3782, difference = 1.9. 
#   But the dimension says 19.0. So either the coordinates are wrong or the dimension is wrong. 
#   Given the dimension is explicit and the coordinates are derived from a sketch, I'll trust the explicit dimension (19.0 mm) and adjust the coordinates.
#   The center of the rectangle in UV: u_center = (-58.2782 + -56.3782)/2 = -57.3282, v_center = (-12.0401 + -13.9401)/2 = -12.9901
#   Half-width = 19.0/2 = 9.5. So u from -57.3282-9.5 = -66.8282 to -57.3282+9.5 = -47.8282? That doesn't match.
#   Actually, let's just use the dimensions directly: a 19x19 mm square centered at the given center.
#   But the design plan specifies exact UV coordinates. I'll use the given coordinates but scale them to match the 19.0 mm dimension.
#   The given UV span is 1.9, but should be 19.0. So scale factor = 10. 
#   So multiply all UV coordinates by 10: u from -582.782 to -563.782, v from -120.401 to -139.401. That gives width = 19.0, height = 19.0.
#   But wait, the plan says the values are already in mm after cm_to_mm conversion. So -58.2782 mm to -56.3782 mm is 1.9 mm. 
#   I think there's an inconsistency in the plan. I'll go with the explicit dimensions (19.0 mm) and create a proper 19x19 mm square.
#   The frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]. So the profile is in the XZ plane (u=X, v=-Z), extruded along Y (w=Y).
#   Extrude distance = 200.0 mm along +w (positive Y).

# Let's create the rectangle centered at the given center point, with dimensions 19x19 mm.
# Center in UV: u_c = (-58.2782 + -56.3782)/2 = -57.3282, v_c = (-12.0401 + -13.9401)/2 = -12.9901
# But to match the 19.0 mm dimension, we need to scale. Actually, let's just use the given coordinates as-is and see if the dimension is 1.9 or 19.0.
# The plan says length_u = 19.0, width_v = 19.0. The UV coordinates give 1.9. I'll trust the explicit dimension and create a 19x19 rectangle.
# The center point in UV: (-57.3282, -12.9901). Rectangle from (-57.3282-9.5, -12.9901-9.5) to (-57.3282+9.5, -12.9901+9.5)
# = (-66.8282, -22.4901) to (-47.8282, -3.4901)

# But wait, the v_dir is [0,0,-1], so v coordinate goes along negative Z. The rectangle in UV maps to XZ plane.
# u -> X, v -> -Z. So point (u, v) in UV maps to (u, 0, -v) in 3D.

# Let's use the workplane approach: create a rectangle on the XZ plane, then extrude along Y.

result = (
    cq.Workplane("XZ")
    .center(-57.3282, 12.9901)  # center in XZ: u->X, v->-Z, so v_c = -12.9901 -> Z = 12.9901
    .rect(19.0, 19.0)
    .extrude(200.0)
)

# Export
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M3_SolverKQP\100243_9fb796fe_0005\neg_01/generated.step")
