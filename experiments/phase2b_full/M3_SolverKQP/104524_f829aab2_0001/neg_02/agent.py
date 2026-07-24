import cadquery as cq

# Create a cylinder (extruded circle) with radius 7.5 mm and height 20.0 mm
# The design plan specifies a disk (cylinder) with radius 7.5 and extrude distance 20.0
# The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means the circle is in the uv-plane (x and z axes) and extrudes along w (y axis)
# We'll create the circle on the XY plane and extrude along Z, then rotate to match frame

# Step 1: Create a circle on the XY plane centered at origin with radius 7.5
result = cq.Workplane("XY").circle(7.5).extrude(20.0)

# The resulting cylinder has its axis along Z, but the design plan frame has w_dir = (0,1,0)
# So we need to rotate the cylinder so its axis aligns with Y (w_dir)
# Rotate -90 degrees around X axis to go from Z to Y
result = result.rotate((0,0,0), (1,0,0), -90)

# Export the result
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\104524_f829aab2_0001\\neg_02/generated.step")
