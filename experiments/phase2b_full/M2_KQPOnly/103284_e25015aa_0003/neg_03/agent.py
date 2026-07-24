import cadquery as cq

# Design Plan: extruded circle (disk)
# Dimensions:
#   radius = 25.4 mm (from dimensions.profiles[0].radius.value)
#   extrude distance = 8.89 mm (from dimensions.extrude_distance.value)
#   center_uv = [16.994661, 17.998557] (from dimensions.profiles[0].center_uv)
#   profile circle center_uv = [1.6994660913961006, 1.7998556732836484] (from profiles[0].rings[0].curves[0].center_uv)
#   profile circle radius = 2.54 (from profiles[0].rings[0].curves[0].radius)
#
# Note: The design plan shows two different center_uv values and two different radii.
# The "dimensions" section gives radius=25.4 and center_uv=[16.994661, 17.998557].
# The "profiles" section gives radius=2.54 and center_uv=[1.6994660913961006, 1.7998556732836484].
# The validation intents expect span_u=50.8, span_v=50.8, span_w=8.89.
# span_u=50.8 implies diameter=50.8, so radius=25.4. This matches the dimensions section.
# The profile radius=2.54 seems to be a scaled version (maybe cm to mm conversion factor 10).
# We use the dimensions section values: radius=25.4, extrude=8.89.
# The center_uv is just the position in the sketch plane; we place the circle at origin for simplicity.

result = (
    cq.Workplane("XY")
    .circle(25.4)
    .extrude(8.89)
)

# Export
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\103284_e25015aa_0003\neg_03/generated.step")
