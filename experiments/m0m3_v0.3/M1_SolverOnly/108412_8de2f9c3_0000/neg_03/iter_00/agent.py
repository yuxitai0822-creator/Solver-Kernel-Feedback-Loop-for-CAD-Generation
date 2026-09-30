import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\108412_8de2f9c3_0000\neg_03\iter_00/generated.step"

# Design Plan dimensions (in mm, after cm->mm conversion)
# Rectangle: length_u = 2438.4 mm, width_v = 1219.2 mm
# Extrude: distance_total = 12.7 mm
# The profile coordinates in the design plan are given in UV space:
#   start_uv = (121.92, -60.96) ... but these are in cm? 
#   Actually the design plan says unit_conversion_applied: cm_to_mm (x10)
#   So the original values were in cm, and we multiply by 10 to get mm.
#   The profile coordinates: 121.92 cm = 1219.2 mm, 60.96 cm = 609.6 mm
#   But the rectangle dimensions: length_u = 2438.4 mm, width_v = 1219.2 mm
#   So the half-lengths are 1219.2 mm and 609.6 mm respectively.
#   The profile coordinates in UV space: 
#     (121.92, -60.96) -> (1219.2, -609.6) in mm
#     (121.92, 60.96)  -> (1219.2, 609.6)
#     (-121.92, 60.96) -> (-1219.2, 609.6)
#     (-121.92, -60.96)-> (-1219.2, -609.6)
#   This gives a rectangle of width 2438.4 mm and height 1219.2 mm, matching.

# Build the rectangle centered at origin
result = (
    cq.Workplane("XY")
    .center(0, 0)
    .rect(2438.4, 1219.2, centered=True)
    .extrude(12.7)
)

exporters.export(result, OUT_STEP_PATH)
