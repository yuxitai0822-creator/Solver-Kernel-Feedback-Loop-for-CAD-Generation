import cadquery as cq

# Design Plan: rectangular prism with dimensions 8.5 x 18.0 x 2.5 mm
# The profile is a rectangle centered at origin in the XY plane
# Extrude in the +Z direction by 2.5 mm

# Create the rectangle profile (centered at origin)
# Width along X (u-direction) = 8.5 mm, Length along Y (v-direction) = 18.0 mm
result = (
    cq.Workplane("XY")
    .rect(8.5, 18.0)  # centered rectangle
    .extrude(2.5)      # extrude upward in +Z
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\102525_06a3094b_0004\neg_03/generated.step")
