import cadquery as cq
import os

# Ensure output directory exists
OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M3_SolverKQP\100243_9fb796fe_0005\neg_03"
OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")
os.makedirs(OUT_DIR, exist_ok=True)

# Design Plan: extruded_rectangle (square_strut)
# Frame: u=(1,0,0), v=(0,0,-1), w=(0,1,0)
# Profile rectangle in uv-plane: u_span=19.0, v_span=19.0
# Extrude along +w direction (Y axis) by 200.0 mm

# Rectangle corners in uv-plane:
# (-58.2782, -12.0401) to (-56.3782, -13.9401)
# u_span = 1.9, v_span = 1.9 (in cm, converted to mm -> 19.0, 19.0)

# Map uv to XYZ: X=u, Z=-v, Y=0 (sketch plane)
# Corner mapping:
# (-58.2782, -12.0401) -> X=-58.2782, Z=12.0401
# (-58.2782, -13.9401) -> X=-58.2782, Z=13.9401
# (-56.3782, -13.9401) -> X=-56.3782, Z=13.9401
# (-56.3782, -12.0401) -> X=-56.3782, Z=12.0401

# Build the rectangle on the XZ plane (Y=0) and extrude along +Y
result = (
    cq.Workplane("XZ")
    .rect(19.0, 19.0)
    .center(-57.3282, 12.9901)  # center of rectangle in XZ
    .rect(19.0, 19.0)
    .extrude(200.0)
)

# Export to STEP
cq.exporters.export(result, OUT_STEP_PATH)
