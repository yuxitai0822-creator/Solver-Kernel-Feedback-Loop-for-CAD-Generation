# M0-M3 Iterative Agentic System — Runner

This directory contains the M0-M3 iterative framework that supersedes
the v0 single-shot `p2b_full.py`.  The v0 runner stays frozen as a
historical record; this runner writes to a fresh output directory
(`experiments/phase2b_iter/`).

## Architecture

```
p2b_iter_runner.py         # walks (method, sid, nid, layer)
└── trial_iteration.py     # one trial, max 3 iterations
    ├── cad_agent/
    │   ├── prompt_builder_v2.py    # v2 template with feedback slot
    │   ├── prompt_builder.py       # back-compat shim
    │   ├── agent_v2.py             # passes feedback through
    │   └── schema.py               # adds 'reasoning' field
    ├── cad_verification/           # Verification Object framework
    │   ├── pipeline.py
    │   ├── solver.py
    │   └── kernel.py
    └── method_policy.py            # M0-M3 feedback-channel table
```

## M0-M3 feedback-channel policy

| Method | Channels exposed to LLM | Notes |
|---|---|---|
| **M0_NoFeedback**  | `pipeline` only | Solver & kernel failures are NOT shown to the LLM; the agent must self-correct. |
| **M1_SolverOnly**  | `pipeline` + `solver` | Kernel failures are not shown. |
| **M2_KQPOnly**     | `pipeline` + `kernel` | Solver failures are not shown. |
| **M3_SolverKQP**   | all three | Full feedback. |

The three Verification Objects are ALWAYS run (when their inputs are
available); the policy only controls which `diagnostic` fields are
copied into the next iteration's prompt.  This is the
"decouple verification from feedback" invariant from spec §5.

## Per-iteration flow

```
1. Filter iter_history to the active method's channels.
2. Build the v2 prompt
       (Design Plan + Perturbation desc + Previous Code + filtered iter_history)
3. Call the LLM.
   - If "no_change" → exit success.
   - If script is empty → exit failure.
4. Run all 3 verifications.
5. If all 3 pass → exit success.
6. Otherwise record and continue (up to MAX_ITERATIONS=3).
```

## Smoke test (does NOT call the LLM — import / dry-run only)

```bash
"D:/Anaconda/envs/cad_subproject1/python.exe" -c "
import trial_iteration, method_policy
# Dry-run: do not actually call the LLM, just verify the wiring
print('Methods:', method_policy.METHODS_IN_ORDER)
print('Channels per method:')
for m in method_policy.METHODS_IN_ORDER:
    print(' ', m, '->', method_policy.feedback_channels_for(m))
print('MAX_ITERATIONS =', method_policy.MAX_ITERATIONS)
"
```

## Smoke test (calls the LLM — 1 sample × 4 methods)

```bash
"D:/Anaconda/envs/cad_subproject1/python.exe" p2b_iter_runner.py \
    --methods M0_NoFeedback M1_SolverOnly M2_KQPOnly M3_SolverKQP \
    --max-samples 1
```

This will run ~4 trials (one per method on the first (sid, nid) pair),
with up to 3 iterations each.  Each iteration that calls the LLM
incurs a DeepSeek API cost; expect ~$0.05-0.20 for the smoke test.

## Output

Results are written to `experiments/phase2b_iter/pilot_results.json`
with the schema documented in `p2b_iter_runner.py`'s docstring.
Atomic write (`.tmp` + `os.replace`) ensures no half-written file on
crash.

## Frozen / out-of-scope for this commit

- `p2b_full.py` (v0 single-shot) — **frozen, not modified**.
- `experiments/phase2b_full/pilot_results.json` (v0 results) — kept
  as the v0 baseline.
- The negative-CAD-code modality — the LLM is still given the
  *original* design plan; a `perturbation_description` placeholder
  is rendered in the prompt.  Next phase: load the perturbed-history
  → perturbed-script artefact and pass it as the negative CAD code.
