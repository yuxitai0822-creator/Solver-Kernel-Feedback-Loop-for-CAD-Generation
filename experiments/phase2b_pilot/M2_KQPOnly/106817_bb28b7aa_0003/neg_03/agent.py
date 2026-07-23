import cadquery as cq

# Build an extruded circle (cylinder) representing the ruler holder w/screw
# The design plan specifies:
#   - primitive_type: extruded_circle
#   - radius: 4.7117 mm (from dimensions.profiles[0].radius)
#   - extrude distance: 12.192 mm (along +w, which maps to +Y in part_local frame)
#   - center_uv: [50.800002, 63.500002] (in the sketch plane)
#   - frame: u=[1,0,0] (X), v=[0,0,-1] (-Z), w=[0,1,0] (Y)
#   - origin_convention: bbox_min_corner

radius = 4.7117
extrude_distance = 12.192
center_x = 50.800002
center_y = 63.500002

# Create the cylinder by extruding a circle on the XZ plane (since v_dir is -Z)
# and then translating to the correct center position.
# The sketch plane is defined by u (X) and v (-Z), so the circle lies in XZ.
# Extrusion is along w (+Y).

result = (
    cq.Workplane("XZ")
    .transform(offset=(center_x, 0, -center_y))
    .circle(radius)
    .extrude(extrude_distance)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M2_KQPOnly\106817_bb28b7aa_0003\neg_03/generated.step")
