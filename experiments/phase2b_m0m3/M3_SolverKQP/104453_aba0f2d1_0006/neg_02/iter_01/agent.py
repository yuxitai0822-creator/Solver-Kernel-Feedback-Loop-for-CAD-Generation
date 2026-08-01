import cadquery as cq
from cadquery import exporters

# Constants from design plan
OUTER_LENGTH = 500.0  # mm (u direction)
OUTER_WIDTH = 300.0   # mm (v direction)
INNER_LENGTH = 400.0  # mm (u direction)
INNER_WIDTH = 200.0   # mm (v direction)
EXTRUDE_DISTANCE = 500.0  # mm (w direction)

# Build the rectangular frame profile
# Outer rectangle: 500 x 300 mm
# Inner rectangle: 400 x 200 mm, offset 50 mm from edges
# (outer - inner)/2 = (500-400)/2 = 50 in u, (300-200)/2 = 50 in v

# Create workplane on XY plane
wp = cq.Workplane("XY")

# Draw outer rectangle centered at origin
# Outer: width=500 (x), height=300 (y)
outer = wp.moveTo(0, 0).rect(OUTER_LENGTH, OUTER_WIDTH, centered=True)

# Draw inner rectangle (cutout) centered at origin
# Inner: width=400 (x), height=200 (y)
inner = wp.moveTo(0, 0).rect(INNER_LENGTH, INNER_WIDTH, centered=True)

# Create the frame by extruding outer and subtracting inner
# First extrude the outer rectangle
frame = outer.extrude(EXTRUDE_DISTANCE)

# Create the inner cutting prism
cut_prism = inner.extrude(EXTRUDE_DISTANCE)

# Subtract inner from outer to create hollow frame
result = frame.cut(cut_prism)

# Export to STEP
OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\104453_aba0f2d1_0006\neg_02\iter_01/generated.step"
exporters.export(result, OUT_STEP_PATH)