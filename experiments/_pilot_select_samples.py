"""_pilot_select_samples.py — materialise pilot sample selection."""
import json, os, collections, random

with open('task5_negative_perturbation/reports/kqp_detection_summary.json',
            encoding='utf-8') as f:
    summary = json.load(f)
eligible = [r for r in summary['rows']
              if r.get('eligible_for_detection_eval')]

op_to_pair = {}
for r in eligible:
    sid = r['sample_id']
    nid = r.get('negative_id', 'neg_01')
    with open(f'task5_negative_perturbation/perturbations/{sid}/{nid}/perturbation_meta.json',
                encoding='utf-8') as f:
        meta = json.load(f)
    op_to_pair[(sid, nid)] = meta.get('operator_input_name')

by_op = collections.defaultdict(list)
for pair, op in op_to_pair.items():
    by_op[op].append(pair)

random.seed(42)

# Stratum 1: 4 KQP-visible via E1 (2 envelope_u + 2 envelope_v_shrink)
e1_u = random.sample(by_op['E1_envelope_u'], 2)
e1_v = random.sample(by_op['E1_envelope_v_shrink'], 2)
# Stratum 1': 4 KQP-visible via E2 (4 extrude_deep)
e2_d = random.sample(by_op['E2_extrude_deep'], 4)
kqp_selected = e1_u + e1_v + e2_d

# Stratum 2: 6 solver-visible
e3 = random.sample(by_op['E3_radius_up'], 3)
e4 = random.sample(by_op['E4_void_add'] + by_op['E4_void_remove_one'], 3)
solver_selected = e3 + e4

# Stratum 3: E5 (only 1 eligible)
edge_selected = list(by_op.get('E5_extent_type_change', []))

# Stratum 4: pad to 18 with 3 fragile from E2 pool
all_picked = set(kqp_selected + solver_selected + edge_selected)
# restrict fragile to operators that are known-clean (KQP-success likely)
fragile_pool = [pair for pair in by_op['E2_extrude_deep'] + by_op['E2_extrude_shallow']
                 if pair not in all_picked]
fragile_selected = random.sample(fragile_pool, min(3, len(fragile_pool))) if fragile_pool else []

# Build final list, dedup
total_seen = set()
pilot = []
for bucket in (kqp_selected, solver_selected, edge_selected, fragile_selected):
    for pair in bucket:
        if pair in total_seen:
            continue
        total_seen.add(pair)
        pilot.append(pair)
# Pad with E2 if short
if len(pilot) < 18:
    extras = [p for p in by_op['E2_extrude_deep'] if p not in total_seen]
    for pair in extras:
        if len(pilot) >= 18:
            break
        pilot.append(pair)
        total_seen.add(pair)

print(f'KQP-visible:        {len(kqp_selected)}')
print(f'Solver-visible:     {len(solver_selected)}')
print(f'Both/edge:          {len(edge_selected)}')
print(f'Fragile:            {len(fragile_selected)}')
print(f'TOTAL:              {len(pilot)}')
print()
print('Pilot sample list:')
for pair in pilot:
    sid, nid = pair
    op = op_to_pair.get(pair, 'unknown')
    print(f'  {sid}/{nid}   op={op}')

selection = {
    'selection_seed': 42,
    'rationale': 'Per pilot_protocol §1.2 grid; padded to 18 with E2_extrude_deep extras',
    'negative_samples': {
        'kqp_visible_solver_blind': [
            {'sample_id': s, 'negative_id': n} for s, n in kqp_selected],
        'solver_visible': [
            {'sample_id': s, 'negative_id': n} for s, n in solver_selected],
        'both_visible_edge': [
            {'sample_id': s, 'negative_id': n} for s, n in edge_selected],
        'pipeline_fragile': [
            {'sample_id': s, 'negative_id': n} for s, n in fragile_selected],
    },
    'positive_samples': [],
    'no_op_decision': 'Option A deferred — no-op CLI not yet implemented',
    'all_negative_samples': [
        {'sample_id': s, 'negative_id': n} for s, n in pilot],
}

os.makedirs('experiments/pilot', exist_ok=True)
with open('experiments/pilot/pilot_sample_selection.json', 'w',
            encoding='utf-8') as f:
    json.dump(selection, f, indent=2, ensure_ascii=False)
print('Wrote experiments/pilot/pilot_sample_selection.json')
