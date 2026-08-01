import cadquery as cq

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\104453_aba0f2d1_0006\neg_01\iter_01\generated.step"

# Design Plan: extruded rectangular frame
# Outer rectangle: 500mm x 300mm (from span_u=500, span_v=300)
# Inner rectangle: 400mm x 200mm (from inner_length_u=400, inner_width_v=200)
# Extrude distance: 500mm (from extrude_distance=500)

# Build the outer rectangle (500 x 300) and extrude 500mm
result = (cq.Workplane("XY")
          .rect(500, 300)
          .extrude(500))

# Cut the inner rectangle (400 x 200) to create the hollow frame
inner = (cq.Workplane("XY")
         .rect(400, 200)
         .extrude(500))

result = result.cut(inner)

# Export
cq.exporters.export(result, OUT_STEP_PATH)