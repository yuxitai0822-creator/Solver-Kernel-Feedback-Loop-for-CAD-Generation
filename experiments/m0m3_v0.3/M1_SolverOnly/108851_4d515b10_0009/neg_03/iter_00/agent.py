import cadquery as cq
from cadquery import exporters
import math

# Design Plan: SoapCutterLeg1 v1
# Extruded rectangle: 209.55 x 57.912 x 19.05 mm
# Frame: u=[1,0,0], v=[0,0,-1], w=[0,1,0]
# Rectangle in uv-plane: u from 0 to 209.55, v from 0 to 57.912
# Extrude along +w (y-axis) by 19.05 mm

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\108851_4d515b10_0009\neg_03\iter_00/generated.step"

# Build the rectangle in the XZ plane (since v_dir = [0,0,-1] means v is along -z, u along x)
# The rectangle corners in uv: (0,0), (209.55,0), (209.55,57.912), (0,57.912)
# In world: u->x, v-> -z, so point (u,v) -> (u, 0, -v)
# But we can just use Workplane("XZ") and draw rectangle centered at (104.775, -28.956)
# with width=209.55, height=57.912, then extrude along y (positive w direction)

wp = cq.Workplane("XZ")

# Rectangle centered at (104.775, -28.956) with size (209.55, 57.912)
# The rectangle spans u:0..209.55, v:0..57.912, so center in uv is (104.775, 28.956)
# In XZ plane: x = u, z = -v, so center is (104.775, -28.956)
result = wp.moveTo(104.775, -28.956).rect(209.55, 57.912, centered=True).extrude(19.05)

exporters.export(result, OUT_STEP_PATH)
