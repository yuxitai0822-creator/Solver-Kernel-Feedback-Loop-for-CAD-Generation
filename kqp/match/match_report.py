"""match_report.py — Generate the final match report from compiler_v0.1 vs
manual KQP instances.

Usage: python match_report.py
Writes: match_report_v0.1.json (canonical report)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from semantic_match import main_match

ROOT = Path(__file__).resolve().parents[2]
manual = ROOT / "KQP" / "samples" / "v0.2"
compiler = ROOT / "KQP" / "outputs" / "compiler_v0.1"

report = main_match(manual, compiler)
out = Path(__file__).parent / "match_report_v0.1.json"
out.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str),
               encoding="utf-8")
print(f"Wrote {out}")
print()
print(f"Sample match: {report['matched_samples']}/{report['total_samples']} ({report['sample_match_rate']*100:.0f}%)")
print(f"Query match:  {report['total_query_pairs_matched']}/{report['total_queries_manual']} ({report['query_match_rate']*100:.0f}%)")
print(f"Mismatches:   {sum(1 for s in report['per_sample'] if s.get('mismatches'))} samples with mismatches")

