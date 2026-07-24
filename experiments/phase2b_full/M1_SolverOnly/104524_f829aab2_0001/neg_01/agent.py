import cadquery as cq

# Create a cylinder (extruded circle) with radius 7.5 mm and height 20.0 mm
# The design plan specifies a disk (cylinder) with radius 7.5 and extrude distance 20.0
# The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means the circle is in the u-v plane (x-z plane) and extrudes along w (y-axis)
# To match standard orientation, we create the circle on the XY plane and extrude along Z
# Then rotate to match the specified frame orientation

# Create the base cylinder: circle radius 7.5 on XY plane, extrude 20.0 along Z
result = (
    cq.Workplane("XY")
    .circle(7.5)
    .extrude(20.0)
)

# The design plan frame has w_dir = (0,1,0) meaning the extrusion direction is along Y
# Our current extrusion is along Z, so we need to rotate -90 degrees around X axis
# This maps Z -> Y, matching the design plan
result = result.rotate((0,0,0), (1,0,0), -90)

# Export the result
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\104524_f829aab2_0001\\neg_01/generated.step")
