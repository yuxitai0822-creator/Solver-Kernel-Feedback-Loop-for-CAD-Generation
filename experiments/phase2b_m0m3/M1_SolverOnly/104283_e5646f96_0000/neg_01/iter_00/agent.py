import cadquery as cq
from cadquery import exporters
import math

# Design Plan: SHAFT[ v1
# Extruded circle (disk) with radius 12.5 mm, extrude distance 75.0 mm
# Frame: u_dir=[0,0,-1], v_dir=[0,1,0], w_dir=[1,0,0]
# Circle center in UV: (-15.0, 10.0) -> but in the frame, this is a local coordinate
# The frame indicates the sketch plane is YZ (since w_dir is X axis)
# So we work on YZ plane, center at (-15.0, 10.0) in YZ coordinates

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\104283_e5646f96_0000\neg_01\iter_00\generated.step"

# Build on YZ plane (since w_dir = [1,0,0] means extrusion along X)
# The circle center in UV coordinates is (-15.0, 10.0)
# In YZ plane: U corresponds to -Z? Actually u_dir=[0,0,-1], v_dir=[0,1,0]
# So U axis = -Z, V axis = Y
# Center in YZ: Y = v_coord = 10.0, Z = -u_coord = -(-15.0) = 15.0
# But simpler: just use the UV coordinates directly on a workplane

# Create workplane on YZ
wp = cq.Workplane("YZ")

# Move to center and create circle with radius 12.5 mm
# The center in UV is (-15.0, 10.0). In YZ plane, we use (y, z) = (10.0, 15.0)
# because u_dir = [0,0,-1] means u maps to -z, so u=-15 gives z=15
result = wp.moveTo(10.0, 15.0).circle(12.5).extrude(75.0)

# Export
exporters.export(result, OUT_STEP_PATH)
