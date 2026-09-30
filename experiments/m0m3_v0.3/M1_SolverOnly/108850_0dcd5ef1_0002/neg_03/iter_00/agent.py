import cadquery as cq
from cadquery import exporters
import math

# Design Plan: MPPF_FrameBottom1 4x6 v1
# Extruded rectangle: 171.45 mm x 38.1 mm, extruded 6.35 mm
# The profile is defined in UV space where:
#   u_dir = [1.0, 0.0, 0.0] (X axis)
#   v_dir = [0.0, 0.0, -1.0] (negative Z axis)
#   w_dir = [0.0, 1.0, 0.0] (Y axis)
# The rectangle corners in UV: (0,0), (17.145,0), (17.145,3.81), (0,3.81)
# Note: The design plan dimensions are length_u=171.45, width_v=38.1
# The UV coordinates appear to be in cm (17.145 cm = 171.45 mm, 3.81 cm = 38.1 mm)
# So we multiply by 10 to convert to mm.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\108850_0dcd5ef1_0002\neg_03\iter_00\generated.step"

# Build the rectangle in the XZ plane (since v_dir is -Z, u_dir is X)
# The rectangle is 171.45 mm along X, 38.1 mm along Z (negative direction)
# We'll create it centered at origin for simplicity

# Create workplane on XZ plane
wp = cq.Workplane("XZ")

# Rectangle dimensions in mm
length_u = 171.45  # along X
width_v = 38.1     # along Z (but v_dir is -Z, so we use positive Z for the rect)

# Create the rectangle centered at origin
# The rectangle spans from -length_u/2 to +length_u/2 in X
# and from -width_v/2 to +width_v/2 in Z
result = wp.center(0, 0).rect(length_u, width_v).extrude(6.35)

# Export
importers = None
exporters.export(result, OUT_STEP_PATH)
