import cadquery as cq
from cadquery import exporters

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\102295_86f842dd_0000\neg_02\iter_01/generated.step"

# Design Plan: stadium extrusion
# Stadium profile: two arcs (radius=10.0) connected by two lines (straight_length=28.0)
# The profile lies in the XZ plane (u=x, v=z), extrude along Y (w direction)
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# So sketch plane is XZ, extrude along +Y

# Stadium dimensions from design plan:
# radius = 10.0 mm (explicit)
# straight_length = 28.0 mm (inferred from point span)
# Extrude distance = 4.0 mm along +Y

# Build the stadium profile in the XZ plane
# Center the stadium at origin for simplicity
# The stadium consists of:
# - Left arc: center at (-14.0, 0, 0), radius 10.0, from 90° to 270° (or 0 to 180 in local UV)
# - Top line: from (-14.0, 0, 10.0) to (14.0, 0, 10.0)
# - Right arc: center at (14.0, 0, 0), radius 10.0, from 270° to 90° (or 0 to 180 in local UV)
# - Bottom line: from (14.0, 0, -10.0) to (-14.0, 0, -10.0)

# Using cadquery's Workplane on XZ plane
result = (
    cq.Workplane("XZ")
    .moveTo(-14.0, 10.0)  # Start at top-left junction
    .threePointArc((0.0, 20.0), (14.0, 10.0))  # Left arc (center at -14,0, radius 10)
    .lineTo(14.0, -10.0)  # Right side line going down
    .threePointArc((0.0, -20.0), (-14.0, -10.0))  # Right arc (center at 14,0, radius 10)
    .lineTo(-14.0, 10.0)  # Left side line going up
    .close()
    .extrude(4.0)  # Extrude along Y (positive direction)
)

# Export to STEP
exporters.export(result, OUT_STEP_PATH)
