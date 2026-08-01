import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded rectangular frame
# Outer rectangle: corners at (-1.88,10.88), (-1.88,15.12), (-6.12,15.12), (-6.12,10.88)
# Inner rectangle: corners at (-6.0,11.0), (-2.0,11.0), (-6.0,15.0), (-2.0,15.0)
# Extrude direction: -w (which is -x in the design plan frame)
# Extrude distance: 1120.0 mm
# The design plan frame has u_dir = [0,0,-1], v_dir = [0,1,0], w_dir = [1,0,0]
# So the profile is in the u-v plane (y-z plane in world), extrude along -w = -x

# Build the outer rectangle
outer = cq.Workplane("YZ").moveTo(-4.0, 13.0).rect(4.24, 4.24, centered=True)

# Build the inner rectangle (hole)
inner = cq.Workplane("YZ").moveTo(-4.0, 13.0).rect(4.0, 4.0, centered=True)

# Create the profile with the hole
profile = outer.cut(inner)

# Extrude along -x direction (which is -w in design plan frame)
# The profile is on YZ plane, extrude along X axis
result = profile.extrude(1120.0)

# Export
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101817_b02acd9f_0002\neg_01\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)