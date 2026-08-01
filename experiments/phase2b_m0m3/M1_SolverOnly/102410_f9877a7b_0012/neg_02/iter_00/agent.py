import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded annulus (bearing)
# Outer radius = 6.0 mm, Inner radius = 4.25 mm, Extrude distance = 12.0 mm
# The previous script used perturbed radius 7.5 mm (outer) which is wrong.
# We must use the design plan dimensions.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\102410_f9877a7b_0012\neg_02\iter_00/generated.step"

# Build the annulus on the XZ plane (as per previous script's WORKPLANE = 'XZ')
# The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# So sketch plane is XZ, extrude direction is +Y (w_dir)

result = (
    cq.Workplane("XZ")
    .circle(6.0)  # outer radius = 6.0 mm (from design plan)
    .circle(4.25)  # inner radius = 4.25 mm (from design plan)
    .extrude(12.0)  # extrude distance = 12.0 mm (from design plan)
)

# Export to STEP
importers = None  # not needed
exporters.export(result, OUT_STEP_PATH)
