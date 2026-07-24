import cadquery as cq

# Design Plan: extruded rectangular frame (hollow box)
# Outer dimensions: 40 x 40 mm (u x v), extrude 520 mm along w
# Wall thickness: (40 - 37.6)/2 = 1.2 mm

# Create the outer rectangle profile on the XY plane (u=x, v=y, w=z)
# The profile is centered at origin for convenience, then extruded

# Outer rectangle: 40 x 40 mm
outer = cq.Workplane("XY").rect(40, 40)

# Inner rectangle: 37.6 x 37.6 mm (centered, so offset by 1.2 mm from each edge)
inner = cq.Workplane("XY").rect(37.6, 37.6)

# Create the frame profile by subtracting inner from outer
# We'll build the profile as a single wire
frame_profile = outer.union(inner).wires().toPending()

# Actually, simpler approach: create the outer rectangle, then cut the inner
# Using CadQuery's approach: create a rectangle, then subtract a smaller rectangle

result = (
    cq.Workplane("XY")
    .rect(40, 40)  # outer profile
    .extrude(520.0)  # extrude along +Z (w direction)
    .faces(">Z")  # select top face
    .workplane()  # create workplane on top face
    .rect(37.6, 37.6)  # inner profile on top
    .cutThruAll()  # cut through the entire body
)

# Export to STEP
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M2_KQPOnly\101817_b02acd9f_0001\neg_03/generated.step")
