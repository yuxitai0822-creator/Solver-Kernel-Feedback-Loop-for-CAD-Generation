import cadquery as cq

# Create a rectangular plate with dimensions from the design plan
# The profile is a rectangle with length_u = 209.55 mm and width_v = 57.912 mm
# The extrusion distance is 19.05 mm in the +w direction

# Create the rectangle profile on the XY plane (u=x, v=z, w=y)
# The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# This means: u -> x, v -> -z, w -> y
# The rectangle spans from (0, 0) to (209.55, 57.912) in uv coordinates
# But v_dir is [0,0,-1], so v coordinate maps to -z
# To get positive z extent, we need to negate the v coordinate

# Start with a workplane on the XY plane
result = (cq.Workplane("XY")
          # Create a rectangle centered at origin with dimensions 209.55 x 57.912
          # The rectangle in uv space goes from (0,0) to (209.55, 57.912)
          # We'll center it at (209.55/2, 57.912/2) to match the origin convention
          .rect(209.55, 57.912, centered=True)
          # Extrude in the +w direction (which is +y) by 19.05 mm
          .extrude(19.05)
         )

# Export the result
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\108851_4d515b10_0009\\ex2/generated.step")
