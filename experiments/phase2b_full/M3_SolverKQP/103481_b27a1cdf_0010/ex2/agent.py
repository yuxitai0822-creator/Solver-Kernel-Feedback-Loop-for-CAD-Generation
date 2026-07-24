import cadquery as cq

# Create a rectangular prism with dimensions 101.6mm x 101.6mm x 38.1mm
# The profile is centered at origin (as per UV coordinates from -5.08 to 5.08, which after cm->mm conversion gives -50.8 to 50.8)
# Actually the UV coordinates are in mm already: -5.08 to 5.08, but the dimensions say 101.6mm length/width.
# This means the rectangle spans from -50.8 to 50.8 in both U and V directions.
# The extrude distance is 38.1mm in the +W direction.

# Build the result
result = (
    cq.Workplane("XY")
    .rect(101.6, 101.6)
    .extrude(38.1)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\103481_b27a1cdf_0010\\ex2/generated.step")
