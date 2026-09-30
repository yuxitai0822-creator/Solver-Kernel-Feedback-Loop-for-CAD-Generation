import cadquery as cq
import os

OUT_DIR = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-SolverKQP\102410_f9877a7b_0012\neg_02"
OUT_STEP_PATH = os.path.join(OUT_DIR, "generated.step")

# Ensure the output directory exists
os.makedirs(OUT_DIR, exist_ok=True)

# Parameters from the design plan
outer_radius = 6.0
inner_radius = 4.25
extrude_distance = 12.0

# Build the extruded annulus (bearing ring)
# The design plan specifies an annulus extruded along +w (which corresponds to +Y in CadQuery's default XZ plane)
result = (
    cq.Workplane("XZ")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(extrude_distance)
)

# Export the result to STEP format
cq.exporters.export(result, OUT_STEP_PATH)
