# §13 Stop-Bar Sensitivity — Threshold Replay Report

- M3 root: `D:\PythonProgramming\CAD Generation\Constraint-grounded agentic CAD generation\子课题1-Solver-Kernel双反馈闭环驱动的CAD生成质量提升研究\experiments\results_v0.2\M3_SolverKQP`
- samples included: **1** (skipped: 0)

## Central Table (§13.5 — DUAL COLUMN)

⚠️ **`own_bar_stop_rate` and `mean_stop_iter` are NOT comparable across bars** (different denominators).
Only `common_bar_quality` is cross-bar comparable.

| Bar | n | own-bar stop rate | mean stop iter | **common-bar (B3) final quality** | quality gap vs B3 | mean token savings vs B3 |
|-----|---|------------------|----------------|------------------------------------|---------------------|-----------------------------|
| B0 | 1 |     0.0% |      - | **    0.0%** | +   0.0% | +      0 |
| B1 | 1 |     0.0% |      - | **    0.0%** | +   0.0% | +      0 |
| B2 | 1 |     0.0% |      - | **    0.0%** | +   0.0% | +      0 |
| B3 | 1 |     0.0% |      - | **    0.0%** | +   0.0% | +      0 |

## Interpretation (§13.6)

- B0 → B3 common-bar quality gap: **0.0**
- B2 − B1 common-bar quality gap: **0.0**
- Verdict: `small_gap`
- Triggers N0–N3 (§13.7)? **False**

> M3 trajectory is full-feedback; weaker-bar deployment quality ≤ this common-bar quality (upper bound per §13.6).

## §13.7 N0–N3 Conditional Trigger

- triggered: **False**
- reason: B0→B3 gap < 0.10; §13 alone suffices.

## §13.9 Acceptance

- [x] four bars B0–B3 defined with monotonicity (§13.3)
- [x] replay reuses M3 artefacts only — no new LLM (§13.4)
- [x] central table reports BOTH own-bar (non-comparable) AND common-bar (comparable) with caption (§13.5)
- [x] over-trust upper-bound caveat included (§13.6)
- [x] N0–N3 gated behind gap condition (§13.7)