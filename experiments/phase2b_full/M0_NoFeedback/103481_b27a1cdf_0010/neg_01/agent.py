import cadquery as cq

# Create a rectangular prism with dimensions 101.6mm x 101.6mm x 38.1mm
# The profile is centered at origin, extruded in +w direction

# Create the rectangle profile centered at origin
# From the design plan, the rectangle spans from (-5.08, -5.08) to (5.08, 5.08) in UV space
# But the actual dimensions are 101.6mm x 101.6mm, so the half-dimensions are 50.8mm
# The UV coordinates in the plan appear to be scaled by 0.1 (cm to mm conversion factor of 10)
# So 5.08 * 10 = 50.8mm half-dimension

result = (
    cq.Workplane("XY")
    .rect(101.6, 101.6)  # width=101.6mm, height=101.6mm
    .extrude(38.1)  # extrude 38.1mm in +Z direction
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\103481_b27a1cdf_0010\neg_01/generated.step")