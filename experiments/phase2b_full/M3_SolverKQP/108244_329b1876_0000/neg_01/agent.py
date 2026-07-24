import cadquery as cq

# Design Plan: extruded rectangle (flat plate/panel)
# Dimensions: length_u = 1219.2 mm, width_v = 2590.8 mm, extrude_distance = 44.45 mm
# The profile is a rectangle in the UV plane, then extruded along +W direction.
# From the frame: u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# So the rectangle lies in the XZ plane (u=X, v=-Z), extruded along Y (w).
# The profile curves give start_uv and end_uv points. We'll center the rectangle at origin for simplicity.

# Build the rectangle profile on the XZ plane (u=X, v=-Z)
# The span in u is 1219.2 mm, in v is 2590.8 mm.
# We'll place it centered on the XZ plane, then extrude along Y.

length_u = 1219.2
width_v = 2590.8
extrude_dist = 44.45

# Create the rectangle in the XZ plane (u -> X, v -> -Z, so v direction is negative Z)
# We'll use a workplane on the XZ plane (which is Y=0 plane in CadQuery)
result = (cq.Workplane("XZ")
          .rect(length_u, width_v, centered=True)
          .extrude(extrude_dist))

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M3_SolverKQP\108244_329b1876_0000\neg_01/generated.step")
