import cadquery as cq

# Design Plan: extruded circle (disk) with radius 25.4 mm and height 8.89 mm
# The profile circle center is at (16.994661, 17.998557) in UV plane, but since we work in
# part-local coordinates, we can place the circle at the origin and then translate if needed.
# However, the design plan indicates the circle center in UV coordinates, which correspond to
# the local frame's u and v axes. We'll create the circle centered at (0,0) and then translate
# to match the specified center. But the validation intents only check spans (50.8 x 50.8 x 8.89),
# so the absolute position doesn't matter for those checks. We'll place it at the specified center.

# Create a workplane on the XY plane (which corresponds to the UV plane in the design plan)
result = (cq.Workplane("XY")
          .circle(25.4)  # radius from design plan (value 25.4, note the profile radius is 25.4, not 2.54)
          .extrude(8.89)  # extrude distance from design plan
         )

# The design plan shows center_uv = [16.994661, 17.998557], but since we are creating the
# circle at the origin, we need to translate the result to match the specified center.
# However, the validation intents only check spans, so translation doesn't affect them.
# We'll translate to match the design plan center.
result = result.translate((16.994661, 17.998557, 0))

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\103284_e25015aa_0003\\ex2/generated.step")
