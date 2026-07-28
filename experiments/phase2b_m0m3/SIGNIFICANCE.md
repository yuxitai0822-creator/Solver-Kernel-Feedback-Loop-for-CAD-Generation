# M0-M3 Significance Analysis

**Frozen triples input**: 120 (each tested under all four methods)  
**Common (sid, nid) pairs**: 120  

## Pass counts

| method | pass / total | pass rate |
|---|---:|---:|
| M0_NoFeedback | 91 / 120 | 75.8% |
| M1_SolverOnly | 81 / 120 | 67.5% |
| M2_KQPOnly | 111 / 120 | 92.5% |
| M3_SolverKQP | 107 / 120 | 89.2% |

## McNemar pairwise (paired on (sid, nid))

Each cell = `a_wins / b_wins` followed by the exact two-sided
McNemar p-value.  `a_wins` is the number of pairs in which the
row method succeeded but the column method did not; `b_wins` is
the reverse.

| row \\ column | M0_NoFeedback | M1_SolverOnly | M2_KQPOnly | M3_SolverKQP |
|---|---|---|---|---|
| M0_NoFeedback | — | 24/14 p=0.1433 | 4/24 p=0.0002* | 10/26 p=0.0113* |
| M1_SolverOnly | 14/24 p=0.1433 | — | 1/31 p=0.0000* | 6/32 p=0.0000* |
| M2_KQPOnly | 24/4 p=0.0002* | 31/1 p=0.0000* | — | 10/6 p=0.4545 |
| M3_SolverKQP | 26/10 p=0.0113* | 32/6 p=0.0000* | 6/10 p=0.4545 | — |

(`*` = p < 0.05)

## Interpretation

**M0_NoFeedback vs M2_KQPOnly** — M0_NoFeedback wins in 4, M2_KQPOnly wins in 24; McNemar p = 0.0002; **significant**.  Does KQP feedback beat no feedback?
**M1_SolverOnly vs M2_KQPOnly** — M1_SolverOnly wins in 1, M2_KQPOnly wins in 31; McNemar p = 0.0000; **significant**.  Does KQP feedback beat solver-only feedback?
**M0_NoFeedback vs M1_SolverOnly** — M0_NoFeedback wins in 24, M1_SolverOnly wins in 14; McNemar p = 0.1433; n.s..  Does solver feedback beat no feedback? (intuition: no)
**M2_KQPOnly vs M3_SolverKQP** — M2_KQPOnly wins in 10, M3_SolverKQP wins in 6; McNemar p = 0.4545; n.s..  Does adding solver feedback to KQP feedback help?
**M3_SolverKQP vs M1_SolverOnly** — M3_SolverKQP wins in 32, M1_SolverOnly wins in 6; McNemar p = 0.0000; **significant**.  Combined vs solver-only — does adding KQP help?

