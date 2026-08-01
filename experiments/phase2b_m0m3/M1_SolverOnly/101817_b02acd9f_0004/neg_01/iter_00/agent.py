import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded rectangle
# Dimensions: length_u=1200.0 mm, width_v=600.0 mm, extrude_distance=20.0 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile rectangle corners in UV space:
#   (127.82976131535646, -66.34402294937294) -> (7.829761315356478, -66.34402294937294)
#   (127.82976131535646, -6.344022949372942) -> (127.82976131535646, -66.34402294937294)
#   (7.829761315356478, -6.344022949372942) -> (127.82976131535646, -6.344022949372942)
#   (7.829761315356478, -66.34402294937294) -> (7.829761315356478, -6.344022949372942)
# The rectangle spans 120.0 in u and 60.0 in v (since 127.83-7.83=120.0, -6.34-(-66.34)=60.0)
# Extrude along +w (y-axis) by 20.0 mm

# Build the rectangle in the XZ plane (since v_dir is [0,0,-1], u_dir is [1,0,0], w_dir is [0,1,0])
# The rectangle center in UV: u_center = (127.82976131535646 + 7.829761315356478)/2 = 67.82976131535647
# v_center = (-66.34402294937294 + -6.344022949372942)/2 = -36.34402294937294
# width_u = 120.0, height_v = 60.0

result = (
    cq.Workplane("XZ")
    .center(67.82976131535647, -36.34402294937294)
    .rect(120.0, 60.0)
    .extrude(20.0)
)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\101817_b02acd9f_0004\neg_01\iter_00/generated.step"
exporters.export(result, OUT_STEP_PATH)