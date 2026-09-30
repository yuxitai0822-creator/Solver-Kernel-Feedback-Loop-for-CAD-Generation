import cadquery as cq
import os

# Dimensions from design plan (unit conversion cm_to_mm applied)
length_u = 12.0  # span along u
width_v = 60.0   # span along v
extrude_w = 40.0 # span along w

# Build the rectangular prism
# The frame has u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# This means the rectangle is drawn on the XZ plane (u=X, v=-Z)
# and extruded along the Y axis (w=Y) by 40mm.
# Using centered=True ensures the extrusion spans from Y=0 to Y=40.
result = (
    cq.Workplane("XZ")
    .rect(length_u, width_v)
    .extrude(extrude_w)
)

# Ensure output directory exists
out_dir = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M2_KQPOnly\105278_909f3813_0000\ex2"
os.makedirs(out_dir, exist_ok=True)

# Export to STEP
out_step_path = os.path.join(out_dir, "generated.step")
cq.exporters.export(result, out_step_path)
