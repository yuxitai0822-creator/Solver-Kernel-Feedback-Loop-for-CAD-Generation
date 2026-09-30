import cadquery as cq
from cadquery import exporters
import math

# Design Plan: Drone Leg - square strut
# Extruded rectangle: 19.0 x 19.0 mm profile, extruded 130.0 mm
# The profile is defined in UV space with frame:
#   u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# The rectangle corners in UV are:
#   (-58.2782, -12.0401) to (-56.3782, -13.9401)
# This gives width_u = 1.9, width_v = 1.9 (in cm -> 19 mm after conversion)
# Extrude distance = 130.0 mm

# Build the rectangle on the XZ plane (since v_dir is [0,0,-1] and w_dir is [0,1,0])
# The UV coordinates are in cm, convert to mm by multiplying by 10
# But the design plan says unit is mm, and the coordinates are already in mm
# Let's verify: width_u = 19.0 mm, width_v = 19.0 mm
# The UV coordinates span: u from -58.2782 to -56.3782 = 1.9 (in original units)
# v from -13.9401 to -12.0401 = 1.9 (in original units)
# These are in cm originally, converted to mm by multiplying by 10 -> 19 mm
# So the coordinates in the plan are already in mm (after conversion)

# Create workplane on XZ plane (since v_dir is [0,0,-1], the sketch plane is XZ)
# Actually, with u_dir=[1,0,0], v_dir=[0,0,-1], the sketch plane normal is u x v = [0,1,0] = w_dir
# So the sketch is on the XZ plane

result = (
    cq.Workplane("XZ")
    .center(-57.32820137826746, -12.99014576968157)  # center of rectangle
    .rect(19.0, 19.0)  # width=19mm, height=19mm
    .extrude(130.0)  # extrude along Y (w_dir = [0,1,0])
)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\100243_9fb796fe_0006\neg_01\iter_00\generated.step"
exporters.export(result, OUT_STEP_PATH)