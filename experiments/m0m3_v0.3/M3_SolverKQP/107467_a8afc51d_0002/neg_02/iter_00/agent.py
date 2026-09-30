import json
import math
from pathlib import Path
import cadquery as cq
from cadquery import exporters

# Constants from design plan
EXTENT_TOTAL_MM = 25.0
NORMAL = [0.0, 0.0, 1.0]
WORKPLANE = 'XY'
OUT_STEP = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\107467_a8afc51d_0002\neg_02\iter_00/generated.step"

# Design plan specifies radius = 3.0 mm (from dimensions section)
# The perturbed radius 0.375 is a scaling factor, not the actual radius
# The actual radius from design plan is 3.0 mm
RADIUS_MM = 3.0

def main():
    # Create a simple disk: circle extruded to 25mm
    # Using the design plan dimensions directly
    result = (
        cq.Workplane(WORKPLANE)
        .circle(RADIUS_MM)
        .extrude(EXTENT_TOTAL_MM)
    )
    
    exporters.export(result, OUT_STEP)

if __name__ == "__main__":
    main()