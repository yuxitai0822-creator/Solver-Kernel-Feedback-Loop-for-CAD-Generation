import cadquery as cq

# Create a rectangular prism with dimensions: length_u=39.0, width_v=68.0, extrude_distance=10.0
# The profile is a rectangle in the uv-plane, then extruded in the +w direction.
# Based on the design plan, the rectangle corners are at uv coordinates:
#   (-3.9, 0.0) to (0.0, 6.8) in cm, but unit conversion cm->mm (x10) gives:
#   (-39.0, 0.0) to (0.0, 68.0) in mm.
# The extrude distance is 10.0 mm.

result = (
    cq.Workplane("XY")
    .rect(39.0, 68.0, centered=False)
    .extrude(10.0)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\102175_699d5e7c_0003\\ex2/generated.step")
