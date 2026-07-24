import cadquery as cq

# Design Plan: extruded rectangular frame (hollow box)
# Outer dimensions: 40 x 40 mm (u x v), extrude 520 mm along w
# Wall thickness: (40 - 37.6)/2 = 1.2 mm

# Create outer rectangle profile on XY plane (u=x, v=y, w=z)
# Outer rectangle: centered at origin, width=40, height=40
# Inner rectangle: centered at origin, width=37.6, height=37.6

# Build the frame by extruding a rectangular ring
result = (
    cq.Workplane("XY")
    .rect(40, 40)  # outer rectangle
    .rect(37.6, 37.6)  # inner rectangle (cutout)
    .extrude(520.0)  # extrude along +z (w direction)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\101817_b02acd9f_0001\neg_02/generated.step")
