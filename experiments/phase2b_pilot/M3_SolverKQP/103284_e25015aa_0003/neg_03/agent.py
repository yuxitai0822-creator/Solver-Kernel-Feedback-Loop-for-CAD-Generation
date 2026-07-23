import cadquery as cq

# Build the extruded circle (disk) based on the design plan
# The design plan specifies a unit conversion of cm_to_mm (x10) was applied.
# The profile radius in the 'profiles' section is 2.54 mm (from the circle curve),
# while the 'dimensions' section lists 25.4 mm (which is 2.54 cm converted to mm).
# The validation intents expect spans of 50.8 mm (diameter of 25.4 mm radius).
# Therefore, we use radius = 25.4 mm to satisfy the span constraints.

radius = 25.4
center_x = 16.994661
center_y = 17.998557
extrude_distance = 8.89

result = (
    cq.Workplane("XY")
    .center(center_x, center_y)
    .circle(radius)
    .extrude(extrude_distance)
)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M3_SolverKQP\103284_e25015aa_0003\neg_03/generated.step"

cq.exporters.export(result, OUT_STEP_PATH)
