import cadquery as cq

# Design Plan: extruded circle (disk)
# Dimensions:
#   radius = 4.7117 mm (from profile radius, note: the center_uv is in sketch plane)
#   extrude distance = 12.192 mm
# The profile center_uv is given as [50.800002, 63.500002] but that is in the sketch plane;
# we place the circle at the origin for simplicity (part-local frame).
# The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0).
# So the sketch plane is XY (u=x, v=z negative? Actually v_dir = (0,0,-1) means v points -Z,
# but for a circle we just use workplane XY and extrude in Y direction (w_dir).
# We'll create a workplane on XY, draw a circle radius 4.7117, then extrude in the Y direction by 12.192 mm.

radius = 4.7117
height = 12.192

result = (cq.Workplane("XY")
          .circle(radius)
          .extrude(height)
         )

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M3_SolverKQP\106817_bb28b7aa_0003\neg_01/generated.step")
