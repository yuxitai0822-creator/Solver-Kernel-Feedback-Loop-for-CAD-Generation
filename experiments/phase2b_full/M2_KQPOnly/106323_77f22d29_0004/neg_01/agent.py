import cadquery as cq

# Create the outer circle (radius 17.5 mm) and inner circle (radius 12.5 mm)
# The annulus is centered at (0,0) in the XY plane
# Extrude symmetrically by total distance 10 mm (5 mm each side)

result = (
    cq.Workplane("XY")
    .circle(17.5)  # outer radius
    .circle(12.5)  # inner radius (creates a hole)
    .extrude(10.0, both=True)  # symmetric extrusion, total height 10 mm
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\106323_77f22d29_0004\\neg_01/generated.step")
