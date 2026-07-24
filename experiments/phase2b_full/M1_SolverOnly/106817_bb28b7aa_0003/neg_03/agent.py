import cadquery as cq

# Design Plan: extruded circle (disk)
# Dimensions:
#   radius = 4.7117 mm (from profile radius, note: the design plan shows radius 0.47117 but that is in cm? 
#   The compiler notes say unit_conversion_applied: cm_to_mm (x10). So radius = 0.47117 cm * 10 = 4.7117 mm.
#   center_uv = [50.800002, 63.500002] but that is in the local frame; we place the circle at origin for simplicity.
#   extrude distance = 12.192 mm
#   direction: +w (which is along y-axis in our coordinate system: w_dir = [0,1,0])

# Build the disk: a circle extruded along the y-axis.
result = (
    cq.Workplane("XY")
    .circle(4.7117)  # radius in mm
    .extrude(12.192)  # extrude along Z (default), but we need along Y? 
    # The design plan frame: u_dir = [1,0,0], v_dir = [0,0,-1], w_dir = [0,1,0]
    # So w is Y. We'll extrude along Y by using workplane on XZ.
)

# Actually, to extrude along Y, we should work on XZ plane.
result = (
    cq.Workplane("XZ")
    .circle(4.7117)
    .extrude(12.192)
)

# Export
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M1_SolverOnly\106817_bb28b7aa_0003\neg_03/generated.step")
