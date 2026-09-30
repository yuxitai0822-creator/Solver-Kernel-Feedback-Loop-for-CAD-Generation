import cadquery as cq
import os

# Dimensions from design plan (unit conversion cm_to_mm already applied)
length_u = 279.4   # mm
width_v = 215.9    # mm
extrude_w = 1.5875 # mm

# Build the extruded rectangle (flat plate/panel)
result = (cq.Workplane("XY")
          .rect(length_u, width_v)
          .extrude(extrude_w))

# Ensure output directory exists
out_dir = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M2_KQPOnly\100877_ac1e5a17_0001\ex2"
os.makedirs(out_dir, exist_ok=True)

# Export to STEP
out_step_path = os.path.join(out_dir, "generated.step")
cq.exporters.export(result, out_step_path)
