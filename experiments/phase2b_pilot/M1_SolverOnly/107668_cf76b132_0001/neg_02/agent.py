import cadquery as cq

# Build the extruded annulus (bearing/wheel)
# Outer radius: 132.5 mm, Inner radius: 75.0 mm, Extrude distance: 100.0 mm
# The design plan specifies the extrusion direction along +w (which maps to +X in the part local frame)
# CadQuery extrudes along +Z by default, so we build the annulus on the XY plane and then rotate it
# to align the extrusion axis with +X.

annulus = (
    cq.Workplane("XY")
    .circle(132.5)
    .circle(75.0)
    .extrude(100.0)
)

# Rotate the part so that the extrusion direction (+Z) aligns with the +X axis (+w in the design plan)
# Rotation of 90 degrees around the Y axis maps +Z to +X
result = annulus.rotate((0, 0, 0), (0, 1, 0), 90)

# Export the result to STEP format
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M1_SolverOnly\107668_cf76b132_0001\neg_02/generated.step"
cq.exporters.export(result, OUT_STEP_PATH)
