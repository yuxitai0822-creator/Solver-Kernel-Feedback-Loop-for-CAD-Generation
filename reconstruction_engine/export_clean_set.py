"""Export the Clean Reconstruction Set: samples where generated STEP passes KQP 100%."""
import sys, json
from pathlib import Path
sys.path.insert(0, r'D:/PythonProgramming/CAD Generation/Constraint-grounded agentic CAD generation/子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究')
from kqp.runner.run_kqp import run_kqp

ROOT = Path(r'D:/PythonProgramming/CAD Generation/Constraint-grounded agentic CAD generation/子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究')
KQP_DIR = ROOT / 'kqp/samples/v0.2'
PLAN_DIR = ROOT / 'DesignPlan/compiler/instances_v6'
GEN_DIR = ROOT / 'Reconstruction_results'
OUT = ROOT / 'Reconstruction_results/clean_reconstruction_set.json'

clean_samples = []
isolated_samples = []
for kqp_path in sorted(KQP_DIR.glob('*.kqp_instance.json')):
    sid = kqp_path.stem.replace('.kqp_instance', '')
    step_path = GEN_DIR / sid / 'generated.step'
    if not step_path.exists():
        isolated_samples.append({"sample_id": sid, "reason": "no generated STEP"})
        continue
    plan_path = PLAN_DIR / f'{sid}.design_plan.json'
    kqp = json.loads(kqp_path.read_text(encoding='utf-8'))
    plan = json.loads(plan_path.read_text(encoding='utf-8'))
    r = run_kqp(step_path, kqp, plan)
    if r['overall_status'] == 'pass':
        clean_samples.append({
            "sample_id": sid,
            "n_queries": r['summary']['total_queries'],
            "step_path": str(step_path),
        })
    else:
        fails = [(q['query_id'], q['intent'], q['expected'], q['actual'])
                 for q in r['query_results'] if q['status'] != 'pass']
        isolated_samples.append({
            "sample_id": sid,
            "reason": "KQP fail",
            "failing_queries": fails,
        })

report = {
    "clean_set_size": len(clean_samples),
    "isolated_set_size": len(isolated_samples),
    "total": len(clean_samples) + len(isolated_samples),
    "clean_samples": clean_samples,
    "isolated_samples": isolated_samples,
    "task5_plan": {
        "base_samples": len(clean_samples),
        "perturbations_per_sample": "2-3",
        "expected_negatives": f"{len(clean_samples)*2}-{len(clean_samples)*3}",
        "minimum_required": 100,
        "sufficient": len(clean_samples) * 2 >= 100,
    },
}
OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'Clean Set: {len(clean_samples)} samples')
print(f'Isolated:  {len(isolated_samples)} samples')
print(f'Task 5 expected negatives: {len(clean_samples)*2}-{len(clean_samples)*3}')
print(f'Sufficient for >=100: {len(clean_samples)*2 >= 100}')
print(f'Report: {OUT}')
