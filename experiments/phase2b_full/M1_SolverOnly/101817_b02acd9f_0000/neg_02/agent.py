import cadquery as cq

# Design Plan: extruded rectangular frame
# Outer rectangle: 40mm x 40mm (u: 10 to 6, v: -7 to -3 -> span 4 in uv? Wait, need to interpret correctly)
# The profile is defined in a local UV frame where:
#   u_dir = (1,0,0)  -> X axis
#   v_dir = (0,0,-1) -> -Z axis
#   w_dir = (0,1,0)  -> Y axis (extrude direction)
#
# Outer ring curves (in UV):
#   (10, -7) -> (6, -7)   : line along -u
#   (10, -3) -> (10, -7)  : line along -v
#   (6, -3)  -> (10, -3)  : line along +u
#   (6, -7)  -> (6, -3)   : line along +v
# So outer rectangle spans u in [6, 10] and v in [-7, -3].
# Span in u: 4, span in v: 4. But expected outer dimensions are 40mm x 40mm.
# This suggests the UV coordinates are in cm (since compiler note says cm_to_mm x10).
# So multiply all UV coordinates by 10 to get mm.
#
# After scaling: outer u: [60, 100], v: [-70, -30] -> span 40mm each.
# Inner ring (in UV after scaling):
#   (61.2, -68.8) -> (61.2, -31.2)  : line along +v
#   (61.2, -31.2) -> (98.8, -31.2)  : line along +u
#   (98.8, -31.2) -> (98.8, -68.8)  : line along -v
#   (98.8, -68.8) -> (61.2, -68.8)  : line along -u
# Inner span: u: [61.2, 98.8] -> 37.6mm, v: [-68.8, -31.2] -> 37.6mm.
#
# Extrude along +w (Y axis) by 780mm.

scale = 10.0  # cm to mm

# Outer rectangle corners (scaled)
outer_pts = [
    (10.0 * scale, -7.0 * scale),
    (6.0 * scale, -7.0 * scale),
    (6.0 * scale, -3.0 * scale),
    (10.0 * scale, -3.0 * scale),
]

# Inner rectangle corners (scaled)
inner_pts = [
    (6.12 * scale, -6.88 * scale),
    (6.12 * scale, -3.12 * scale),
    (9.88 * scale, -3.12 * scale),
    (9.88 * scale, -6.88 * scale),
]

# Build the profile in the XY plane (since u_dir = X, v_dir = -Z, we map v to -Z)
# But CadQuery works in XY plane for 2D sketches, then extrudes along Z.
# We need to map: u -> X, v -> -Z, w -> Y.
# So in sketch plane (XY), we use (u, -v) as (X, Y) because v_dir = -Z, and we want Z up.
# Actually simpler: define the profile in the XZ plane? Let's think.
# The frame says u_dir = (1,0,0) = X, v_dir = (0,0,-1) = -Z, w_dir = (0,1,0) = Y.
# So the profile lies in the X-Z plane (u along X, v along -Z).
# Extrude along Y (w).
# In CadQuery, we can create a workplane on the XZ plane (front plane) and draw.
# But the sketch is 2D in that plane: X for u, Z for v (but v_dir is -Z, so v coordinate maps to -Z).
# So point (u, v) in UV maps to (X=u, Z=-v) in 3D.

# Create the outer wire
outer_wire = cq.Workplane("XZ").moveTo(outer_pts[0][0], -outer_pts[0][1])
for pt in outer_pts[1:]:
    outer_wire = outer_wire.lineTo(pt[0], -pt[1])
outer_wire = outer_wire.close()

# Create the inner wire
inner_wire = cq.Workplane("XZ").moveTo(inner_pts[0][0], -inner_pts[0][1])
for pt in inner_pts[1:]:
    inner_wire = inner_wire.lineTo(pt[0], -pt[1])
inner_wire = inner_wire.close()

# Combine into a single sketch with a hole
# We can use the outer wire as the base and cut the inner wire.
# But CadQuery's Workplane doesn't directly support nested wires from separate workplanes.
# Better approach: create the profile as a single wire with a hole using cq.Wire.
# Or use cq.Solid.extrudeLinear with a face that has a hole.
# Let's build the face manually using cq.Wire and cq.Face.

# Build outer wire
outer_verts = [cq.Vector(pt[0], 0, -pt[1]) for pt in outer_pts]  # Y=0 for sketch plane
outer_edges = []
for i in range(len(outer_verts)):
    p1 = outer_verts[i]
    p2 = outer_verts[(i+1) % len(outer_verts)]
    outer_edges.append(cq.Edge.makeLine(p1, p2))
outer_wire_cq = cq.Wire.assembleEdges(outer_edges)

# Build inner wire
inner_verts = [cq.Vector(pt[0], 0, -pt[1]) for pt in inner_pts]
inner_edges = []
for i in range(len(inner_verts)):
    p1 = inner_verts[i]
    p2 = inner_verts[(i+1) % len(inner_verts)]
    inner_edges.append(cq.Edge.makeLine(p1, p2))
inner_wire_cq = cq.Wire.assembleEdges(inner_edges)

# Create face with hole
face = cq.Face.makeFromWires(outer_wire_cq, [inner_wire_cq])

# Extrude along Y (w direction) by 780mm
extrude_distance = 780.0
result = cq.Solid.extrudeLinear(face, cq.Vector(0, extrude_distance, 0))

# Export
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M1_SolverOnly\\101817_b02acd9f_0000\\neg_02/generated.step")
