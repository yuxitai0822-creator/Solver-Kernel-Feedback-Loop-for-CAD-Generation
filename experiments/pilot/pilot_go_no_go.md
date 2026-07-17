# Pilot v0.1 — Go / No-Go Decision (§6) — REVISED post B-001/B-004 fix

> **Date**: 2026-07-16 (revised 21:00)
> **Decision owner**: human reviewer
> **Inputs**: `pilot_re_read_summary.json`, `pilot_failure_analysis.md`, `bug_db.json`
> **Verdict**: ⚠️ **NO-GO — B-005 blocks the ablation**

---

## What changed since the first §6 draft

| Bug | Fix | Impact |
|-----|-----|--------|
| **B-001** (S2 pre-empts S3) | Reordered S1>S3>S2 | success_at_K correctly attributed |
| **B-004** (pipeline_valid enum) | `_is_truthy_status()` accepts 'pass'/'success' | pipeline_valid True where adapter succeeded |

Pilot artefacts re-evaluated without re-running via `re_read_pilot_results.py`.

---

## Post-fix pilot numbers

### Overall (18 × 4)

| Method | Success@1 | Success@3 | Stops |
|--------|-----------|-----------|-------|
| M0 | 16.7% | **55.6%** | S3:10, S4:7, S2:1 |
| M1 | 16.7% | **55.6%** | S3:10, S2:2, S4:6 |
| M2 | 16.7% | **55.6%** | S3:10, S4:7, S2:1 |
| M3 | 16.7% | **55.6%** | S3:10, S4:7, S2:1 |

### KQP-visible stratum (8 samples)

| Method | Success@3 | Stops |
|--------|-----------|-------|
| M0 | **75.0%** | S3:6, S4:2 |
| M1 | **75.0%** | S3:6, S4:2 |
| M2 | **75.0%** | S3:6, S4:2 |
| M3 | **75.0%** | S3:6, S4:2 |

**All 4 methods identical.** This is a structural finding, not noise.

---

## §6 Go criteria

| # | Criterion | Status |
|---|-----------|:------:|
| 1 | No F-protocol failures | ✅ |
| 2 | **M0 ≠ M2 on KQP-visible stratum** | ❌ **FAILS** |
| 3 | ≥90% parseable | ✅ (72/72) |
| 4 | All 4 methods completed | ✅ (18/18 each) |
| 5 | Artifacts complete | ✅ |

---

## Verdict: **NO-GO**

### Root cause: B-005 — perturbation battery too weak

The task5 perturbation battery produces perturbed IRs that **already pass Success(C) at iter_0** (before any agent call). S3 fires immediately; agent never exercised; all 4 methods converge to identical outcomes.

Per-sample inspection confirms: every iter_0 across all 72 runs has P=True, S=True, K=True → success=True → S3 → stop.

The feedback injection mechanism is NOT broken (pre-fix stop-rule distributions diverged: M0 had 3×S2 vs M2 had 0×S2). But B-005 makes the agent irrelevant because the perturbation doesn't break Success(C) below threshold.

### Resolution options

| Option | Description | Effort |
|--------|-------------|--------|
| **A.** Strengthen perturbation scale (×3.0+) | Increase E1/E2 multiplier so perturbed STEP fails KQP | 2h |
| **B.** Tighten KQP tolerance | Reduce from 0.05 to 0.01 | 1h (re-freeze) |
| **C.** Use canonical ×3.0 in run_benchmark | Bypass task5 battery; apply deterministic perturbation on clean IR | 30min + re-run |
| **D.** Debug why task5 STEP passes KQP | Investigate whether reconstruction engine corrected the perturbation | 4h |

**Recommended: C** — fastest, most controlled.

---

## Bug lifecycle

| Bug | Status | Fixed by |
|-----|--------|----------|
| B-001 (S2 vs S3) | ✅ fixed-shipped | S1>S3>S2 reorder |
| B-002 (§2.2 env doc) | open (doc-only) | — |
| B-003 (out_dir clash) | ✅ fixed-shipped | parse_sample_arg + load_initial_ir |
| B-004 (pipeline enum) | ✅ fixed-shipped | _is_truthy_status helper |
| **B-005** (perturbation too weak) | **open — blocks benchmark** | — |

---

## Next steps

1. **Resolve B-005** (pick A/B/C/D)
2. **Re-run pilot** 18×4 with resolved perturbation
3. **Re-evaluate §6** — if M0 ≠ M2 → GO
4. **Full benchmark** 104×4 — only after pilot GO
