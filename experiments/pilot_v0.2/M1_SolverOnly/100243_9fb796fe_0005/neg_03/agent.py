import cadquery as cq
import os

# Ensure output directory exists
OUT_DIR = r'D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M1_SolverOnly\100243_9fb796fe_0005\neg_03'
OUT_STEP_PATH = os.path.join(OUT_DIR, 'generated.step')
os.makedirs(OUT_DIR, exist_ok=True)

# Build the square strut based on the design plan
# The profile is a 19x19 mm rectangle, extruded 200 mm along the +Y axis.
# The rectangle is centered at the origin for simplicity, which satisfies the span constraints.
result = (cq.Workplane("XZ")
          .rect(19.0, 19.0)
          .extrude(200.0))

# Export the result to STEP format
cq.exporters.export(result, OUT_STEP_PATH)