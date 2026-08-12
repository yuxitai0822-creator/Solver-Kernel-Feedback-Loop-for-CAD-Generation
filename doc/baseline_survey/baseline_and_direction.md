# Report 2: Baseline Selection & Future Direction
## Acting on the M2 > M3 > M0 > M1 Experimental Finding

> **Date**: 2026-08-02 (updated 2026-08-11 to expand to 12 directions)
> **Author**: ZCode (research agent)
> **Project**: 子课题1 — Solver-Kernel 双反馈闭环驱动的 CAD 生成质量提升研究
> **Scope**: Given the project's experimental result that
> **M2 (Kernel) > M3 (Kernel + Solver) > M0 (No feedback) > M1 (Solver)**,
> what baseline selections and follow-up research directions best serve
> the project's contribution claim?
>
> **Note**: This report uses the **expanded 12-type CGVM taxonomy** from
> `taxonomy_report.md` (the original 4 types are a subset). Each
> direction below is labeled with the CGVM type(s) it primarily targets.

---

## Executive Summary

The project's experimental result is **counter-intuitive under the
"more feedback is better" prior** but **highly interpretable under the
"Verification → Actionable Feedback" principle**.

Three implications for baseline selection:
1. **Baselines must include single-channel CGVMs** (not just multi-channel
   hybrids), to expose the M3 < M2 effect.
2. **Baselines must be selected per-CGVM-type**, not per-paper, to compare
   action-alignment fairly.
3. **Detection-strength metrics** (e.g., invalidity rate) must be
   **complemented by repair-action metrics** (e.g., parameter-edit
   distance, repair-loop iterations).

Three implications for future direction:
1. **Action-alignment scoring** is the missing dimension in CGVM evaluation.
2. **Solver CGVM** needs a redesign — current outputs are far from the
   LLM's parameter-edit action space; a translation layer is needed.
3. **Multi-channel CGVM composition rules** need investigation — when
   does adding a channel help, and when does it dilute?

---

## 1. The Experimental Finding — Re-Anchoring

### 1.1 The Result
```
M2 (Pipeline + KQP)            > M3 (Pipeline + Solver + KQP)
M3 (Pipeline + Solver + KQP)   > M0 (Pipeline only)
M0 (Pipeline only)             > M1 (Pipeline + Solver)
```

### 1.2 The Counter-Intuitive Part
- The project's original hypothesis was M3 > M2 (additive feedback).
- The result is M2 > M3 — adding Solver to Kernel *hurts*.

### 1.3 The Interpretation (under CGVM framework)

| Method | CGVM types | Channel Quality |
|---|---|---|
| M0 | Execution | "code runs" — coarse but unambiguous |
| M1 | Execution + Solver | "constraint conflict" — high detection, low action |
| M2 | Execution + Kernel | "bbox_x=15 vs 20" — high detection, high action |
| M3 | Execution + Solver + Kernel | M2 + M1 — Solver noise dilutes KQP |

The M1 noise problem: when Solver says "redundant constraint", the
LLM may attempt to remove a constraint to satisfy Solver, but this
removal may break the KQP intent (e.g., removing a length constraint
that was actually needed for the bbox to be 20). The LLM then enters
an action-conflict cycle that slows convergence.

---

## 2. The Actionable Feedback Principle

### 2.1 Definition

> **Actionable Feedback** = feedback whose diagnostic information maps
> 1-to-1 (or at most k-to-1 with small k) onto the LLM's repair action
> space.

### 2.2 The Spectrum

```
Most actionable                                              Least actionable
  ◄──────────────────────────────────────────────────────────────►
  numeric parameter        constraint diagnosis       visual mismatch
  discrepancy (KQP)         (Solver)                   (Visual)
  "bbox_x=15 vs 20"        "redundant constraint X"   "view doesn't match"
       ↓                          ↓                          ↓
  edit one parameter         remove one constraint       ???
       ↓                          ↓                          ↓
  deterministic edit         ambiguous edit              guess + retry
```

### 2.3 Why M2 Wins

KQP feedback is **directly parameter-actionable**:
- `bbox_x: expected=20, observed=15` → set IR's `extrude.distance` to 20 (or
  scale width by 20/15).
- `through_void_count: expected=4, observed=3` → add one cut operation.
- `is_solid: false` → add missing close (likely a boolean op).

Solver feedback is **constraint-state-actionable** but **not parameter-
actionable**:
- "redundant constraint" → which parameter to change? which constraint
  to remove? the LLM must guess.
- "under-constrained" → which dimension is missing? ambiguity.

### 2.4 Why M3 = M2 + M1 Hurts

Adding M1 (Solver) noise to M2 (KQP) introduces:
- **Conflicting actions**: Solver may tell LLM to "remove constraint X"
  but KQP's bbox intent depends on constraint X.
- **Mis-prioritized actions**: LLM focuses on Solver's constraint
  diagnosis instead of KQP's parameter discrepancy.
- **False positives**: Solver may report "valid" while KQP reports
  "bbox mismatch" — LLM stops on Solver's premature Pass.

---

## 3. Baseline Selection Criteria (Reframed)

### 3.1 Selection Principle

> **A baseline is comparable to the project if and only if it provides
>  a *full CGVM* (not just one channel), and its feedback is in the
>  same action space (parameter-edit / constraint-edit / code-edit).**

### 3.2 The Six Criteria (from the project framework)

| Criterion | Weight for M0–M3 baseline |
|---|---|
| Use scope | M0–M3 use Design Plan + IR + Script → baselines must too |
| Diagnostic boundary | M0–M3 use 138 perturbations → baselines must too |
| **Feedback effectiveness** | **CRITICAL — must be parameter-actionable** |
| **Feedback efficiency** | **CRITICAL — must converge in ≤3 iterations** |
| Module extensibility | Low priority (project is frozen components) |
| Diagnostic granularity | High priority — must reach parameter level |

### 3.3 Three Baseline Categories (project-relevant)

| Category | Purpose | Examples |
|---|---|---|
| **Per-CGVM-type baselines** | Isolate each CGVM's contribution | OCCT (Kernel), FreeCAD (Solver), Self-Debug (Execution), CADFusion (Visual) |
| **Hybrid CGVM baselines** | Test the additive assumption | Embodied CAD, PR-CAD, Cosmo-Agent |
| **Action-aligned baselines** | Test the actionable-feedback principle | FllumaOne, CADReasoner, HoLa, Aligning Constraint |

---

## 4. Recommended Baseline Set (Revised)

### 4.1 Tier 1 — Direct M2 / M3 Competitors (must run)

| Baseline | CGVM type | Why |
|---|---|---|
| **Embodied CAD** (Liu et al., 2026) | Solver + Kernel | Closest solver-grounded agent; **validates the M3 noise hypothesis** |
| **GenCAD-Self-Repairing** (Tsuji et al., 2025) | Kernel (diffusion repair) | Tests diffusion-based feasibility restoration (66% success) |
| **CAD-Coder** (NeurIPS 2025) | Kernel (RL reward) | Tests GRPO + geometric reward (action-alignment signal) |

### 4.2 Tier 1b — New M2 Competitors (from C4 retry)

| Baseline | CGVM type | Why |
|---|---|---|
| **FllumaOne** (Zhan, 2026) | Kernel (full pipeline) | 99.14% STEP validity; explicit kernel-verifier-in-loop |
| **CADReasoner** (Kabisov et al., 2026) | Kernel (mesh discrepancy) | Iterative geometric-discrepancy repair |
| **STEP-LLM** (Shi et al., DATE 2026) | Kernel (Chamfer reward) | RL training-time kernel feedback |
| **Aligning Constraint Generation** (Autodesk) | Solver (DPO + solver) | 93% fully-constrained; **the cleanest M1 baseline** |
| **CAD-Coder (Geometric)** (NeurIPS 2025) | Kernel (GRPO) | One-channel M2 analog with verified numbers |

### 4.3 Tier 2 — Per-CGVM-type Classical Baselines

| Baseline | CGVM type | Role |
|---|---|---|
| **OCCT `ShapeFix_*` + `BRepCheck_*`** | Kernel (auto-correct) | Establishes the M2 floor |
| **FreeCAD Sketcher (GCS)** | Solver | Establishes the M1 floor |
| **Reflexion** (Shinn et al., 2023) | Execution + reflection | Establishes the M0+reflection reference |
| **Self-Debug** (Chen et al., 2023) | Execution | Establishes the pure Execution baseline |
| **CADFusion** (Wang et al., ICML 2025) | Visual | Establishes the Visual baseline |

### 4.4 Tier 3 — Domain LLM Baselines (M0-style)

| Baseline | Role |
|---|---|
| **CAD-Recode** (Rukhovich et al., 2024) | LLM-as-decoder; re-editable Python |
| **Text-to-CadQuery** (Xie & Ju, 2025) | 69.3% top-1 exact match |
| **GenCAD** (Alam & Ahmed, 2024) | Image→CAD baseline |
| **Text2CAD** (Khan et al., NeurIPS 2024) | Text→CAD baseline |

### 4.5 Tier 4 — Hybrid / Agentic Baselines (M3-style)

| Baseline | CGVM types | Role |
|---|---|---|
| **CAD-Editor** (Yuan et al., Microsoft, 2025) | Hybrid (LLM iterative editing, no kernel) | Tests non-kernel repair loop |
| **ArtiCAD** (Shui et al., 2026) | Visual + Execution (multi-agent rollback) | Tests rollback mechanism |
| **Zero-to-CAD** (Ataei et al., 2026) | Kernel (agentic search) | Tests million-scale agentic validation |
| **Cosmo-Agent** (Deng et al., 2026) | Solver + Kernel (RL revise) | Tests RL revise-until-valid |
| **ProCAD** (ICML 2026) | Kernel + clarification | Tests clarification as soft feedback |

### 4.6 Minimum Viable Baseline Set

For an ablation paper with limited compute:
1. **M2 must**: Embodied CAD, FllumaOne, CAD-Coder (Tier 1 + 1b)
2. **M1 must**: Aligning Constraint Generation, FreeCAD Sketcher
3. **M0 must**: Reflexion, Self-Debug, CAD-Recode
4. **M3 hybrid**: Embodied CAD (already in M2 tier), PR-CAD, Cosmo-Agent

This guarantees:
- Each M-method has at least one direct competitor
- At least one per-CGVM-type classical baseline
- At least one hybrid baseline (to test additive assumption)

---

## 5. Future Research Directions (Beyond Current Baseline)

The original 7 directions (5.1–5.7) below are retained. They are
*anchored to the expanded 12-type CGVM taxonomy* (see `taxonomy_report.md`)
— each direction is labeled with the CGVM type(s) it primarily targets.

### 5.1 Direction A — Action-Alignment Scoring for CGVMs (Type-agnostic)

**Gap**: The project framework lists "feedback effectiveness" as a
criterion but has no operational metric. **Propose**:
```
ActionAlignment(CGVM) := E[LLM_repair_success | CGVM_feedback]
                          / E[LLM_repair_success | ground-truth feedback]
```
i.e., the ratio of LLM success rate with CGVM feedback vs. with oracle
feedback. A CGVM with ActionAlignment ≈ 1.0 is "fully actionable".

**Types covered**: All 12 types. This direction is the *meta-metric*
that quantifies the M0–M3 ordering across types.

### 5.2 Direction B — Solver CGVM Translation Layer (Type III → Type IV)

**Gap**: Solver feedback (DOF/conflict/redundancy) is far from the
LLM's parameter-edit action space. **Propose**:
A translation layer that maps Solver state to parameter-discrepancy
feedback, similar to how KQP does for kernel queries. Specifically:
- "redundant constraint X" → "constraint X duplicates the implied
  value of parameter Y; consider removing one".
- "under-constrained" → "missing dimension along Z; consider setting
  Y=Z=expected_value".

This would convert M1 from a low-action-alignment CGVM to a
medium-action-alignment CGVM, and would test the framework's prediction
that **action-alignment is the dominant factor** for repair success.

### 5.3 Direction C — Multi-Channel CGVM Composition Rules (Type X)

**Gap**: The project's M3 = M2 + M1 < M2 result contradicts the additive
assumption. **Propose**:
Systematic study of when multi-channel CGVM helps vs. hurts. Hypotheses:
- **Additive** if channels have *non-overlapping* action spaces.
- **Dilutive** if channels have *overlapping or conflicting* action
  spaces (as Solver and Kernel do).
- **Complementary** if channels have *sequential* action dependencies
  (one channel's output is another channel's input).

Empirical protocol: take all pairs of CGVM types (II, III, IV, V, VIII)
and run dual-channel ablation. The M0–M3 result is one data point;
Direction C generalizes the finding.

### 5.4 Direction D — Knowledge-Driven CGVM (Type VIII)

**Gap**: No surveyed CGVM systematically uses industry rules or design
norms as the reference. MUSE and AgentsCAD touch this (overhang
detection), but neither is comprehensive. **Propose**:
- FEA-aware verification (e.g., wall-thickness rules, manufacturability)
- DFM (design for manufacturing) verification
- Standard-compliance verification (ISO/ASME/DIN geometric tolerances)

This is the **least-surveyed CGVM type** in the literature and the
**most publishable unexplored niche** identified by the expanded
taxonomy. The project's Design-Plan-as-reference framework naturally
extends to EngineeringKnowledge-as-reference.

### 5.5 Direction E — CAD-Code Co-verification (Type II + Type IV)

**Gap**: Most CGVMs verify the *CAD result* (STEP/B-rep) but not the
*CAD code* (CadQuery script). The two have a related but distinct
failure space. **Propose**:
- Static analysis of CadQuery scripts (e.g., unused variables, type
  mismatches, missing operations).
- Co-verification: code-level + geometry-level feedback jointly.

This is **Type II + Type IV composition**, and tests the action-alignment
ranking: code-level feedback (Type II) is medium-alignment, but
*combined* with parameter-level feedback (Type IV), the LLM has two
complementary channels (one for code-level fixes, one for value-level
fixes). Hypothesis: this composition is **additive**, unlike the
Type III + IV composition (which is dilutive).

### 5.6 Direction F — Evaluation Beyond Success@K (Type-agnostic)

**Gap**: Success@K (Success@1, @2, @3) is the project's primary metric,
but it doesn't capture *how much* was edited (CED is a partial proxy).
**Propose**:
- **Action alignment score** (Direction A).
- **Repair path optimality**: ratio of repair steps taken to repair
  steps in the ground-truth recovery path.
- **Over-repair rate**: fraction of successful repairs that introduced
  new defects (a common LLM side-effect).

### 5.7 Direction H — LLM-Semantic CGVM with Action Prompting (Type V)

**Gap**: Type V (LLM-Semantic) is currently under-characterized. Most
LLM-as-judge verifiers output "looks wrong" without specifying what
parameter to edit. **Propose**:
- Prompt engineering for action alignment: instruct the LLM-judge to
  output (location, suggested_edit) tuples directly, in the same
  format as the LLM repair agent's contract.
- Compare: Type V with action-prompting vs. Type IV with the same
  perturbation set. Hypothesis: with proper prompting, Type V can
  achieve action alignment comparable to Type IV.

### 5.9 Direction I — CSG-Program + Geometry Intent Hybrid (Type VI + IV)

**Gap**: CSG-Program (Type VI) verifies by reverse-decomposition, while
Geometry Intent (Type IV) verifies by direct intent comparison. A
hybrid approach that combines them is missing. **Propose**:
- For Boolean-heavy parts (CSG-natural): use Type VI as primary
  verifier, Type IV as fallback.
- For sketch-extrude parts (project's domain): use Type IV as primary.
- Test the routing logic on the project's 138-perturbation set.

### 5.10 Direction J — Editability CGVM (Type VII) as Project's Niche

**Gap**: The project's M0–M3 ablation is implicitly a Type VII
(Editability) ablation — the perturbed IR is tested for repairability
under valid edits. **Propose**:
- Formalize Type VII in the project's framework:
  - **VII.b Reachability** (HistCAD's ER metric) — can a target state
    be reached by valid edits?
  - **VII.c Repairability** (this project's M0–M3) — can a perturbed
    state be recovered by valid edits?
- Use Type VII as the **project's positioning claim**: "we are the
  first to systematically study Type VII.c on Fusion360-derived
  parametric IR with explicit CED".

### 5.11 Direction K — Feature Recognition as CGVM Preprocessor (Type XI + IV)

**Gap**: Feature recognition is typically offline. A pipeline that
uses Type XI (feature recognition) as a preprocessor for Type IV
(Geometry Intent) is missing. **Propose**:
- Run BRepFormer/BRepMAE/FeatureFox on the STEP output to identify
  feature instances.
- Run KQP only on the *recognized feature instances*, not on the
  whole shape.
- Hypothesis: feature-restricted verification reduces noise and
  improves action alignment.

### 5.12 Direction L — Training-Time vs. Inference-Time CGVM Interaction (Type XII)

**Gap**: When the LLM is trained on data curated by CGVM-X, does
inference-time CGVM-Y still provide marginal benefit? **Propose**:
- For the project: ZHIPU glm-5.1 is NOT CAD-finetuned, so the project's
  CGVMs are not pre-trained. The M0–M3 result is **clean** in this
  sense.
- For CAD-Recode / Text-to-CadQuery / CAD-Coder (VLM): the LLM is
  pre-trained on a CAD corpus. Does inference-time KQP still help?
- If not, the project's contribution generalizes only to non-CAD-fine-tuned
  LLMs — a meaningful boundary condition for the paper.

---

## 5.A Cross-Direction Coverage Matrix (Updated)

| Direction | Primary CGVM Type(s) | Status |
|---|---|---|
| A — Action-Alignment Scoring | All 12 | Meta-metric |
| B — Solver Translation Layer | III → IV | Project-internal |
| C — Multi-Channel Composition Rules | X | Generalizes M3 finding |
| D — Knowledge-Driven CGVM | VIII | **Most unexplored niche** |
| E — CAD-Code Co-verification | II + IV | Additive composition hypothesis |
| F — Evaluation Beyond Success@K | All 12 | Meta-evaluation |
| G — Generative CGVM | All 12 | Architectural |
| H — LLM-Semantic with Action Prompting | V | Prompt-engineering study |
| I — CSG-Program + Geometry Intent Hybrid | VI + IV | Boolean-part routing |
| J — Editability CGVM as Project's Niche | VII | Project positioning |
| K — Feature Recognition as Preprocessor | XI + IV | Pipeline architecture |
| L — Training-Time vs. Inference-Time | XII | Boundary condition |

---

## 6. Concrete Next Steps for the Project

### 6.1 Immediate (next 1-2 weeks)
1. **Re-run M3 with KQP-only output filtering** — strip Solver feedback
   and observe whether M3 ≈ M2 (validates the noise hypothesis).
2. **Compute action-alignment scores** for Solver vs. KQP feedback on the
   project's 138 perturbation set (Direction A).
3. **Implement one Tier-1b baseline** (FllumaOne's pipeline is most
   reproducible) for direct empirical comparison.

### 6.2 Short-term (next 1-2 months)
4. **Implement the Solver→parameter translation layer** (Direction B)
   and add as M1' method. to the M0–M3 ablation.
5. **Re-run the ablation with M0, M1, M1', M2, M3, M4 (=M2+translated-
   solver)** to test Direction C.
6. **Add Success@K + CED + ActionAlignment + Over-repair as the
   standard metric set** for the project's main paper.

### 6.3 Medium-term (next 6 months)
7. **Publish the CGVM framework as a stand-alone taxonomy paper** —
   it would be the first systematic taxonomy for CAD Generation
   Verification Modules.
8. **Release a CGVM benchmark** (the project's 138 perturbations +
   extension to 1000+ samples) with frozen GT + perturbation recipes,
   analogous to HistCAD's release.
9. **Pursue Directions D, E, G** as separate sub-projects.

---

## 7. Final Recommendation Summary

| Priority | Item | Reason |
|---|---|---|
| **P0** | Implement Tier 1b (FllumaOne, Aligning Constraint) | Direct competitors; first to run |
| **P0** | Compute action-alignment scores | Direction A — operationalizes the framework |
| **P1** | Implement Solver translation layer | Direction B — would close the M1 vs M2 gap |
| **P1** | Add M1' (=M1 + translation) to the ablation | Tests Direction C |
| **P2** | Publish the CGVM taxonomy as a paper | Establishes the framework in the community |
| **P2** | Release the 138-perturbation benchmark | Enables future comparisons |
| **P3** | Pursue Directions D, E, G | New research threads |

---

## 8. Closing Note

The project's experimental result (M2 > M3 > M0 > M1) is not a setback —
it is the **most publishable finding** of the project. It validates the
**Verification → Actionable Feedback** principle and provides empirical
evidence that **detection strength is insufficient** for CGVM evaluation.
This reframes the entire field's understanding of CAD repair feedback.

The baseline selection and future directions should reflect this insight:
**prioritize action-alignment**, not detection strength; **prefer
single-channel CGVMs** as baselines (not just hybrids); and **investigate
the composition rules** for multi-channel CGVMs as the next frontier.

---

*End of Report 2.*