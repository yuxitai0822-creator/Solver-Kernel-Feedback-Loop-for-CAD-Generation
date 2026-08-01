import cadquery as cq

# Design Plan: extruded annulus (bearing)
# Outer radius = 6.0 mm, Inner radius = 4.25 mm, Extrude distance = 12.0 mm
# Frame: u_dir=[1,0,0], v_dir=[0,0,-1], w_dir=[0,1,0]
# Profile on XZ plane (u,v), extrude along Y (w)

OUT_STEP_PATH = r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\phase2b_m0m3\M3_SolverKQP\102410_f9877a7b_0012\neg_01\iter_01/generated.step"

# Build the annulus profile on XZ plane
wp = cq.Workplane("XZ")

# Outer circle
wp = wp.moveTo(0, 0).circle(6.0)

# Inner circle (cut)
wp = wp.circle(4.25)

# Extrude along Y (positive w direction) by 12.0 mm
result = wp.extrude(12.0)

# Export using correct function name
cq.exporters.export(result, OUT_STEP_PATH)
print(f"Exported to {OUT_STEP_PATH}")