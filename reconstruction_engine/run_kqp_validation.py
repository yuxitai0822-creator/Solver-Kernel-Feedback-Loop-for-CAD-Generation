"""Run KQP on all 50 generated STEPs and write a verification report."""
import sys, json, os
from pathlib import Path
sys.path.insert(0, r'D:/PythonProgramming/CAD Generation/Constraint-grounded agentic CAD generation/子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究')
from kqp.runner.run_kqp import run_kqp

ROOT = Path(r'D:/PythonProgramming/CAD Generation/Constraint-grounded agentic CAD generation/子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究')
KQP_DIR = ROOT/'kqp/samples/v0.2'
PLAN_DIR = ROOT/'DesignPlan/compiler/instances_v6'
GEN_DIR = ROOT/'Reconstruction_results'
OUT = ROOT/'Reconstruction_results/gt_vs_generated_kqp_validation'

n_pass = n_fail = 0
query_pass = 0
query_total = 0
failures = []
for kqp_path in sorted(KQP_DIR.glob('*.kqp_instance.json')):
    sid = kqp_path.stem.replace('.kqp_instance','')
    step_path = GEN_DIR / sid / 'generated.step'
    if not step_path.exists(): continue
    plan_path = PLAN_DIR / f'{sid}.design_plan.json'
    kqp = json.loads(kqp_path.read_text())
    plan = json.loads(plan_path.read_text())
    r = run_kqp(step_path, kqp, plan)
    s = r['summary']
    query_total += s['total_queries']
    query_pass += s['passed_queries']
    if r['overall_status'] == 'pass':
        n_pass += 1
    else:
        n_fail += 1
        fail_queries = [qr for qr in r['query_results'] if qr['status']!='pass']
        failures.append((sid, [(q['query_id'], q['intent'], q['expected'], q['actual']) for q in fail_queries]))

report = {
    'phase': 'Phase 2 KQP validation (KQP run on generated STEP)',
    'total_samples': n_pass + n_fail,
    'kqp_pass_samples': n_pass,
    'kqp_fail_samples': n_fail,
    'total_queries': query_total,
    'passed_queries': query_pass,
    'failed_queries': query_total - query_pass,
    'kqp_pass_rate': f'{n_pass/(n_pass+n_fail)*100:.1f}%',
    'query_pass_rate': f'{query_pass/query_total*100:.1f}%',
    'failures': [{'sample_id': f[0], 'failing_queries': f[1]} for f in failures],
}
os.makedirs(OUT, exist_ok=True)
(OUT/'kqp_validation_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'KQP on generated STEP: {n_pass}/{n_pass+n_fail} pass, {query_pass}/{query_total} queries')
for f in failures:
    print(f'  {f[0]}: {f[1]}')
