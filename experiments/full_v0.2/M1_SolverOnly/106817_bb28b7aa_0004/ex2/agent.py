import cadquery as cq

# Design Plan: washer (extruded annulus)
# Dimensions:
#   outer radius = 5.5372 mm (from dimensions.outer_radius.value)
#   inner radius = 1.9812 mm (from dimensions.inner_radius.value)
#   thickness (extrude distance) = 1.3208 mm
# The profile center in UV is at (-25.400001, 12.7) but we place the sketch at origin for simplicity.
# The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0).
# Extrude direction is +w, which is +Y in world coordinates.

# Build the washer by creating a circle for outer and inner, then extruding.

# Create the outer circle
outer = cq.Workplane("XY").circle(5.5372)

# Create the inner circle (hole) by subtracting
result = outer.circle(1.9812).extrude(1.3208)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\106817_bb28b7aa_0004\\ex2/generated.step")
