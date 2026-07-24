import cadquery as cq

# Design Plan: extruded circle (disk) with radius 7.5 mm and height 20.0 mm
# The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means the circle lies in the u-v plane (x-z plane) and extrudes along +w (y direction)

# Create the circle profile on the XY plane (default workplane), then extrude along Z
# To match the frame: circle in x-z plane, extrude along y.
# We can use workplane on XZ plane (front) and extrude in Y direction.

result = (
    cq.Workplane("XZ")  # circle lies in XZ plane (u=x, v=z)
    .circle(7.5)         # radius 7.5 mm
    .extrude(20.0)       # extrude along Y (positive Y = +w direction)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\104524_f829aab2_0001\neg_01/generated.step")
