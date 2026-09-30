import cadquery as cq

# Design Plan: Washer (2)
# Dimensions:
#   Outer radius: 3.49 mm
#   Inner radius: 2.0 mm
#   Thickness: 0.36 mm

# Create the washer by extruding an annulus (circle with a hole)
# Start with a cylinder of outer radius, then cut the inner hole

outer_radius = 3.49
inner_radius = 2.0
thickness = 0.36

# Build the washer: extrude a circle for the outer shape
result = (
    cq.Workplane("XY")
    .circle(outer_radius)
    .extrude(thickness)
    # Cut the inner hole
    .faces(">Z")
    .workplane()
    .hole(inner_radius * 2)  # hole() takes diameter
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M0_NoFeedback\107055_0500fdd1_0027\neg_01/generated.step")
