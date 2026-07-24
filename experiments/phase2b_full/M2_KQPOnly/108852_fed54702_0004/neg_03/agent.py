import cadquery as cq

# Design Plan: ThreadedRod v1 (2) - Disk with extruded circle
# Dimensions: radius = 3.96875 mm, extrude distance = 139.7 mm
# Note: The design plan specifies a circle of radius 0.396875 for the profile ring,
# but the dimensions section gives radius = 3.96875. The dimensions section is the
# authoritative source for the actual part geometry. The ring radius 0.396875 appears
# to be a different measurement (possibly thread root radius) but the part is a simple
# disk/cylinder. We use the dimensions radius = 3.96875 mm.

# Create a circle profile and extrude it
result = (
    cq.Workplane("XY")
    .circle(3.96875)  # radius in mm
    .extrude(139.7)    # extrude distance in mm
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\108852_fed54702_0004\neg_03/generated.step")
