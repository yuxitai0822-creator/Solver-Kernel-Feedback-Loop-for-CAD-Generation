import cadquery as cq

# Create a rectangular prism based on the design plan
# Dimensions: length_u = 3.9 mm, width_v = 4.9 mm, extrude_distance = 1.55 mm
# The profile is centered at origin in the uv-plane, then extruded in +w direction

# Create the rectangle profile centered at origin
# From the curves, the rectangle spans from -0.195 to 0.195 in u and -0.245 to 0.245 in v
# This gives total length_u = 0.39 (but expected 3.9) and width_v = 0.49 (but expected 4.9)
# The design plan notes unit_conversion_applied: cm_to_mm (x10), so the uv values are in cm
# Converting: 0.195 cm = 1.95 mm, 0.245 cm = 2.45 mm
# So the rectangle spans from -1.95 to 1.95 in u (total 3.9 mm) and -2.45 to 2.45 in v (total 4.9 mm)

# Build the rectangle using the converted dimensions
result = (cq.Workplane("XY")
          .center(0, 0)
          .rect(3.9, 4.9)
          .extrude(1.55))

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\102525_06a3094b_0000\ex2/generated.step")