import cadquery as cq

outer_radius = 6.0
inner_radius = 4.25
extrude_distance = 12.0

result = (
    cq.Workplane("XY")
    .circle(outer_radius)
    .circle(inner_radius)
    .extrude(extrude_distance)
)

cq.exporters.export(result, OUT_STEP_PATH)