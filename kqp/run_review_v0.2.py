"""run_review_v0.2.py — wrapper to run review_batch_1.main on v0.2 manual."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import review_batch_1

# Override KQP_DIR to point at v0.2 (updated manual)
review_batch_1.KQP_DIR = Path(r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\KQP\samples\v0.2")
review_batch_1.PLAN_DIR = Path(r"D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\DesignPlan\compiler\instances_v6")

if __name__ == "__main__":
    review_batch_1.main()
