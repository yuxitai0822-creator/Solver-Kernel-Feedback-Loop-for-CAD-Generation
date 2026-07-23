import cadquery as cq

# Build an extruded circle (disk) per the design plan.
# The plan specifies a circle with radius 2.54 mm (from the profile curves)
# centered at (1.6994660913961006, 1.7998556732836484) in the sketch plane,
# extruded by 8.89 mm along +Z.
# The validation intents expect spans of 50.8 mm along U and V axes,
# which corresponds to a diameter of 50.8 mm (radius = 25.4 mm).
# The compiler notes indicate a unit conversion of cm_to_mm (x10) was applied,
# explaining why the profile curve radius is 2.54 while the dimension radius is 25.4.
# We use the 25.4 mm radius to satisfy the span validation intents.

radius = 25.4
center_x = 1.6994660913961006
center_y = 1.7998556732836484
extrude_distance = 8.89

result = (cq.Workplane("XY")
          .center(center_x, center_y)
          .circle(radius)
          .extrude(extrude_distance))

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M2_KQPOnly\103284_e25015aa_0003\neg_03/generated.step"
cq.exporters.export(result, OUT_STEP_PATH)