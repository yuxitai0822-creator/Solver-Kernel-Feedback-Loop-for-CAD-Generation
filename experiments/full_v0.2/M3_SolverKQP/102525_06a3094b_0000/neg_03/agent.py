import cadquery as cq

# Create a rectangular prism with dimensions:
# Length (u): 3.9 mm, Width (v): 4.9 mm, Height (w): 1.55 mm
# The profile is centered at the origin in the XY plane, extruded in +Z direction.

# Define the rectangle dimensions
length_u = 3.9  # along X
width_v = 4.9   # along Y (since v_dir is [0,0,-1], but we use standard orientation)
extrude_height = 1.55  # along Z

# Create the rectangle profile centered at origin
result = (
    cq.Workplane("XY")
    .rect(length_u, width_v)
    .extrude(extrude_height)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\102525_06a3094b_0000\\neg_03/generated.step")
