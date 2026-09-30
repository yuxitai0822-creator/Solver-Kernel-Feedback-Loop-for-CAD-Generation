import cadquery as cq

# Design Plan: extruded rectangle (flat plate/panel)
# Dimensions: length_u = 1219.2 mm, width_v = 2590.8 mm, extrude_distance = 44.45 mm
# The profile rectangle is defined in UV space with u_dir = (1,0,0), v_dir = (0,0,-1), w_dir = (0,1,0)
# The rectangle corners in UV: 
#   start_uv = (121.17356129030935, 31.299551148092803)
#   end_uv = (-0.7464387096940412, 31.299551148092803)  -> this is the other corner along u
#   Actually the curves define a rectangle with u range [-0.7464, 121.1736] and v range [31.2996, 290.3796]
#   So width in u = 121.1736 - (-0.7464) = 121.92 cm = 1219.2 mm (matches length_u)
#   Width in v = 290.3796 - 31.2996 = 259.08 cm = 2590.8 mm (matches width_v)
# The extrude is along +w direction (0,1,0) by 44.45 mm

# Build the rectangle in the XY plane (since u_dir = X, v_dir = Z negative, w_dir = Y)
# To match the frame: u along X, v along -Z, w along Y
# So the rectangle lies in the XZ plane (since u and v axes are X and -Z)
# We'll create a rectangle on the XZ plane, then extrude along Y

# The rectangle corners in UV: u from -0.7464387096940412 to 121.17356129030935, v from 31.299551148092803 to 290.379551148076
# In XYZ: x = u, z = -v (since v_dir = (0,0,-1)), y = 0 initially

# Compute corners:
x_min = -0.7464387096940412
x_max = 121.17356129030935
z_min = -290.379551148076  # because v_max -> -v_max
z_max = -31.299551148092803  # because v_min -> -v_min

# Create the rectangle on the XZ plane (y=0)
result = (cq.Workplane("XZ")
          .center((x_min + x_max)/2, (z_min + z_max)/2)
          .rect(x_max - x_min, z_max - z_min)
          .extrude(44.45))  # extrude along Y (positive)

# Export
cq.exporters.export(result, r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_full\M3_SolverKQP\108244_329b1876_0000\neg_03/generated.step")
