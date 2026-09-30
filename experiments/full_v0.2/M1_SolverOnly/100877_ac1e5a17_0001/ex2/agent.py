import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# Length (u) = 279.4 mm, Width (v) = 215.9 mm, Extrude distance (w) = 1.5875 mm

# Note: The design plan uses cm->mm conversion (x10), so the values are already in mm.
# The rectangle profile is defined in UV coordinates:
#   start_uv: (0.0, 21.59) -> (0.0, 0.0) -> (27.94, 0.0) -> (27.94, 21.59) -> back to start
# These UV values are in cm originally, converted to mm: multiply by 10
#   (0, 215.9) -> (0, 0) -> (279.4, 0) -> (279.4, 215.9) -> back to (0, 215.9)

# Build the plate
result = (
    cq.Workplane("XY")
    .rect(279.4, 215.9)  # rectangle centered at origin, width=279.4, height=215.9
    .extrude(1.5875)      # extrude in +Z direction
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\100877_ac1e5a17_0001\ex2/generated.step")
