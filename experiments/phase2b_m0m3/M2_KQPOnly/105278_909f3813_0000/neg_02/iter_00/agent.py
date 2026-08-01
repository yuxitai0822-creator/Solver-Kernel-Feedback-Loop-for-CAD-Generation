import cadquery as cq
from cadquery import exporters

# Design Plan: rectangular prism 12mm x 60mm x 40mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile rectangle in uv-plane: u from -0.6 to 0.6 (span 1.2 -> 12mm after cm->mm conversion?)
# Wait: design plan says length_u=12.0, width_v=60.0, extrude_distance=40.0
# The profile curves show start_uv/end_uv values like -0.6 to 0.6 (span 1.2) and -3.0 to 3.0 (span 6.0)
# These are in cm (since compiler notes say cm_to_mm x10). So 1.2cm = 12mm, 6.0cm = 60mm.
# Extrude distance is already in mm: 40.0mm.
# The frame has u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# So sketch plane is XZ (u=x, v=-z), extrude along y (w_dir)

# Build rectangle centered at origin in XZ plane
# Width along u (x): 12mm, height along v (z): 60mm
# But v_dir is [0,0,-1], so positive v goes in -z direction.
# The rectangle spans from u=-6 to u=6, v=-30 to v=30 (in mm)
# Since v_dir is -z, v=30 maps to z=-30, v=-30 maps to z=30
# So the rectangle goes from z=-30 to z=30, which is centered at z=0.

result = (
    cq.Workplane("XZ")
    .center(0, 0)
    .rect(12.0, 60.0, centered=True)
    .extrude(40.0)  # extrude along Y (positive direction)
)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\105278_909f3813_0000\neg_02\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)