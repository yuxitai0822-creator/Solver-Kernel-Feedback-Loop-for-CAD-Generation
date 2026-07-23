import cadquery as cq
import os

# Ensure output directory exists
OUT_DIR = r'D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_pilot\M2_KQPOnly\102295_86f842dd_0000\ex2'
OUT_STEP_PATH = os.path.join(OUT_DIR, 'generated.step')
os.makedirs(OUT_DIR, exist_ok=True)

# Parameters from design plan (unit conversion cm_to_mm applied)
straight_length = 28.0  # mm
radius = 10.0            # mm
extrude_distance = 4.0  # mm

# Build the stadium extrusion
# A stadium is a rectangle with two semicircular caps on opposite ends.
# We construct it by extruding a rectangle and then unioning two half-cylinders.

# 1. Central rectangular section
rect = (cq.Workplane("XY")
        .rect(straight_length, 2 * radius)
        .extrude(extrude_distance))

# 2. Left semicircular cap (half cylinder)
left_cap = (cq.Workplane("XY")
            .transformed(offset=(0, 0, 0), rotate=(0, 0, 0))
            .circle(radius)
            .extrude(extrude_distance))

# Cut the left cap to keep only the left half (y >= 0 in local coords maps to x <= 0 in stadium center coords)
# The center of the left arc is at x = -straight_length/2. We want the half facing left.
left_half = (cq.Workplane("XY")
             .transformed(offset=(-straight_length/2, 0, 0))
             .rect(radius, 2 * radius)
             .extrude(extrude_distance))

left_cap_half = left_cap.cut(left_half)

# 3. Right semicircular cap (half cylinder)
right_cap = (cq.Workplane("XY")
             .transformed(offset=(straight_length/2, 0, 0))
             .circle(radius)
             .extrude(extrude_distance))

# Cut the right cap to keep only the right half (y <= 0 in local coords maps to x >= 0)
right_half = (cq.Workplane("XY")
              .transformed(offset=(straight_length/2, 0, 0))
              .rect(radius, 2 * radius)
              .extrude(extrude_distance))

right_cap_half = right_cap.cut(right_half)

# 4. Union all three parts to form the complete stadium
result = rect.union(left_cap_half).union(right_cap_half)

# Export the result to STEP file
cq.exporters.export(result, OUT_STEP_PATH)
