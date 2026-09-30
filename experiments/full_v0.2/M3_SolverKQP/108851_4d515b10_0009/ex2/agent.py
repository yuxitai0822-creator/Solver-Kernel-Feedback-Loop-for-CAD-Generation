import cadquery as cq

# Create a rectangular plate based on the design plan
# Dimensions from the plan:
#   length_u = 209.55 mm (along x-axis)
#   width_v = 57.912 mm (along z-axis, since v_dir = [0,0,-1])
#   extrude_distance = 19.05 mm (along y-axis, since w_dir = [0,1,0])
# The profile rectangle is defined in UV space with:
#   u from 0 to 20.955 (note: this is 1/10 of 209.55, likely a scaling factor)
#   v from 0 to 5.7912 (1/10 of 57.912)
# The extrude distance is 19.05 mm
# The frame has u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
# So the rectangle lies in the XZ plane and extrudes along Y

# Create the rectangle in the XZ plane (normal = Y axis)
# Using the full dimensions: 209.55 mm along X, 57.912 mm along Z
result = (cq.Workplane("XZ")
          .rect(209.55, 57.912)
          .extrude(19.05))

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\108851_4d515b10_0009\\ex2/generated.step")
