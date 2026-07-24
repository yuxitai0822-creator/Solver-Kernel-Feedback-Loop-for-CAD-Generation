import cadquery as cq

# Design Plan: extruded rectangular frame (hollow box)
# Outer rectangle: 42.4 x 42.4 mm (from u/v spans)
# Inner rectangle: 40.0 x 40.0 mm (from inner_length_u/inner_width_v)
# Extrude distance: 1120.0 mm along -w direction (which is -x in world)
# The frame's u_dir = [0,0,-1], v_dir = [0,1,0], w_dir = [1,0,0]
# So in world: u = -z, v = y, w = x
# The profile is in the uv-plane (y-z plane), extruded along w (x)
# Outer ring: u from -6.12 to -1.88, v from 10.88 to 15.12
# Inner ring: u from -6.0 to -2.0, v from 11.0 to 15.0
# Note: u is along -z, v is along y. So in world: z = -u, y = v
# Outer: z from 1.88 to 6.12, y from 10.88 to 15.12
# Inner: z from 2.0 to 6.0, y from 11.0 to 15.0
# Extrude along x from 0 to -1120 (since direction is -w = -x)

# Build the outer rectangle
outer = (
    cq.Workplane("YZ")
    .center(0, 0)
    .rect(42.4, 42.4)
    .extrude(1120.0)
)

# Build the inner rectangle (to be subtracted)
inner = (
    cq.Workplane("YZ")
    .center(0, 0)
    .rect(40.0, 40.0)
    .extrude(1120.0)
)

# Subtract inner from outer to create hollow frame
result = outer.cut(inner)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\101817_b02acd9f_0002\\neg_03/generated.step")
