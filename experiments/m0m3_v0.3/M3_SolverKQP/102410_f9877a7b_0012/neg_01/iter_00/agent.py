import cadquery as cq
from cadquery import exporters
import math

# Design Plan: extruded annulus (bearing)
# Outer radius = 6.0 mm, Inner radius = 4.25 mm, Extrude distance = 12.0 mm
# The perturbation description says perturbed=1.8000000000000003 (cm) = 18 mm
# But the design plan explicitly states extrude_distance = 12.0 mm with tol 0.01
# We follow the design plan dimensions exactly.

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102410_f9877a7b_0012\neg_01\iter_00/generated.step"

# Create workplane on XZ plane (as per previous script's WORKPLANE = 'XZ')
# But the design plan frame has u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# This means the profile is in the XZ plane (u,v) and extrude is along Y (w)
# So we use XY plane and then rotate, or use XZ directly.
# Using XZ plane directly matches the frame: u=X, v=Z, extrude along Y

# Build the annulus profile
wp = cq.Workplane("XZ")

# Outer circle
wp = wp.moveTo(0, 0).circle(6.0)

# Inner circle (cut)
wp = wp.circle(4.25)

# Extrude along Y (positive w direction) by 12.0 mm
result = wp.extrude(12.0)

# Export
importers.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")
