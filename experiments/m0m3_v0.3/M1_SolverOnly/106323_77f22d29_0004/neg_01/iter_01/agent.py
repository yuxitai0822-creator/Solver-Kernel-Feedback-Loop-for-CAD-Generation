import cadquery as cq

# Design Plan: bearing 2 v1
# Extruded annulus: outer radius 17.5 mm, inner radius 12.5 mm, total height 10.0 mm
# Perturbation: OneSide extent (extrude in +Z direction only)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M1_SolverOnly\106323_77f22d29_0004\neg_01\iter_01\generated.step"

# Build the annulus using a single Workplane with a circle and then a hole
result = (cq.Workplane("XY")
          .circle(17.5)          # outer circle
          .circle(12.5)          # inner circle (hole)
          .extrude(10.0)         # extrude in +Z direction only (OneSide)
         )

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
