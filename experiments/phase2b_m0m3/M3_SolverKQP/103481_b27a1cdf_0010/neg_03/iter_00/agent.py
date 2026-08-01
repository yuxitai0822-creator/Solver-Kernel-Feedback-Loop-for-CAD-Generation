import cadquery as cq
import math
from pathlib import Path

OUT_STEP_PATH = Path(r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\103481_b27a1cdf_0010\neg_03\iter_00") / "generated.step"

# Design Plan: rectangular prism 101.6 x 101.6 x 38.1 mm, centered at origin
# The profile rectangle is defined in UV coordinates with corners at (±5.08, ±5.08) in cm,
# but after unit conversion (cm->mm) that becomes (±50.8, ±50.8) mm.
# However the perturbation description says the original half-length was 10.16 cm = 101.6 mm,
# and the perturbed half-length is 8.128 cm = 81.28 mm.  The design plan's profile coordinates
# are in cm (since unit_conversion_applied: cm_to_mm x10).  The original rectangle half-side
# was 5.08 cm = 50.8 mm, so full side = 101.6 mm.  The perturbation reduces the half-side
# to 4.064 cm = 40.64 mm, so full side = 81.28 mm.  But the design plan explicitly states
# length_u = 101.6 mm and width_v = 101.6 mm.  The perturbation description says
# "operator=E1_envelope; original=10.159999999999998; perturbed=8.127999999999998".
# That suggests the original half-side was 10.16 cm = 101.6 mm, perturbed half-side = 8.128 cm = 81.28 mm.
# However the design plan's profile coordinates are ±5.08 cm = ±50.8 mm, which is half of 101.6 mm.
# There is an inconsistency: the design plan says 101.6 mm, but the perturbation says 81.28 mm.
# We follow the design plan's explicit dimensions (101.6 x 101.6 x 38.1 mm) because the perturbation
# description is marked as TODO and not yet wired.  The script must produce a valid STEP file.

# Build the rectangle centered at origin, size 101.6 x 101.6 mm
result = (
    cq.Workplane("XY")
    .rect(101.6, 101.6, centered=True)
    .extrude(38.1)
)

cq.exporters.export(result, str(OUT_STEP_PATH))
