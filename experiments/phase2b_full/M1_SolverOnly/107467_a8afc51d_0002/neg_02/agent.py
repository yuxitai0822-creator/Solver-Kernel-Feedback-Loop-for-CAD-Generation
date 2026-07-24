import cadquery as cq

# Create a cylinder (extruded circle) with radius 3.0 mm and height 25.0 mm
# The design plan specifies a disk-like part: a circle of radius 3.0 extruded by 25.0 mm
# Note: The profile radius in the plan is 0.3 (from curves) but the dimensions section says radius 3.0.
# The dimensions section is authoritative for explicit dimensions, so we use radius = 3.0 mm.

# Create the cylinder by extruding a circle
result = cq.Workplane("XY").circle(3.0).extrude(25.0)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\107467_a8afc51d_0002\neg_02/generated.step")
