# Baseline Survey — Index

> **Project**: 子课题1 — Solver-Kernel 双反馈闭环驱动的 CAD 生成质量提升研究
> **Date**: 2026-08-02
> **Scope**: Baseline identification for M0–M3 ablation. Survey only, no reproduction.

---

## Files in this directory

| File | Purpose |
|---|---|
| `analysis_model.md` | 10-dimension rubric applied uniformly to every candidate baseline |
| `final_report.md` | **Main survey** — ~95 works, executive summary + per-category findings + coverage matrix + recommendations |
| `taxonomy_report.md` | **Report 1** — All ~95 works reorganized under the CAD Generation Verification Module (CGVM) framework |
| `baseline_and_direction.md` | **Report 2** — Baseline selection (action-alignment principle) + future research directions |
| `survey_c1_oneshot_cad.md` | Category C1 — One-shot text/spec → CAD code generation (M0 analog) |
| `survey_c2_iterative_codegen.md` | Category C2 — Iterative / self-reflective code generation (M0+reflection) |
| `survey_c3_neurosymbolic.md` | Category C3 — Constraint-solver / symbolic-reasoning–guided LLM (M1 analog) |
| `survey_c4_kernel_query.md` | Category C4 — Geometric verification / kernel query / B-rep validity (M2 analog) — 25+ works |
| `survey_c5_cad_llm_agents.md` | Category C5 — CAD-domain LLM agents (M2/M3) |
| `survey_c6_cad_repair.md` | Category C6 — CAD repair / B-rep editing / constraint satisfaction (M3) |

---

## Headline conclusions

1. **~95 candidate baselines** surveyed across 6 categories.
2. **No prior work implements the exact project recipe**: solver + KQP
   dual-feedback repair on perturbed Fusion360-derived CAD IR with
   Success@3 + CED.
3. **Closest published M3 competitors**:
   - Embodied CAD (solver-grounded, generation)
   - GenCAD-Self-Repairing (single-channel feasibility repair, **66%** success)
   - CADReasoner (iterative geometric-mismatch repair)
   - CAD-Coder (GRPO + geometric reward)
   - Cosmo-Agent (RL revise-until-valid)
4. **Closest published M2 competitors** (C4 retry surfaced):
   - **FllumaOne** — 99.14% STEP-export validity; most explicit
     kernel-validator-in-loop pipeline
   - **HoLa** — 82% B-rep validity (canonical benchmark)
   - **CMT** — +10.68% Coverage, +10.3% Valid ratio on ABC
   - **STEP-LLM** — RL with Chamfer Distance reward
   - **Aligning Constraint Generation** (Autodesk) — 93% fully-constrained
     via DPO + constraint-solver feedback
5. **Classical open-source floors** that any LLM-based repair must beat:
   - OpenCASCADE `ShapeFix_*` + `BRepCheck_*`
   - FreeCAD Sketcher (GCS) with DoF diagnostics
6. **Expanded CGVM taxonomy** (12 types, 5 dimensions) — see `taxonomy_report.md`:
   - Original 4 types: Visual / Execution / Solver / Geometry Intent
   - **8 new types** from the literature: LLM-Semantic / CSG-Program /
     Editability / Knowledge-Driven / Implicit-Field / Multi-Modal
     Hybrid / Pre-Execution Feature Recognition / Training-Time
   - **5 orthogonal dimensions**: Reference / Match mechanism / Timing /
     Action alignment / Granularity
7. **Recommended baseline execution set** (priority order):
   - Tier 1 (M3 competitors): Embodied CAD, GenCAD-Self-Repairing, CAD-Coder
   - Tier 1b (M2 from C4 retry): FllumaOne, CADReasoner, STEP-LLM, Aligning Constraint
   - Tier 2 (Domain code agents): CAD-Recode, CAD-Editor, CAD-MLLM, Text-to-CadQuery
   - Tier 3 (Classical floor + validity benchmark): OCCT ShapeFix, FreeCAD Sketcher, HoLa, BRepFormer/MAE
   - Tier 4 (Reflection baselines): Reflexion, Self-Debug
   - Tier 5 (Diagnostic only): GenCAD, Text2CAD
   - Tier 6 (RL revise): Cosmo-Agent, PR-CAD, Zero-to-CAD
8. **Future research directions** (12 directions, see `baseline_and_direction.md`):
   - A — Action-Alignment Scoring
   - B — Solver Translation Layer (M1 → M2-equivalent)
   - C — Multi-Channel Composition Rules (generalizes M3 finding)
   - D — Knowledge-Driven CGVM (most unexplored niche)
   - E — CAD-Code Co-verification (Type II + IV additive)
   - F — Evaluation Beyond Success@K
   - G — Generative CGVM (CGVM-as-Generator)
   - H — LLM-Semantic with Action Prompting
   - I — CSG-Program + Geometry Intent Hybrid
   - J — Editability CGVM as Project's Niche
   - K — Feature Recognition as Preprocessor (Type XI + IV)
   - L — Training-Time vs. Inference-Time Interaction (Type XII)

---

## How to read the surveys

- Each `survey_c*.md` is structured as: works surveyed (with full
  bibliographic info + arXiv URL + result), coverage summary.
- Each work is evaluated against the 10 dimensions in `analysis_model.md`,
  with a "Mapping to M0–M3" assignment.
- All URLs are absolute arXiv links (or Nature DOIs / project pages /
  GitHub where the work is not on arXiv).
- Where exact numerical results are available, they are reported verbatim.
  Where only abstract-level claims exist, that is explicitly flagged.

---

## Coverage matrix

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        Baseline Coverage Audit                             │
├────────────────────────────────────────────────────────────────────────────┤
│  All candidate baselines covered?            Y  (~95 works across C1-C6)   │
│  Each M0–M3 analog has ≥1 candidate?         Y                             │
│    M0 (no feedback)                          Y (Text2CAD, CAD-Recode, …)   │
│    M0+reflection                             Y (Reflexion, Self-Refine, …) │
│    M1 (solver feedback)                      Y (LLM+P, LeanDojo, …)        │
│    M2 (KQP / geometric feedback)             Y (OCCT, FreeCAD, HoLa,       │
│                                                 FllumaOne, CAD-Coder, …)   │
│    M3 (dual feedback)                        PARTIAL (no exact prior work) │
│  Public benchmarks present?                  Y (HumanEval, SWE-bench,     │
│                                                   DeepCAD, ABC, Fusion360, │
│                                                   mmABC, Omni-CAD)          │
│  At least one SOTA comparison per category?  Y (see §9.1 + §6.6 tables)   │
│  At least 3 pre-LLM classical CAD works?     Y (OCCT, FreeCAD, CSGNet)     │
│  At least 5 LLM-era CAD/code-agent works?    Y (Embodied, CAD-Coder,       │
│                                                   CADFusion, ProCAD, …)    │
│  Closest M3 competitor documented?           Y (Embodied CAD, GenCAD-SR,   │
│                                                 Cosmo-Agent, PR-CAD)       │
│  Headline numerical benchmarks gathered?     Y (HoLa 82% B-rep validity,   │
│                                                 FllumaOne 99.14% STEP,     │
│                                                 GenCAD-SR 66% infeasible→   │
│                                                 feasible, Constraint-Align  │
│                                                 93% fully-constrained,      │
│                                                 CMT +10.68% Coverage)       │
│  Works organized under CGVM framework?       Y (~95 in taxonomy_report)    │
│  Action-alignment analysis for baselines?    Y (in baseline_and_direction) │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Status

- **Project understood**: ✅
- **Analysis model built**: ✅
- **C1 surveyed**: ✅ (15 works)
- **C2 surveyed**: ✅ (17 works)
- **C3 surveyed**: ✅ (7 works + 1 pattern class)
- **C4 surveyed**: ✅ (9 works + 5 commercial tools, partial data from
  failed agent run; supplemented with direct OCCT/BRepFormer fetches)
- **C5 surveyed**: ✅ (20 works)
- **C6 surveyed**: ✅ (16 works + 4 datasets)
- **Coverage matrix built**: ✅
- **Recommendations provided**: ✅

---

## Limitations of this survey

1. **Abstract-only verification for many works.** Where the arXiv page did
   not include numerical results (most do not on their abstract pages),
   only abstract-level claims are reported. PDF/HTML bodies would be
   required for exact tables.

2. **No prior work implements the project's exact recipe.** This is
   framed as the project's contribution gap, not a survey failure.

3. **Commercial B-rep repair tools** cannot be benchmarked directly:
   they are proprietary and lack published success-rate numbers.

4. **The C4 (kernel-query) category** had one agent run fail; data was
   recovered via direct fetches of OCCT documentation and the BRepFormer
   arXiv page. Some neural-verifier-in-the-loop works (GIFT, CAD-Coder,
   CADFusion) are also covered in C5.
