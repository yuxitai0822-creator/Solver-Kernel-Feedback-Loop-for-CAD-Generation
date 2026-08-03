# Baseline Analysis Model

> **Purpose**: Define a unified analytical lens to compare candidate baseline
> works against the project's M0–M3 ablation. The lens must be applicable
> to LLM-based CAD generation, code generation, agentic repair, and CAD
> verification works alike.

---

## 1. Reference: this project's core proposition

The project (子课题1) builds a **Constraint-grounded Agentic CAD Generation
Pipeline**:

```
Design Plan v0.6
    │  (task spec, no leakage)
    ▼
[CAD Agent | LLM glm-5.1] ──► CAD IR v0.1 ──► [Adaptor] ──► cadquery script ──► STEP
                                          ▲                     │
                                          │                     ▼
                            ┌─────────────┴──────────────┐ ┌──────────────┐
                            │   Feedback Channels        │ │ Verification │
                            │   • Pipeline               │ │ Pipeline     │
                            │   • Solver (FreeCAD)       │ │              │
                            │   • KQP (geometric intent) │ │              │
                            └────────────────────────────┘ └──────────────┘
                                          │                     │
                                          └───── repair ◄──────┘
```

### 1.1 Core Research Questions

- **RQ1**: Does injecting solver constraint feedback improve CAD repair Success@3?
- **RQ2**: Does injecting KQP geometric-intent feedback improve CAD repair Success@3?
- **RQ3**: Is the dual feedback (M3) better than either single feedback?
- **RQ4 (secondary)**: How does stop-bar strictness affect over-trust?

### 1.2 What makes this project unique (defensible axes)

A baseline is comparable ONLY if it can be positioned on at least one of
these axes:

| Axis | This project | Why it matters for baseline selection |
|---|---|---|
| **A. Input spec** | Design Plan v0.6 (structured JSON: bbox, features, intents) | Different from "raw text description" or "single image" |
| **B. Output** | CAD IR v0.1 → CadQuery script → STEP file | Not just mesh/voxel/point cloud; needs executable CAD |
| **C. Loop** | Iterative repair with feedback channels (M0–M3) | Not one-shot; not pure regeneration |
| **D. Feedback** | Two diagnostic channels: solver feasibility + KQP geometric intent | Different from execution-error feedback or self-reflection |
| **E. Edit cost** | CED_declared + RepairCost | Not just end-state success; how much did it edit? |
| **F. Dataset** | 46 clean + 138 perturbation records from Fusion360 reconstruction | B-rep based, has history JSON, not just rendered images |
| **G. Constraint modeling** | Real CAD constraint solver (FreeCAD sketcher / kiwisolver) | Different from LLM-prior-only "constraint satisfaction" |
| **H. Kernel verification** | OCCT-based STEP loading + KQP runner | Real geometric verification, not visual-only |

---

## 2. The Analysis Model — 10 dimensions for every baseline

For each candidate baseline work, we record the following 10 dimensions.
This is the rubric applied uniformly across all surveyed works.

### D1. Task Formulation
- What does the system generate? (CAD script, IR, B-rep, mesh, voxel, image, etc.)
- Is it generation, repair, edit, retrieval, classification?
- Single-part or assembly?

### D2. Input Modality
- Free-form text, structured spec (like Design Plan), single image, multi-view, point cloud, partial CAD, sketch, history JSON, etc.
- Is there an explicit "task spec" similar to Design Plan?

### D3. Output Representation
- Executable code (CadQuery, OpenSCAD, FreeCAD Python), DSL/IR, native CAD kernel calls, mesh, voxel, neural field, etc.
- Does it produce **executable** CAD or just **representation**?

### D4. Generation / Inference Approach
- One-shot LLM, multi-shot, agentic loop, iterative refinement, search/tree search, RL, supervised, etc.
- LLM backbone(s) used.

### D5. Feedback / Verification Mechanism
- Execution-only, runtime error, self-reflection (Reflexion), unit test, geometric verifier (B-rep validity), constraint solver, semantic check, manual review.
- **Crucially**: does it have a separate *kernel/solver* channel separate from the LLM?

### D6. Repair / Iteration Capability
- Can the system iterate? Max iterations? Stop criteria?
- Edit distance / cost measured?
- "Self-debug" or "self-refine"?

### D7. Datasets Used
- ABC, DeepCAD, Fusion360 Gallery, Text2CAD, MCB, SketchGraphs, Onshape, etc.
- Size, train/test split, perturbation methodology.

### D8. Evaluation Metrics
- Compile/Execute success, STEP load success, KQP pass rate, CED, Chamfer, IoU, Volume Error, BBox Error, success@K, mean-iter, BLEU/ROUGE on code, etc.
- Are geometric intent metrics used? Or only "does the code run"?

### D9. Reported SOTA / Results
- Quantitative numbers on standard benchmarks (best to cite exact splits).
- Human-eval / user study scores.
- Where does this sit relative to SOTA at time of publication?

### D10. Closest Mapping to M0–M3 (this project's ablation axis)
- Which of M0 / M1 / M2 / M3 does it most resemble?
- What feedback channel does it use that matches: pipeline / solver / KQP / self-reflection / image-render?
- If it does not map cleanly, what is the closest analog?

---

## 3. Baseline taxonomy (6 categories)

We organize candidate baselines into 6 categories that cover the closest
analogous work. Each category targets a specific position on the
M0–M3 axis.

| # | Category | Closest M-method | Why relevant |
|---|---|---|---|
| **C1** | **Text/Spec → CAD code generation** (LLM one-shot) | **M0** (no iterative feedback) | The "no-feedback" baseline comparison: can a one-shot LLM generate valid CAD? |
| **C2** | **Agentic / iterative code generation with self-reflection** (Reflexion, Self-Debug, LDB, etc.) | **M0+self-reflect** (between M0 and M1) | Tests whether LLM self-correction alone (no kernel) can match M3 |
| **C3** | **Constraint-solver / symbolic-reasoning–guided code generation** (LLM + SMT, neurosymbolic) | **M1 analog** (constraint feedback) | Direct competitor to solver-feedback channel |
| **C4** | **CAD / B-rep verification, kernel query, geometric check** | **M2 analog** (geometric-intent verification) | Direct competitor to KQP-feedback channel |
| **C5** | **CAD-specific code agents** (CadQuery LLM, OpenSCAD-LLM, text2CAD agents) | **M2 / M3** (CAD domain + feedback) | The closest domain competitors |
| **C6** | **CAD repair / B-rep editing / constraint-satisfaction works** | **M3** (full dual-feedback repair) | The most analogous work — full CAD repair loop |

Each category is surveyed in a dedicated section of the final report.

---

## 4. Inclusion & exclusion criteria

### 4.1 Inclusion
- A work is included if it (a) targets CAD / mechanical part generation
  OR (b) targets code/program generation with iterative refinement
  OR (c) targets constraint-solver or geometric-verification-guided LLM
  generation.
- Both LLM-based and classical (pre-LLM) methods are included where
  they remain SOTA-relevant (e.g., FreeCAD's sketcher, OCCT, SAT-based
  CAD repair).
- Year range: 2020–2026, with priority on 2023–2026 (LLM era).
- Venue priority: SIGGRAPH, NeurIPS, ICML, ICLR, CVPR, ICCV, ECCV,
  ACM TOG, CAD/CAM journals (CAD&A, CAGD, JCISE), and major arXiv.

### 4.2 Exclusion
- Pure mesh/voxel/image generation that does not produce executable CAD
  (unless used as a baseline for B-rep comparison).
- General code-generation works unrelated to CAD or to iterative
  verification (unless they are foundational self-debug / Reflexion).
- Works whose evaluation is only on synthetic / private data with no
  public benchmark.

---

## 5. Coverage check (to be filled after survey)

After surveying, the final report must include a coverage matrix:

```
                ┌───────────────────────────────────────────────┐
                │  All candidate baselines covered?  Y/N        │
                │  Each M0–M3 analog has ≥1 candidate?  Y/N    │
                │  Public benchmarks present?  Y/N              │
                │  At least one SOTA comparison per category?  │
                │  At least 3 pre-LLM classical CAD works?     │
                │  At least 5 LLM-era CAD/code-agent works?    │
                └───────────────────────────────────────────────┘
```

Coverage gaps (if any) MUST be listed in the limitation section of
the final report.

---

## 6. Reading order of the report

1. Project recap (1 page)
2. Analysis model (this file, abbreviated)
3. Category C1 — One-shot LLM CAD generation
4. Category C2 — Iterative / self-reflective code generation
5. Category C3 — Constraint-solver-guided generation
6. Category C4 — Geometric verification / kernel query
7. Category C5 — CAD-domain LLM agents
8. Category C6 — CAD repair / B-rep editing
9. Coverage matrix + open gaps
10. Recommendation: which baselines to actually run
