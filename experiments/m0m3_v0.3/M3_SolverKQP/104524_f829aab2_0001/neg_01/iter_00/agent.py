import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\104524_f829aab2_0001\neg_01\iter_00/generated.step"

# Design Plan: extruded circle (disk)
# - Circle radius: 7.5 mm (from profiles[0].radius)
# - Extrude distance: 20.0 mm (from extrude.distance_total.value)
# - Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
#   This means the sketch plane is XZ (u=x, v=-z), extrude along +w = +y

# Build on XY plane, then rotate to match frame orientation
# Frame: u=x, v=-z, w=y
# So sketch on XZ plane (x horizontal, z vertical), extrude along y

# Create workplane on XZ
wp = cq.Workplane("XZ")

# Draw circle at origin with radius 7.5
wp = wp.center(0, 0).circle(7.5)

# Extrude along +w = +y direction by 20.0 mm
result = wp.extrude(20.0)

# Export
importers.export(result, OUT_STEP_PATH)
