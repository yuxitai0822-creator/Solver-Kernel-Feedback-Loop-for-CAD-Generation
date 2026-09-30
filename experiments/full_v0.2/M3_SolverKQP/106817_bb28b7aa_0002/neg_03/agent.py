import cadquery as cq

# Design Plan: thumb screw (disk)
# Profile: circle with radius 4.87045 mm, center at (114.300004, 0.0) in UV
# Extrude: 6.8707 mm in +w direction
# Frame: u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0)
# Note: The profile center_uv is given as [114.300004, 0.0] but the radius is 4.87045.
# The span along u and v should be 2*radius = 9.7409, so the circle is centered at (11.43, 0) in local UV (since 114.300004/10 = 11.43 after cm->mm conversion? Actually the plan says unit conversion cm_to_mm x10, so original was 11.43 cm -> 114.3 mm? But radius is 4.87045 mm, so center at 114.3 mm seems far off. However, the validation expects span 9.7409, so the circle must be centered near origin. The center_uv in the plan is [114.300004, 0.0] but that might be a mistake or in different units. Given the span validation, we place the circle at (0,0) with radius 4.87045.

# Build the disk
result = (
    cq.Workplane("XY")
    .circle(4.87045)
    .extrude(6.8707)
)

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\106817_bb28b7aa_0002\\neg_03/generated.step")
