import cadquery as cq

# Create a cylinder (extruded circle) with radius 7.5 mm and height 20.0 mm
# The design plan specifies a disk (cylinder) with radius 7.5 and extrude distance 20.0
# The frame has u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# This means the extrusion is along +w = (0,1,0) direction
# The circle is in the uv-plane, so we create a circle on the XZ plane and extrude along Y

result = (
    cq.Workplane("XZ")
    .circle(7.5)
    .extrude(20.0)
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\104524_f829aab2_0001\neg_03/generated.step")
