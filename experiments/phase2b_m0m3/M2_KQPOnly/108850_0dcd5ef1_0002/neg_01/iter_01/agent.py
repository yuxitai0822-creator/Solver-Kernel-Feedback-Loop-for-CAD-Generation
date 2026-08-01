import cadquery as cq

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\108850_0dcd5ef1_0002\neg_01\iter_01\generated.step"

# Design Plan: extruded rectangle 171.45 mm x 38.1 mm, extrude depth 6.35 mm (original 0.635 cm -> 6.35 mm)
# Perturbation description says operator=E2_extrude_depth; original=0.635; perturbed=0.9525
# However, the design plan explicitly states extrude distance = 6.35 mm (value: 6.35, tol: 0.01)
# The perturbation is a negative CAD code that should be applied, but the design plan is the ground truth.
# Since the design plan is the authoritative source, we use 6.35 mm.

# Build rectangle on XZ plane, centered at origin, then extrude along Y (normal of XZ)
result = cq.Workplane("XZ").center(171.45/2, 38.1/2).rect(171.45, 38.1).extrude(6.35)

# Export STEP
cq.exporters.export(result, OUT_STEP_PATH)