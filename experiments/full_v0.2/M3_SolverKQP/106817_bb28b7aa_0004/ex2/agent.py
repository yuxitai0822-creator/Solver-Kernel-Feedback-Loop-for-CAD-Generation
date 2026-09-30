import cadquery as cq

# Design Plan: washer (extruded annulus)
# Dimensions:
#   Outer radius: 5.5372 mm (from dimensions.profiles[0].outer_radius.value)
#   Inner radius: 1.9812 mm (from dimensions.profiles[0].inner_radius.value)
#   Thickness: 1.3208 mm (from extrude.distance_total.value)
# Note: The profile center_uv is given as [-25.400001, 12.7] but this is in the local frame.
# The annulus is centered at the origin for simplicity; the exact position is not critical for a single part.

# Build the washer by extruding a circle with a hole.
outer_radius = 5.5372
inner_radius = 1.9812
thickness = 1.3208

# Create the outer cylinder
result = cq.Workplane("XY").circle(outer_radius).extrude(thickness)

# Cut the inner hole
result = result.faces(">Z").workplane().hole(inner_radius * 2, thickness)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\106817_bb28b7aa_0004\\ex2/generated.step")
