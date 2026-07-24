import cadquery as cq

# Create a rectangular plate based on the design plan
# Dimensions from the plan:
#   length_u = 209.55 mm (along x-axis)
#   width_v = 57.912 mm (along z-axis, since v_dir = [0,0,-1])
#   extrude_distance = 19.05 mm (along y-axis, since w_dir = [0,1,0])
#
# The frame defines:
#   u_dir = [1,0,0]  -> x-axis
#   v_dir = [0,0,-1] -> negative z-axis (but we'll use positive for width)
#   w_dir = [0,1,0]  -> y-axis (extrude direction)
#
# The profile rectangle in UV space:
#   u from 0 to 209.55 (but note: the plan shows 20.955 in curves, 
#   but dimensions say 209.55; the curves appear to be in cm converted to mm,
#   so we use the explicit dimension: 209.55 mm)
#   v from 0 to 57.912 (curves show 5.7912 which is cm -> mm *10 = 57.912)

# Build the plate
result = (
    cq.Workplane("XY")
    .rect(209.55, 57.912)
    .extrude(19.05)
)

# Export to STEP
cq.exporters.export(result, "D:\\PythonProgramming\\CAD Generation\\Constraint-grounded agentic CAD generation\\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\\experiments\\phase2b_full\\M3_SolverKQP\\108851_4d515b10_0009\\neg_02/generated.step")
