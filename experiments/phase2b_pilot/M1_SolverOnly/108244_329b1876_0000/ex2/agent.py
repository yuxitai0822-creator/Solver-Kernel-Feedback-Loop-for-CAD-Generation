import cadquery as cq
import os

# Dimensions from the design plan
length_u = 1219.2  # mm
width_v = 2590.8   # mm
extrude_w = 44.45  # mm

# Build the extruded rectangle
# The design plan specifies the local frame with u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# This means the rectangle lies in the XY plane (u=X, v=-Z) and extrudes along Y (w=Y).
# In CadQuery, we sketch on the XZ plane (u=X, v=Z) and extrude along Y.
# Since v_dir is [0,0,-1], the width_v spans along -Z. Sketching on the XZ plane with width_v
# naturally maps to the Z axis, and extruding along +Y matches the +w direction.

result = (cq.Workplane("XZ")
          .rect(length_u, width_v)
          .extrude(extrude_w))

# Ensure the output directory exists
out_dir = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M1_SolverOnly\108244_329b1876_0000\ex2"
os.makedirs(out_dir, exist_ok=True)

# Export to STEP
cq.exporters.export(result, os.path.join(out_dir, "generated.step"))
