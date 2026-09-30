import cadquery as cq
from cadquery import exporters

# Design Plan: extruded rectangle
# Dimensions: length_u = 193.0 mm, width_v = 55.0 mm, extrude_distance = 50.0 mm
# Frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# The rectangle is defined in UV space with corners at (0,0), (193,0), (193,55), (0,55)
# Extrude in +w direction (which is +Y in world coordinates)

# Create a workplane on the XZ plane (since v_dir is [0,0,-1], the sketch plane is XZ)
# The rectangle in UV space: u along X, v along Z (negative direction)
# To match the frame: u_dir = X, v_dir = -Z, so the sketch plane is XZ
# The rectangle corners: (0,0) -> (193,0) -> (193,55) -> (0,55) in UV
# In world coordinates: u->X, v->-Z, so:
# (0,0) -> (0, 0, 0)
# (193,0) -> (193, 0, 0)
# (193,55) -> (193, 0, -55)
# (0,55) -> (0, 0, -55)

# Create the rectangle on XZ plane
result = (cq.Workplane("XZ")
          .moveTo(0, 0)
          .lineTo(193, 0)
          .lineTo(193, -55)
          .lineTo(0, -55)
          .close()
          .extrude(50.0))  # extrude in +Y direction (w_dir = [0,1,0])

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M0_NoFeedback\101427_a9bcb09c_0002\neg_01\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)