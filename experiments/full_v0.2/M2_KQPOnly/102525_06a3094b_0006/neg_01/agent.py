import cadquery as cq

# Create a rectangular prism based on the design plan
# Dimensions: length_u = 11.3 mm, width_v = 21.0 mm, extrude_distance = 3.0 mm
# The profile is centered on the origin in the UV plane, then extruded in +W direction

# Create the rectangle profile centered at origin
# The profile coordinates from the plan show a rectangle from (-0.565, -1.05) to (0.565, 1.05) in UV space
# But the actual dimensions are length_u=11.3, width_v=21.0
# The UV coordinates appear to be half-dimensions: 11.3/2 = 5.65? No, 0.565*10 = 5.65, 1.05*10 = 10.5
# The plan notes unit_conversion_applied: cm_to_mm (x10), so the UV values are in cm and need scaling
# Actually, the dimensions are given as 11.3 and 21.0 mm, so we use those directly

# Create the rectangle profile centered at origin
result = (cq.Workplane("XY")
          .rect(11.3, 21.0, centered=True)
          .extrude(3.0))

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\102525_06a3094b_0006\neg_01/generated.step")