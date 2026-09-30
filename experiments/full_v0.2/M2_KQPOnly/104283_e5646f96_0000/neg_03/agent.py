import cadquery as cq

# Design Plan: extruded circle (disk/shaft)
# Profile: circle with radius 12.5 mm, center at (-15.0, 10.0) in UV plane
# Extrude: 75.0 mm along +w direction (which maps to world X axis per frame)
# Frame: u_dir = (0,0,-1), v_dir = (0,1,0), w_dir = (1,0,0)
# So in CadQuery: workplane on XY, then circle center at (-15, 10), extrude along X

result = (
    cq.Workplane("XY")
    .center(-15.0, 10.0)
    .circle(12.5)
    .extrude(75.0)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M2_KQPOnly\\104283_e5646f96_0000\\neg_03/generated.step")
