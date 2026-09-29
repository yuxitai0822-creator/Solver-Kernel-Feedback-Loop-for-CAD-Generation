"""Generate sanity_set_50_index.json — frozen index of all 50 samples.
(moved: outputs now under data/phase1_positive/reconstruction/sanity_set_50_index.json)"""
import json
from pathlib import Path

ROOT = Path(r'D:/PythonProgramming/CAD Generation/Constraint-grounded agentic CAD generation/子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究')
manifest = json.load(open(ROOT / 'data/phase0_initial/manifest.json', encoding='utf-8'))

samples = []
for e in manifest['entries']:
    sid = e['id']
    samples.append({
        'sample_id': sid,
        'history_json': f'data/phase0_initial/history/{sid}.json',
        'gt_step': f'data/phase0_initial/step/{sid}.step',
        'design_plan': f'data/phase1_positive/design_plan/instances/{sid}.design_plan.json',
        'kqp_instance': f'data/phase1_positive/kqp/instances/v0.2/{sid}.kqp_instance.json',
    })

index = {
    'dataset_name': 'phase0_initial',
    'num_samples': len(samples),
    'selection_rule': manifest.get('selection_rule', ''),
    'samples': samples,
}

out = ROOT / 'data/phase1_positive/reconstruction/sanity_set_50_index.json'
out.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'Wrote {out} ({len(samples)} samples)')
