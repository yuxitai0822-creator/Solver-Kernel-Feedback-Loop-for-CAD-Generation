import cadquery as cq
import os

# Ensure the output directory exists
out_dir = r'D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M3_SolverKQP\102525_06a3094b_0004\ex2'
os.makedirs(out_dir, exist_ok=True)

out_step_path = os.path.join(out_dir, 'generated.step')

# Build the rectangular prism
# Dimensions: length_u = 8.5mm, width_v = 18.0mm, extrude_distance = 2.5mm
# The frame maps u->X, v->-Z, w->Y. Extrusion is +w (i.e., +Y).
# Origin is at the bbox_min_corner.
# To achieve this in CadQuery, we sketch on the XZ plane (Y=0), 
# with X mapping to u and -Z mapping to v, then extrude +Y.

result = (
    cq.Workplane("XZ")
    .rect(8.5, 18.0)
    .extrude(2.5)
)

# Export the result to STEP
cq.exporters.export(result, out_step_path)
