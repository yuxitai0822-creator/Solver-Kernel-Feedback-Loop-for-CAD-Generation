import cadquery as cq
from cadquery import exporters
import math

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M2_KQPOnly\101817_b02acd9f_0004\neg_03\iter_00/generated.step"

# Design Plan: extruded rectangle
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Rectangle dimensions: length_u=1200.0 mm, width_v=600.0 mm
# Extrude distance: 20.0 mm along +w direction
# The rectangle profile is defined in UV space with corners:
#   (127.82976131535646, -66.34402294937294) -> (7.829761315356478, -66.34402294937294)
#   (127.82976131535646, -6.344022949372942) -> (127.82976131535646, -66.34402294937294)
#   (7.829761315356478, -6.344022949372942) -> (127.82976131535646, -6.344022949372942)
#   (7.829761315356478, -66.34402294937294) -> (7.829761315356478, -6.344022949372942)
# The UV coordinates span: u from 7.82976 to 127.82976 (delta=120.0), v from -66.34402 to -6.34402 (delta=60.0)
# But the design plan says length_u=1200.0 and width_v=600.0, so there's a scaling factor of 10x.
# The original data was in cm and converted to mm (x10). The UV coordinates appear to be in cm originally.
# We'll build the rectangle with the correct dimensions in mm.

# Build the rectangle on the XZ plane (since v_dir is [0,0,-1], the sketch plane is XZ)
# The frame: u_dir = X axis, v_dir = -Z axis, w_dir = Y axis
# So the sketch plane is XZ, and extrude direction is +Y (w_dir)

# Create the rectangle centered at origin with dimensions 1200 x 600
result = (
    cq.Workplane("XZ")
    .rect(1200.0, 600.0, centered=True)
    .extrude(20.0)
)

# Export to STEP
import os
os.makedirs(os.path.dirname(OUT_STEP_PATH), exist_ok=True)
exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")
