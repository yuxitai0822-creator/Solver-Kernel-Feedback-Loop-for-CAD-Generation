import cadquery as cq

# Design Plan: thumb screw (disk)
# Extruded circle with radius 4.87045 mm and height 6.8707 mm
# The profile circle center is at (11.43, 0) in UV, but in 3D we place it at origin
# Frame: u_dir=(1,0,0), v_dir=(0,0,-1), w_dir=(0,1,0)
# Extrude direction is +w, which is (0,1,0)

# Create the circle profile on the XY plane (normal = (0,0,1))
# But the frame's v_dir is (0,0,-1) which is opposite to normal, so we work in XY plane
# The circle center in UV is (11.43, 0), but that's in the local frame.
# Since we want the part centered at origin for simplicity, we place the circle at (0,0)
# The radius is 4.87045 mm

result = (
    cq.Workplane("XY")
    .circle(4.87045)
    .extrude(6.8707)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\106817_bb28b7aa_0002\neg_02/generated.step")
