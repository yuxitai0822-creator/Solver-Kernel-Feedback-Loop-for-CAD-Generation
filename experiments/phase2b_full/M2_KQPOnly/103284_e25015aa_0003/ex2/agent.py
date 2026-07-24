import cadquery as cq

# Design Plan: extruded circle (disk)
# Dimensions: radius 25.4 mm, extrude distance 8.89 mm
# Center in UV plane: (16.994661, 17.998557) - but for a single disk we can place at origin
# The plan indicates a circle with radius 2.54 in UV but dimensions say radius 25.4 (likely unit conversion)
# The compiler notes mention cm_to_mm (x10), so radius 2.54 cm = 25.4 mm, extrude 0.889 cm = 8.89 mm
# We'll create a cylinder (extruded circle) centered at origin

result = cq.Workplane("XY").circle(25.4).extrude(8.89)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\103284_e25015aa_0003\\ex2/generated.step")
