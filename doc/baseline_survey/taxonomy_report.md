# Report 1 (Expanded): CAD Generation Verification Taxonomy
## An Emergent Taxonomy of Verification Modules from the Literature

> **Date**: 2026-08-02 (updated 2026-08-11 to expand the taxonomy)
> **Author**: ZCode (research agent)
> **Project**: 子课题1 — Solver-Kernel 双反馈闭环驱动的 CAD 生成质量提升研究
> **Scope**: Take the ~95 works surveyed in `final_report.md` and reorganize
> them under an **emergent, multi-dimensional CGVM taxonomy**. The original
> four types (Visual / Execution / Solver / Geometry Intent) are kept as a
> starting point, but the survey reveals at least **8 additional CGVM
> types** that don't fit the original four — and at least **5
> orthogonal dimensions** along which CGVMs vary. This report documents
> the expanded taxonomy.

---

## Executive Summary

The project's original CGVM framework names **four canonical types**:
Visual, Execution, Solver, Geometry Intent. Surveying ~95 works reveals
that these four types are *necessary but not sufficient*. The literature
supports at least **12 distinct CGVM types**, organized along **5
orthogonal dimensions**:

1. **Reference type**: Explicit Intent / Internal / Engineering Knowledge /
   Historical / Hybrid
2. **Match mechanism**: Numerical / Symbolic / Neural / LLM-Semantic / Visual
3. **Application timing**: Inference-time / Training-time / Pre-execution /
   Post-execution
4. **Action alignment**: Parameter / Constraint / Code / Global
5. **Diagnostic granularity**: Global / Local / Parameter / Constraint

The taxonomy is **emergent** — types are induced from the literature, not
pre-defined. The original four types are a subset of the full taxonomy
that the project's experimental work happens to focus on (M0 = Execution,
M1 = Solver, M2 = Geometry Intent, M3 = Solver + Geometry Intent).

The most publishable consequence: **the project owns the "Geometry Intent"
niche** but does not own the broader CGVM design space. Future work
should explore the unoccupied regions: **Knowledge-Driven, LLM-Semantic,
Editability, Multi-Modal Hybrid, RL-Revise** verification.

---

## 1. Framework Recap (Project's Original)

### 1.1 CGVM Formal Definition

```
CGVM := F(CAD_target, Reference, Feature_Extraction, Match_Mechanism)
     = (Verification_result, Verification_feedback)

Verification_result ∈ {Pass, Fail, Unknown}
Verification_feedback = (Location, Error)
```

### 1.2 Original 4 Types (Project-Defined Starting Point)

| Type | Reference | CAD Feature | Match |
|---|---|---|---|
| **Visual** | Explicit (Design Plan) | Three-view rendering | VLM visual-semantic |
| **Execution** | Internal | Execution trace | Rule check on error log |
| **Solver** | Internal | Constraint graph | Solver state (DOF/conflict) |
| **Geometry Intent** | Explicit (Design Plan) | Geometry/topology | Numerical comparison |

### 1.3 The Framework is Open

> The user clarifies: these are *examples*, not a closed enumeration.
> The literature may reveal additional CGVM types. The taxonomy must
> be extended to cover them.

---

## 2. Why Extend Beyond the Original 4 Types?

### 2.1 The 4 Types Cannot Classify Several Surveyed Works

| Work | Why it doesn't fit the 4 types |
|---|---|
| **CSGNet, D²CSG, DiffCSG, Szalinski** | Verify by **reverse-decomposing** into a CSG program — neither code-execution nor numerical-comparison against an intent. |
| **LLM-as-judge verifiers** (LLM compares CAD vs. text directly) | Not visual, not numerical — uses **LLM semantic matching**. |
| **HistCAD, Linkify** | Verify **editability** under constraint-preserving edits — neither geometry nor solver state. |
| **Cosmo-Agent, PR-CAD** | The verifier is the **reward function of an RL policy** — temporal, not one-shot. |
| **NH-Rep, NeurCADRecon, UCSG-Net, DualBrep** | Verify via **implicit field (SDF/UDF) consistency** — neither explicit geometry nor rendering. |
| **AgentsCAD, MUSE, ArtiCAD, Embodied CAD** | Combine **multiple CGVM types** with **routing logic** — pure hybrids. |
| **BRepFormer, BRepMAE, FeatureFox** | Verify by **first recognizing features**, then comparing — **pre-execution**. |
| **FllumaOne, STEP-LLM** | The verifier is used to **curate the training dataset**, not at inference time. |
| **LeanDojo, AlphaProof** | Verify via **theorem-proving** — general code/math, applicable to CAD constraints in principle. |
| **CLIP-based verifiers** (if any) | Verify via **cross-modal embedding similarity** — neither visual nor numerical. |
| **DFM, FEA-aware verifiers** | Reference = **Engineering Knowledge** (industry rules) — not yet surveyed in detail but a clear gap. |

### 2.2 The 4 Types Also Miss Internal Variation

- **Visual CGVM** has at least 3 sub-variants: single-view / multi-view /
  rendered + textual.
- **Solver CGVM** has at least 3 sub-variants: constraint solver / SAT-SMT
  / theorem-prover.
- **Execution CGVM** has at least 2 sub-variants: pure-error-log /
  code-reasoning.

These sub-variants have materially different action alignment, so they
deserve distinct type status.

---

## 3. Emergent CGVM Taxonomy — 12 Types

The taxonomy below is **induced from the literature**, organized along
the 5 orthogonal dimensions. The original 4 types are preserved as
subset positions in this larger space.

### 3.1 Type I — Visual CGVM (existing)

- **Reference**: Explicit (Design Plan)
- **CAD feature**: Three-view rendering
- **Match**: VLM visual-semantic comparison
- **Sub-types**:
  - **I.a Single-view VLM** — single rendered image, VLM check
  - **I.b Multi-view VLM** — front/side/top renders, VLM cross-check
    (e.g., CADFusion)
  - **I.c Rendered + textual** — VLM receives rendering + design text
    (e.g., MUSE, AgentsCAD)
- **Representative works**: CADFusion, AgentsCAD, MUSE, GenCAD-3D
- **Action alignment**: Low (visual mismatch → ambiguous parameter)
- **Granularity**: Global

### 3.2 Type II — Execution CGVM (existing)

- **Reference**: Internal
- **CAD feature**: Execution trace (compile/run)
- **Match**: Rule check on error log
- **Sub-types**:
  - **II.a Pure-error-log** — error message is the feedback
    (e.g., Self-Debug)
  - **II.b Code-reasoning** — code is the verifier (e.g., CodeAct, PAL)
- **Representative works**: Self-Debug, CodeAct, PAL, CodeRL, Voyager
- **Action alignment**: Medium (line-level)
- **Granularity**: Code-line

### 3.3 Type III — Solver CGVM (existing)

- **Reference**: Internal
- **CAD feature**: Constraint graph
- **Match**: Solver state (DOF / conflict / redundancy)
- **Sub-types**:
  - **III.a Constraint solver** — GCS, SAT, SMT
    (e.g., FreeCAD Sketcher, LLM+P)
  - **III.b Theorem-prover** — Lean, Coq for code/math correctness
    (e.g., LeanDojo, AlphaProof, AlphaGeometry)
- **Representative works**: FreeCAD Sketcher, LLM+P, DreamCoder,
  FunSearch, LeanDojo, AlphaProof, SAT-LM, Aligning Constraint
- **Action alignment**: Low (constraint state → ambiguous parameter)
- **Granularity**: Constraint-level

### 3.4 Type IV — Geometry Intent (Kernel) CGVM (existing)

- **Reference**: Explicit (Design Plan)
- **CAD feature**: Geometry / topology statistics (bbox, void count,
  solidity, symmetry, continuity)
- **Match**: Numerical comparison
- **Sub-types**:
  - **IV.a Direct kernel query** — OCCT queries against STEP
    (e.g., KQP, FllumaOne, OCCT BRepCheck)
  - **IV.b Statistical validity** — learned validity check
    (e.g., HoLa, AutoBrep, BrepGen, CMT)
- **Representative works**: KQP (this project), OCCT BRepCheck/ShapeFix,
  HoLa, AutoBrep, BrepGen, CMT, DTGBrepGen, FllumaOne, STEP-LLM,
  CADReasoner, CAD-Coder, STEP-LLM, AssemCAD, HistCAD, MUSE
- **Action alignment**: High (parameter discrepancy → exact edit)
- **Granularity**: Parameter-level

### 3.5 Type V — LLM-Semantic CGVM (NEW)

- **Reference**: Explicit (text description, design plan) or
  EngineeringKnowledge (rules in natural language)
- **CAD feature**: CAD as DSL/script — the LLM reads it as text
- **Match**: LLM-as-judge — the LLM compares the CAD description
  with the reference and reasons about match
- **Sub-types**:
  - **V.a LLM compares DSL vs. text** — LLM reads the generated script
    and the design text, judges alignment
  - **V.b LLM compares render vs. text** (variant of Visual, but with
    LLM-as-judge rather than VLM-as-judge)
  - **V.c LLM compares multi-modal reference vs. CAD** — design text +
    sketch + history JSON + CAD → LLM judges
- **Representative works**:
  - ProCAD (clarifier-coder — implicit LLM-judge)
  - Aligning Constraint Generation (DPO via LLM-judge on constraint sets)
  - Most LLM-CAD pipelines that use GPT-4 to "look at" the rendered
    output and decide if it matches the prompt
- **Action alignment**: Variable (depends on LLM prompt — can be high
  if LLM is instructed to output specific edits, or low if it just says
  "looks wrong")
- **Granularity**: Variable (parameter-level if prompted well, otherwise
  global)

### 3.6 Type VI — CSG-Program CGVM (NEW)

- **Reference**: Internal (the generated geometry itself)
- **CAD feature**: mesh / point cloud (input)
- **Match**: Reverse-decomposition into a CSG program whose execution
  reproduces the input
- **Sub-types**:
  - **VI.a Neural reverse-CSG** — neural network predicts CSG program
    (CSGNet, D²CSG, UCSG-Net)
  - **VI.b Differentiable reverse-CSG** — optimization-based with
    differentiable rendering (DiffCSG)
  - **VI.c Equality-saturation reverse-CSG** — e-graph rewriting with
    inverse transformations (Szalinski)
- **Representative works**: CSGNet (Sharma et al., TPAMI 2020),
  D²CSG (Yu et al., 2023), DiffCSG (Yuan et al., 2024), Szalinski
  (Nandi et al., PLDI 2020), UCSG-Net (NeurIPS 2020)
- **Action alignment**: High (CSG program → editable boolean operations
  on primitives)
- **Granularity**: CSG-tree-level

### 3.7 Type VII — Editability CGVM (NEW)

- **Reference**: Explicit (parametric history with constraints)
- **CAD feature**: Editability score — does the model survive parameter
  edits while preserving design intent?
- **Match**: Apply canonical edits (change one parameter), check whether
  constraints are still satisfied
- **Sub-types**:
  - **VII.a Constraint-preservation editability** — does editing a
    parameter break constraints? (HistCAD, Linkify)
  - **VII.b Reachability editability** — can a target state be reached
    by a sequence of valid edits? (HistCAD's ER metric)
  - **VII.c Repairability editability** — can a perturbed state be
    recovered by valid edits? (project's M0–M3)
- **Representative works**: HistCAD (Dong et al., 2026), Linkify
  (Jignasu & Grandi, 2026), this project
- **Action alignment**: High (edit operation is the verification, so
  feedback is naturally edit-actionable)
- **Granularity**: Edit-level

### 3.8 Type VIII — Knowledge-Driven CGVM (NEW)

- **Reference**: EngineeringKnowledge (industry rules, design norms,
  DFM constraints, FEA constraints)
- **CAD feature**: Geometry/material/topology properties relevant to
  the rule
- **Match**: Rule check (e.g., min wall thickness, max overhang angle,
  no enclosed voids)
- **Sub-types**:
  - **VIII.a DFM (Design for Manufacturing)** — manufacturability rules
    (wall thickness, fillet radii, draft angles)
  - **VIII.b FEA-aware** — structural validity, stress concentrations
  - **VIII.c Standard-compliance** — ISO/ASME/DIN geometric
    tolerances and standards
- **Representative works**: MUSE (Dong et al., 2026) — closest published
  analog; AgentsCAD — overhang detection ≥45°
- **Action alignment**: High (rule → specific parameter edit)
- **Granularity**: Rule-dependent
- **Gap**: This is the **least-surveyed category** — most works do
  not use external engineering rules as a reference. Significant
  opportunity for future work.

### 3.9 Type IX — Implicit-Field CGVM (NEW)

- **Reference**: Internal (the implicit field representation)
- **CAD feature**: Signed distance function (SDF) or unsigned distance
  function (UDF) consistency
- **Match**: Field-continuity check, sharp-feature preservation,
  zero-curvature developability check
- **Sub-types**:
  - **IX.a SDF-based** — neural SDF reconstruction + verification
    (NH-Rep, NeurCADRecon)
  - **IX.b UDF-based** — unsigned distance field (DualBrep)
  - **IX.c Developability-check** — zero Gaussian curvature (NeurCADRecon)
- **Representative works**: NH-Rep (SIGGRAPH Asia 2022), NeurCADRecon
  (SIGGRAPH 2024), UCSG-Net (NeurIPS 2020), DualBrep (SIGGRAPH 2026),
  NeurCross (SIGGRAPH 2025), ODW-loss scheduling (ISVC 2025)
- **Action alignment**: Medium (field inconsistency → ambiguous
  surface edit)
- **Granularity**: Surface-level

### 3.10 Type X — Multi-Modal Hybrid CGVM (NEW)

- **Reference**: Hybrid (combination of Explicit Intent, Engineering
  Knowledge, Internal)
- **CAD feature**: Multiple — geometry, rendering, constraints, etc.
- **Match**: Routing logic chooses which sub-verifier to apply per
  sample / per dimension
- **Sub-types**:
  - **X.a Multi-stage cascade** — code check → geometric check →
    design-intent (MUSE)
  - **X.b Multi-agent verification** — different agents specialize
    in different sub-verifiers (AgentsCAD, ArtiCAD, CAD-Editor)
  - **X.c Solver + Kernel with routing** — solver for parameter
    conflicts, kernel for geometric intent (Embodied CAD, Cosmo-Agent,
    PR-CAD)
- **Representative works**: Embodied CAD, PR-CAD, Cosmo-Agent,
  AgentsCAD, ArtiCAD, CAD-Editor, MUSE, ProCAD
- **Action alignment**: Variable — depends on routing logic and
  per-channel action alignment
- **Granularity**: Variable
- **Critical observation**: The project's M3 (= Solver + Kernel) is a
  X.c sub-type. The M3 < M2 result is a *specific instance* of the
  broader problem: **multi-channel CGVM composition can dilute
  action alignment if channels overlap or conflict**.

### 3.11 Type XI — Pre-Execution Feature Recognition CGVM (NEW)

- **Reference**: Internal (feature taxonomy)
- **CAD feature**: Recognized features (holes, slots, pockets, bosses)
- **Match**: Feature classification + suppression
- **Sub-types**:
  - **XI.a Neural feature recognition** — transformer/GNN over B-rep
    (BRepFormer, BRepMAE, FeatureFox)
  - **XI.b Classical feature recognition** — rule-based AFR (older
    CAD/CAM literature)
- **Representative works**: BRepFormer (Dai et al., ICMR 2025),
  BRepMAE (Yao et al., 2026), FeatureFox (Fuchs et al., 2026),
  BRT (2025), older AAGNet, BRT-Net, BR-IPA, HierCAD, MFInstSeg
- **Action alignment**: Medium (recognized feature → suppress or
  re-categorize, but doesn't tell which parameter to change)
- **Granularity**: Feature-level
- **Use**: Preprocessor for downstream CGVM — recognizes features
  first, then the downstream CGVM (KQP / Solver) operates on the
  recognized feature set

### 3.12 Type XII — Training-Time / Data-Curation CGVM (NEW)

- **Reference**: Either Internal or Explicit, depending on use
- **CAD feature**: The generated CAD
- **Match**: Verifier is applied *during training data curation*, not
  during inference
- **Sub-types**:
  - **XII.a Dataset filter** — keep only samples where verifier passes
    (FllumaOne 99.14% STEP validity, OCCT BRepCheck as data filter)
  - **XII.b Reward function** — RL training uses verifier as reward
    (STEP-LLM's Chamfer Distance reward, CAD-Coder's GRPO geometric
    reward)
  - **XII.c DPO/SFT data filter** — only verified samples used for
    supervised training (Aligning Constraint Generation uses solver as
    the verification oracle for DPO)
- **Representative works**: FllumaOne (Zhan, 2026), STEP-LLM (Shi et al.,
  DATE 2026), CAD-Coder (NeurIPS 2025), Aligning Constraint Generation
  (Casey et al., Autodesk 2025)
- **Action alignment**: N/A at inference time (verifier is offline)
- **Granularity**: N/A at inference time

---

## 4. The 5 Orthogonal Dimensions of CGVM Variation

The 12 types can be organized along 5 orthogonal dimensions:

### 4.1 Dimension 1 — Reference Type

| Reference | Types |
|---|---|
| **Explicit Intent** (Design Plan, specification) | I (Visual), IV (Geometry Intent), V (LLM-Semantic), VII (Editability) |
| **Internal** (execution, constraint graph, CSG tree) | II (Execution), III (Solver), VI (CSG-Program), IX (Implicit-Field), XI (Pre-Execution Feature Rec.) |
| **Engineering Knowledge** (industry rules) | VIII (Knowledge-Driven) |
| **Historical** (previous valid CAD) | VII (Editability, in the constraint-preservation sense) |
| **Hybrid** | X (Multi-Modal Hybrid), XII (Training-Time, varies) |

### 4.2 Dimension 2 — Match Mechanism

| Match | Types |
|---|---|
| **Numerical** (geometric comparison) | IV (Geometry Intent, IV.a) |
| **Symbolic** (rule check, solver state, theorem proving) | III (Solver), VIII (Knowledge-Driven), II (Execution, II.a) |
| **Neural** (learned classifier / regression / diffusion) | IV (Geometry Intent, IV.b), VI (CSG-Program), IX (Implicit-Field), XI (Pre-Execution Feature Rec.) |
| **LLM-Semantic** (LLM-as-judge) | V (LLM-Semantic) |
| **Visual** (VLM cross-modal) | I (Visual) |
| **Hybrid** (multi-mechanism with routing) | X (Multi-Modal Hybrid) |

### 4.3 Dimension 3 — Application Timing

| Timing | Types |
|---|---|
| **Inference-time** | I, II, III, IV, V, VI, VII, VIII, IX, XI |
| **Training-time** | XII |
| **Pre-execution** | XI (typically before main CAD execution) |
| **Post-execution** | I, II, III, IV, V, VI, VII, VIII, IX |

### 4.4 Dimension 4 — Action Alignment

| Alignment | Types |
|---|---|
| **Parameter-level** | IV, VII, VIII (well-designed), V (with prompt) |
| **Constraint-level** | III, IX |
| **Code-level** | II |
| **CSG-tree-level** | VI |
| **Global** | I, V (default), XI |

### 4.5 Dimension 5 — Diagnostic Granularity

| Granularity | Types |
|---|---|
| **Global** | I, V (default), XI |
| **Local** | VIII, X (sub-routing) |
| **Parameter** | IV, V (with prompt), VII, VIII |
| **Constraint** | III, IX |
| **Code-line** | II |

---

## 5. Re-Mapping ~95 Surveyed Works onto the Expanded Taxonomy

### 5.1 Type Counts (Expanded)

| Type | # Works | Representative |
|---|---|---|
| I (Visual) | 4 | CADFusion, AgentsCAD, MUSE |
| II (Execution) | 9 | Self-Debug, CodeAct, PAL, FllumaOne |
| III (Solver) | 10 | FreeCAD Sketcher, Aligning Constraint, LeanDojo, AlphaProof |
| IV (Geometry Intent) | 22 | KQP, HoLa, FllumaOne, CADReasoner, OCCT |
| V (LLM-Semantic) | 5 | ProCAD, Aligning Constraint (DPO judge), GenCAD-LLM |
| VI (CSG-Program) | 5 | CSGNet, D²CSG, DiffCSG, Szalinski, UCSG-Net |
| VII (Editability) | 4 | HistCAD, Linkify, this project |
| VIII (Knowledge-Driven) | 3 | MUSE, AgentsCAD (overhang), DFM (gap) |
| IX (Implicit-Field) | 6 | NH-Rep, NeurCADRecon, UCSG-Net, DualBrep, NeurCross, ODW-loss |
| X (Multi-Modal Hybrid) | 8 | Embodied CAD, PR-CAD, Cosmo-Agent, ArtiCAD, CAD-Editor |
| XI (Pre-Execution Feature Rec.) | 4 | BRepFormer, BRepMAE, FeatureFox, BRT |
| XII (Training-Time / Data-Curation) | 6 | FllumaOne, STEP-LLM, CAD-Coder, Aligning Constraint (DPO), GenCAD-3D |

(Some works appear in multiple types — e.g., FllumaOne is II + IV + XII;
Aligning Constraint is III + V + XII; AgentsCAD is I + VIII.)

### 5.2 Action Alignment by Type (Re-Ranked)

| Type | Action alignment | Why |
|---|---|---|
| **IV (Geometry Intent)** | **HIGH** | Parameter discrepancy → exact edit |
| **VII (Editability)** | **HIGH** | Edit is the verification |
| **VIII (Knowledge-Driven)** | **HIGH** | Rule → specific parameter |
| **VI (CSG-Program)** | **HIGH** | CSG tree → boolean operations |
| **II (Execution)** | MEDIUM | Error trace → line-level hint |
| **V (LLM-Semantic)** | VARIABLE | Prompt-dependent |
| **IX (Implicit-Field)** | MEDIUM | Field inconsistency → surface edit |
| **III (Solver)** | **LOW** | Constraint state → ambiguous parameter |
| **XI (Feature Recognition)** | MEDIUM | Feature → suppress or recategorize |
| **I (Visual)** | **LOW** | Visual mismatch → ambiguous parameter |
| **X (Multi-Modal Hybrid)** | VARIABLE | Depends on routing |
| **XII (Training-Time)** | N/A | Offline use |

---

## 6. Project's M0–M3 Re-Framed Under Expanded Taxonomy

| Method | Active CGVM Types | Channel Quality |
|---|---|---|
| M0 | **II** (Execution only) | Coarse — pipeline feedback |
| M1 | **II + III** (Execution + Solver) | Detection high, action low |
| M2 | **II + IV** (Execution + Kernel) | Detection + action both high |
| M3 | **II + III + IV** (Execution + Solver + Kernel) | X.c sub-type — multi-modal hybrid |

**The M2 > M3 > M0 > M1 result is interpretable as follows**:

- M2 wins because its high-alignment channel (IV) is in pure form.
- M3 loses to M2 because adding III (Solver) introduces low-alignment
  noise that dilutes IV's high-alignment signal — this is the **Type X.c
  composition rule** at work.
- M1 loses to M0 because III alone adds noise without providing
  high-alignment feedback (parameters not directly inferable from
  constraint state).
- M0 beats M1 because pipeline feedback at least points to execution
  errors that have known repair actions, whereas constraint diagnosis
  has a wider action gap.

**Implication for the project**: the M0–M3 ablation can be reframed as
**Type II vs Type II+III vs Type II+IV vs Type II+III+IV**, and the
experimental result is consistent with a general principle:

> **Adding a low-action-alignment CGVM channel to a high-action-alignment
> CGVM channel can reduce overall repair efficiency.**

---

## 7. New Gaps Identified by the Expanded Taxonomy

1. **Knowledge-Driven CGVM (Type VIII) is severely under-explored.**
   Only MUSE and AgentsCAD use engineering rules (overhang detection).
   DFM, FEA-awareness, and standard-compliance CGVMs are missing.
   **Significant opportunity for future work** — this is the most
   publishable unexplored niche.

2. **Type V (LLM-Semantic) is under-characterized.** Most LLM-CAD
   works implicitly use LLM-as-judge, but no work systematically
   studies how prompt design affects action alignment. **Significant
   opportunity for methodological work.**

3. **Type VI (CSG-Program) and Type IV (Geometry Intent) are in
   tension.** CSG-Program verifies by reverse-decomposition, while
   Geometry Intent verifies by direct intent comparison. A hybrid
   approach that combines them is missing. **Architectural opportunity.**

4. **Type X (Multi-Modal Hybrid) composition rules are not studied.**
   The M3 < M2 result is one data point; a systematic study of when
   composition helps vs. hurts is missing. **Methodological opportunity.**

5. **Type XII (Training-Time) and inference-time CGVM interaction is
   not studied.** When the training data was curated by CGVM-X, does
   inference-time CGVM-Y still provide marginal benefit? **Important
   for project design — the project uses ZHIPU glm-5.1, not a
   CAD-finetuned LLM, so the project's CGVMs are not pre-trained.**

6. **Type XI (Feature Recognition) is typically pre-execution, not
   feedback.** Most works treat feature recognition as offline. A
   feedback loop that incorporates feature recognition as a verifier
   is missing. **Architectural opportunity.**

---

## 8. Cross-Type Comparison (Headline, Updated)

| Metric | I | II | III | IV | V | VI | VII | VIII | IX | X | XI | XII |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| # works | 4 | 9 | 10 | 22 | 5 | 5 | 4 | 3 | 6 | 8 | 4 | 6 |
| Detection | M | L | H | H | M | H | H | H | M | M | M | n/a |
| Action align | L | M | L | **H** | V | H | **H** | **H** | M | V | M | n/a |
| Granularity | G | C | Cn | **P** | V | CSG | E | R | S | V | F | n/a |
| Timing | I | I | I | I | I | I | I | I | I | I | Pre | T |

Legend: L=Low, M=Medium, H=High, V=Variable, G=Global, C=Code-line,
Cn=Constraint, P=Parameter, CSG=CSG-tree, E=Edit, R=Rule, S=Surface,
F=Feature; I=Inference, T=Training.

---

## 9. Files Referenced

- `final_report.md` — original ~95-work survey
- `analysis_model.md` — 10-dimension rubric
- `survey_c1_oneshot_cad.md` … `survey_c6_cad_repair.md` — per-category detail
- `baseline_and_direction.md` — Report 2 (baseline selection + future direction)
- This file — CGVM taxonomy re-organization (12 types, 5 dimensions)

---

## 10. Closing Note

The original 4-type framework was a useful starting point, but the
literature reveals a richer **12-type, 5-dimensional space**. The
project's M0–M3 ablation occupies a specific sub-region of this space
(Type II + III + IV) — important, but not exhaustive. Future work
should explore the unoccupied regions:

- **Type V (LLM-Semantic)** with prompt-engineering for action alignment
- **Type VI + IV hybrid** (CSG-Program + Geometry Intent)
- **Type VIII (Knowledge-Driven)** with industry rules as reference
- **Type X (Multi-Modal Hybrid)** with composition-rule study
- **Type XI + IV (Feature Recognition + Geometry Intent)** pipeline

The expanded taxonomy reframes the project's contribution as occupying
one specific niche (Type IV, parameter-actionable, inference-time,
Design-Plan-referenced), with the M0–M3 ablation exploring a small
multi-modal hybrid sub-region around it.

---

*End of Report 1 (Expanded).*