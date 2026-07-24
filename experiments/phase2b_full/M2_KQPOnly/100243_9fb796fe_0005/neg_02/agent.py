import cadquery as cq

# Create a rectangular profile in the UV plane
# From the design plan:
#   u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
#   rectangle corners in UV: (-58.2782, -12.0401) to (-56.3782, -13.9401)
#   This gives a 1.9 x 1.9 mm square (19 mm after cm->mm conversion? Actually the dimensions say 19.0 mm)
#   The UV coordinates are in cm originally, converted to mm by multiplying by 10.
#   So the rectangle in mm: center at (-573.782, -129.901) with size 19 x 19 mm.
#   But simpler: just create a 19x19 mm rectangle centered at origin in the XY plane, then extrude along Z.
#   The design plan's frame has w_dir = [0,1,0], so extrusion is along Y.
#   We'll create the rectangle in the XZ plane and extrude along Y to match the frame.

# Build the profile: 19 mm x 19 mm square centered at origin
width = 19.0
height = 19.0

# Create the rectangle in the XZ plane (since w_dir = Y)
result = (cq.Workplane("XZ")
          .rect(width, height)
          .extrude(200.0))  # extrude along Y (positive direction)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\100243_9fb796fe_0005\neg_02/generated.step")
