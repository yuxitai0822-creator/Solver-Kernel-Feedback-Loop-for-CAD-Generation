# Category C3 — Constraint-Solver / Symbolic-Reasoning–Guided LLM

> **Closest M-method**: M1 (solver feedback channel)
> **Survey count**: 7 works (2020–2024)

---

## Works Surveyed

### 1. LLM+P (Liu et al., 2023)
- **URL**: https://arxiv.org/abs/2304.11477
- **Method**: LLM → PDDL → Fast Downward → plan or error → repair
- **Verifier**: Classical PDDL planner (sound)
- **Feedback**: Plan failure / invalid action → re-prompt LLM
- **Results**: **91–100%** plan accuracy across 8 IPC domains; beats SayCan, Code-as-Policies on Robotouille
- **Mapping**: **M1 analog** (planner is the solver)

### 2. DreamCoder (Ellis et al., NeurIPS 2021)
- **URL**: https://arxiv.org/abs/2006.08381
- **Method**: Wake-sleep Bayesian program synthesis; growing library
- **Verifier**: Typed functional interpreter (sound); counter-examples on inputs
- **Results**: ~80% recovery on classic programs; rediscovers physics laws
- **Mapping**: **M1 analog** (interpreter as constraint oracle)

### 3. LeanDojo (ReProver) (Yang et al., NeurIPS 2023)
- **URL**: https://arxiv.org/abs/2306.15626
- **Method**: Retrieval-augmented LLM + Lean 3 prover
- **Verifier**: Lean 3 kernel (sound); proof-state diff + tactic error
- **Dataset**: 98,734 theorems from Lean mathlib
- **Mapping**: **M1 analog** (tactic error is the solver feedback)

### 4. FunSearch (Romera-Paredes et al., *Nature* 2024)
- **DOI**: https://www.nature.com/articles/s41586-023-06931-7
- **Method**: Evolutionary program search with Codey/PaLM-2 LLM
- **Verifier**: User-supplied deterministic scorer
- **Results**: New cap-set constructions; beats classical online bin-packing
- **Mapping**: **M1 analog** (scorer is the solver)

### 5. AlphaGeometry (Trinh et al., *Nature* 2024)
- **DOI**: https://www.nature.com/articles/s41586-023-06747-5
- **Method**: Transformer + DDAR symbolic Euclidean-geometry prover
- **Verifier**: DDAR (forward-chaining over axioms)
- **Results**: **25/30** on IMO-AG (vs. ~10/30 SOTA)
- **Mapping**: **M1+M2 combined** (closest to **geometric** CAD feedback)

### 6. AlphaProof (DeepMind, 2024)
- **URL**: https://deepmind.google/discover/blog/ai-solves-imo-problems-at-silver-medal-level/
- **Method**: AlphaZero-style RL over Lean-formalized problems + Gemini policy + Lean 4 verifier
- **Results**: **28/42 = silver medal** on IMO 2024
- **Mapping**: **M1+M2 combined** (tightest LLM-symbolic-verifier loop)

### 7. SAT-LM (Poole-Dayan, 2023)
- **Method**: SAT solver as per-token filter on LLM vocabulary during constrained decoding
- **Verifier**: SAT solver (PicoSAT / Glucose)
- **Results**: Significantly reduces constraint violations on constrained-decoding benchmarks
- **Mapping**: **M1 analog** (per-token constraint enforcement)

### 8. Codex + Z3 (multiple works)
- **Pattern**: LM proposes program → Z3 verifies pre/post conditions → counter-example → re-prompt
- **Representative**: Code-gen with static-analysis feedback, program synthesis with execution feedback
- **Mapping**: **M1 analog** (Z3 counter-examples are solver feedback)

---

## Coverage summary

| Solver class | Representative works |
|---|---|
| Classical planner | LLM+P |
| Typed interpreter | DreamCoder |
| Theorem prover (ITP) | LeanDojo (Lean 3), AlphaProof (Lean 4) |
| Symbolic geometry prover | AlphaGeometry (DDAR) |
| SAT/SMT | SAT-LM, Codex+Z3 |
| Scorer | FunSearch |

**Critical observation**: LeanDojo, AlphaProof, and AlphaGeometry are the
tightest existing LLM-symbolic-verifier feedback loops in the literature.
None targets CAD directly, but the architectural pattern (LLM ↔ verifier
with concrete error messages) maps directly onto M1's solver channel.
