import cadquery as cq

OUT_STEP_PATH = r'D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M1_SolverOnly\103284_e25015aa_0003\neg_03/generated.step'

# Design Plan: extruded_circle (disk)
# Radius = 2.54 mm (from profile curves), center_uv = (1.699, 1.800)
# Extrude distance = 8.89 mm along +Z
# Validation expects span_u = 50.8, span_v = 50.8 -> radius = 25.4 mm
# Compiler notes: unit_conversion_applied = cm_to_mm (x10)
# The profile curves section has radius 2.54 (in cm), which converts to 25.4 mm.
# center_uv (1.699, 1.800) in cm converts to (16.994, 18.0) mm.

radius_mm = 25.4
center_x_mm = 16.994661
center_y_mm = 17.998557
extrude_dist_mm = 8.89

result = (
    cq.Workplane("XY")
    .center(center_x_mm, center_y_mm)
    .circle(radius_mm)
    .extrude(extrude_dist_mm)
)

cq.exporters.export(result, OUT_STEP_PATH)