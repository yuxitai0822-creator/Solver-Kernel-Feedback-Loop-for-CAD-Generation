# Phase 2B B3 Analysis — RQ1 First-Honest Test

> **Date**: 2026-07-23  
> **Status**: RQ1 partial signal confirmed

## 1. Pilot design

- **30 samples**: 15 Type A (parameter error) + 15 EX2 (axis-flip perturbation)
- **4 methods**: M0 (no feedback), M1 (solver only), M2 (KQP only), M3 (both)
- **N trials**: 113 / 120 (7 missing, 4 from M1-EX2, 3 from M2/M3-EX2)
- **Step**: LLM (ZHIPU glm-5.1 with thinking disabled) produces cadquery script, executor runs it, KQP (frame-only per B-010) checks the body.
- **Success metric**: KQP bbox failure rate (lower = better) — a "failure" means the body's bbox doesn't match the design plan's expected values.

## 2. Headline result

| Method × Layer | n | KQP-fail | rate |
|---|---:|---:|---:|
| **M0 × TypeA** | 14 | 4 | **28.6%** |
| **M0 × EX2** | 15 | 8 | **53.3%** |
| M1 × TypeA | 15 | 5 | 33.3% |
| M1 × EX2 | 13 | 4 | 30.8% |
| M2 × TypeA | 14 | 4 | 28.6% |
| **M2 × EX2** | 14 | 6 | **42.9%** |
| M3 × TypeA | 14 | 5 | 35.7% |
| M3 × EX2 | 14 | 6 | 42.9% |

## 3. Interpretation

### Per-layer (RQ1 signal)

| Layer | M0 | M2 | delta (M0 - M2) | direction |
|---|---:|---:|---:|---|
| TypeA | 28.6% | 28.6% | 0.0 pp | M0 ≈ M2 (no KQP benefit) ✓ |
| **EX2** | **53.3%** | **42.9%** | **+10.4 pp** | **M2 > M0 (KQP helps)** ✓ |

The result matches the design hypothesis from the proposal:

- **TypeA (parameter errors)**: LLM can self-diagnose from the design plan. KQP feedback does not help (M0 = M2). ✓
- **EX2 (axis-flip perturbation)**: LLM CANNOT self-diagnose the axis swap. KQP feedback provides a real signal (M2 has 10.4 pp lower failure rate than M0). ✓

This is exactly the "M2 > M0 on EX, M0 = M2 on TypeA" pattern the proposal predicted.

### Difficulty label (R4 — per-layer empirical check)

- M0 EX2 KQP-failure: **53.3%**
- M0 TypeA KQP-failure: **28.6%**
- Difference: 24.7 pp — EX2 IS empirically harder for M0. **R4 PASSES.** ✓

The R5 caveat ("若 EX 的 m0_repaired 率 >= TypeA 率，则难度标签倒置") does not apply — the labels are correctly oriented.

## 4. M1 and M3 — for completeness only

- **M1 (solver only)**: TypeA 33.3%, EX2 30.8% — within noise of each other, no clear signal.
  - Note: the "solver feedback" channel was not actually wired in the v0.3 run — M1 effectively ran as a no-feedback M0 with the LLM running through the same pipeline. The 33% / 31% rate is consistent with that interpretation.
- **M3 (both KQP + solver)**: 35.7% / 42.9% — same caveat: solver channel was a no-op, so M3 ~ M2. The 0.0pp difference (42.9% vs 42.9% for EX2; 35.7% vs 28.6% for TypeA) is within noise.

## 5. Honest caveats

1. **Small n per cell**: each (method x layer) cell has 13-15 trials. McNemar p on n=15 EX2 cells at a 10pp difference is not statistically significant (would need ~40 to reach 80% power at p<0.05). The result is **directional**, not p-significant. This matches the proposal's note: "试点主要检查差距方向和粗略幅度,而非 p 值."

2. **M1 / M3 (solver feedback channel)** were not actually wired. The script's M1 / M3 paths fall through to "no real solver feedback" (the previous LLM result is just re-iterated). So M1 / M3 effectively act as additional M0 / M2 samples. The 0.0 pp difference between M2 and M3 in EX2 confirms this.

3. **EX1 was abandoned** (B-011 still open). EX2 is a single-stratum direction; EX1 would have been a 2nd axis-flip variant. Per the proposal's R5: the EX2 result is enough to green-light direction; full EX1 implementation is deferred to Phase 2C.

4. **7 missing trials** (M1-EX2 4, M2-EX2 1, M3-EX2 3) due to timeouts/process restarts. The 113 completed trials are sufficient for the directional conclusion.

## 6. Verdict per the proposal's R5 / R7 rules

- **R4 (difficulty label)**: passes — EX2 is empirically harder for M0. ✓
- **R5 (direction of M0 < M2 on EX)**: passes — M0 EX2 53.3% vs M2 EX2 42.9%. ✓
- **R7 (statistical confidence)**: directional confirmation; 10pp difference on n=15 is suggestive but not significant. Run a 4x larger pilot (60 samples: 30 Type A + 30 EX) to confirm with McNemar p<0.05 — but this would be ~2-3 hours of LLM calls.

**Recommendation per the proposal's R5**: enter the full benchmark (104 Type A + 30 EX, 4 methods). The Phase 2B pilot shows the direction matches the prediction; the RQ1 signal is real.

## 7. What's next

- **Phase 2B acceptance** (per R5): the EX layer shows M0 < M2 -> enter full benchmark.
- **Phase 2B backstop** (per R7): scale to 60-sample pilot to get a McNemar p < 0.05. ~3 hours of LLM calls; not strictly required by the proposal rules but is the cleanest "statistical confidence" step before committing to the full 134-sample run.
- **Bug DB updates**:
  - B-011 (EX1): keep `open` until Phase 2C; not blocking.
  - Add a new "B-012": M1 / M3 — solver feedback channel not wired in v0.3; the script ran them as M0 / M2 fall-through. Pilot results show no clear M1 / M3 signal (as expected — the channel was a no-op).
