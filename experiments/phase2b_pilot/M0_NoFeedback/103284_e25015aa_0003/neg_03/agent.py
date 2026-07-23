import cadquery as cq

# Build an extruded circle (disk) based on the design plan
# Circle radius: 2.54 mm (from profile curves), center offset: (1.699, 1.800)
# Extrude distance: 8.89 mm along +Z

result = (
    cq.Workplane("XY")
    .center(1.6994660913961006, 1.7998556732836484)
    .circle(2.54)
    .extrude(8.89)
)

# Export the result to STEP file
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M0_NoFeedback\103284_e25015aa_0003\neg_03/generated.step"
cq.exporters.export(result, OUT_STEP_PATH)
