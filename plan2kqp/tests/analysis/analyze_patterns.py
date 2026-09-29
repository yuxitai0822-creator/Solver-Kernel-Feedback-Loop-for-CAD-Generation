"""Analyze the 50 hand-written KQP instances to extract query emission patterns.

For each sample, list: profile type, query set, source_field patterns.
Then aggregate by profile type to find deterministic rules.
"""
import json
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
INSTANCES = ROOT / "compiler" / "instances_v6"
KQP_DIR = ROOT / "KQP" / "samples" / "v0.2"

# 1. Map each kqp to (profile, query_set)
PTYPE_QUERIES = defaultdict(Counter)
# (profile, intent) -> (source_field pattern, expected_value pattern, feedback_template pattern)
PTYPE_INTENT_DETAIL = defaultdict(list)
# Profile -> count
PTYPE_COUNT = Counter()

for kqp_path in sorted(KQP_DIR.glob("*.kqp_instance.json")):
    kqp = json.loads(kqp_path.read_text(encoding="utf-8"))
    sid = kqp["design_plan_id"]
    plan_path = INSTANCES / f"{sid}.design_plan.json"
    if not plan_path.exists():
        continue
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    ptype = plan["solid_bodies"][0]["profiles"][0]["type"]
    PTYPE_COUNT[ptype] += 1
    intent_count = Counter()
    for q in kqp["queries"]:
        intent = q["intent"]
        intent_count[intent] += 1
        PTYPE_INTENT_DETAIL[(ptype, intent)].append({
            "sid": sid,
            "source_field": q.get("source_field", ""),
            "expected": q.get("expected"),
            "tolerance": q.get("tolerance"),
            "feedback_template": q.get("feedback_template", ""),
            "params": q.get("params"),
        })
    PTYPE_QUERIES[ptype][sid] = dict(intent_count)

print("=" * 80)
print("Profile type distribution across 50 manual KQP instances")
print("=" * 80)
for p, c in PTYPE_COUNT.most_common():
    print(f"  {p}: {c}")
print()

print("=" * 80)
print("Query intents per profile type (with frequency)")
print("=" * 80)
for ptype in sorted(PTYPE_QUERIES.keys()):
    all_intents = Counter()
    for sid, intents in PTYPE_QUERIES[ptype].items():
        for intent, cnt in intents.items():
            all_intents[intent] += cnt
    n_samples = PTYPE_COUNT[ptype]
    print(f"\n[{ptype}]  n_samples={n_samples}")
    for intent, total in all_intents.most_common():
        # how many samples have this intent at all?
        samples_with = sum(1 for intents in PTYPE_QUERIES[ptype].values() if intent in intents)
        print(f"  {intent}: total={total}, samples={samples_with}/{n_samples}")
print()

print("=" * 80)
print("Sample query details (first 3 per (ptype, intent))")
print("=" * 80)
for (ptype, intent), details in sorted(PTYPE_INTENT_DETAIL.items()):
    print(f"\n[{ptype}][{intent}]  count={len(details)}")
    for d in details[:3]:
        sf = d["source_field"]
        sf_short = sf if len(sf) < 60 else sf[:57] + "..."
        ft = d["feedback_template"]
        ft_short = ft if len(ft) < 60 else ft[:57] + "..."
        print(f"  {d['sid']}: expected={d['expected']!r:30} tol={d['tolerance']!r:15} src={sf_short}")
        print(f"    ft: {ft_short}")
        if d["params"]:
            print(f"    params: {d['params']}")
