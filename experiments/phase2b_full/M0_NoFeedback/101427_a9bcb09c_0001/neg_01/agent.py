import cadquery as cq

# Create the outer rectangle profile
outer = cq.Workplane("XY").rect(1980.0, 600.0).extrude(25.0)

# Create the inner rectangle profile (the hole)
inner = cq.Workplane("XY").rect(1930.0, 550.0).extrude(25.0)

# Position the inner rectangle relative to outer: 
# Outer spans from x=-990 to x=990, y=-300 to y=300 (centered at origin)
# Inner should be offset so that its bottom-left corner is at (0,0) in UV space
# UV space: u from -2.5 to 195.5, v from -2.5 to 57.5
# Outer rect in UV: u from -2.5 to 195.5, v from -2.5 to 57.5
# Inner rect in UV: u from 0 to 193, v from 0 to 55
# Convert to XY: center at (0,0) with width 1980, height 600
# So UV (u,v) maps to XY (u - 96.5, v - 27.5) approximately
# Actually: outer rect width=1980, height=600, centered at origin
# So u_min=-2.5 maps to x=-990, u_max=195.5 maps to x=990 => scale factor = 1980/198 = 10
# v_min=-2.5 maps to y=-300, v_max=57.5 maps to y=300 => scale factor = 600/60 = 10
# So inner rect: u from 0 to 193, v from 0 to 55
# x = (u - 96.5) * 10 = (0 - 96.5)*10 = -965 to (193 - 96.5)*10 = 965
# y = (v - 27.5) * 10 = (0 - 27.5)*10 = -275 to (55 - 27.5)*10 = 275
# So inner rect width = 1930, height = 550, centered at origin

# Subtract inner from outer to create the frame
result = outer.cut(inner)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M0_NoFeedback\\101427_a9bcb09c_0001\\neg_01/generated.step")
