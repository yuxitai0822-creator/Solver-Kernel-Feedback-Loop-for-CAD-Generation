import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101269_f084ba14_0023\neg_03\iter_00\generated.step"

# Design Plan dimensions (in mm):
# Rectangle in UV frame: u from 0 to 95.25, v from 0 to 571.5 (original v=571.5, perturbed v=45.72?)
# The perturbation description says: original=57.15; perturbed=45.72
# But the design plan shows v span = 571.5 (which is 10x 57.15 due to cm->mm conversion).
# The perturbation likely applies to the v dimension: original v span = 571.5 mm, perturbed v span = 457.2 mm (since 45.72 cm = 457.2 mm).
# Let's use the perturbed value: v span = 457.2 mm
# Extrude distance = 19.05 mm along w direction (which is +Y in world frame)

# Frame: u_dir = [1,0,0] (X), v_dir = [0,0,-1] (-Z), w_dir = [0,1,0] (Y)
# So rectangle lies in XZ plane, extruded along Y

# Rectangle corners in UV: (0,0), (95.25,0), (95.25,457.2), (0,457.2)
# Map to world: u->X, v->-Z (since v_dir = [0,0,-1])
# So world points:
# (0, 0, 0), (95.25, 0, 0), (95.25, 0, -457.2), (0, 0, -457.2)

# Build on XY plane, then rotate? Or build directly on XZ plane.
# Cadquery Workplane("XZ") gives us XZ plane with Y as normal.
# On XZ plane: x = u, z = -v (since v_dir = [0,0,-1])

# Create the rectangle on XZ plane
result = (
    cq.Workplane("XZ")
    .moveTo(0, 0)
    .rect(95.25, 457.2, centered=False)
    .extrude(19.05)  # extrude along +Y (w direction)
)

# Export
exporters.export(result, OUT_STEP_PATH)
