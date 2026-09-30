import cadquery as cq

# Build a rectangular flat plate/panel
# Dimensions: 171.45 mm (u) x 38.1 mm (v) x 6.35 mm (w/extrusion)
# The design plan specifies the profile in the UV plane with u_dir=[1,0,0] and v_dir=[0,0,-1],
# extruded along w_dir=[0,1,0] for 6.35 mm.
# In CadQuery's default XY plane, X aligns with u_dir and Y aligns with -v_dir.
# Thus, the rectangle is drawn with length 171.45 (X) and width 38.1 (Y),
# and extruded 6.35 mm along the Z axis.

result = (
    cq.Workplane("XY")
    .rect(171.45, 38.1)
    .extrude(6.35)
)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M2_KQPOnly\108850_0dcd5ef1_0002\ex2/generated.step"
cq.exporters.export(result, OUT_STEP_PATH)