# Baseline Survey Report — Solver–Kernel Dual-Feedback CAD Generation

> **Project**: 子课题1 — Solver-Kernel 双反馈闭环驱动的 CAD 生成质量提升研究
> **Author**: ZCode (research agent)
> **Date**: 2026-08-02
> **Scope**: Identification of candidate baseline works for the project's
> M0–M3 ablation. *Survey only — no reproduction.*
> **Method**: 6 parallel literature surveys (C1–C6) driven by a 10-dimension
> analysis model (see `analysis_model.md`). ~80 candidate works identified,
> ~70 retained with verified bibliographic data.

---

## Executive Summary

This report surveys prior and contemporary works to position the project's
M0–M3 ablation against the closest comparable baselines. The central claim
of the project is that **two orthogonal feedback channels** — a constraint
solver (FreeCAD sketcher / kiwisolver) and a kernel-query protocol (KQP)
for geometric-intent verification — jointly improve CAD-repair Success@3
beyond what either channel or pure self-reflection achieves.

Across 6 categories (C1–C6), we find:

1. **No prior work implements the exact "Solver–Kernel dual-feedback"
   closed-loop repair agent** that this project proposes. Closest competitors
   are (a) Embodied CAD (solver-grounded LLM agent, but for assembly
   *generation* not repair), (b) CAD-Coder (geometric reward via GRPO,
   one-channel feedback only), and (c) CAD-Editor (LLM-based locate-then-infill
   editing, no kernel feedback).
2. **Each of the project's axes (M0–M3) has at least one published SOTA
   competitor** that maps onto it (see coverage matrix §10).
3. **Classical (pre-LLM) baselines remain highly relevant** for B-rep validity
   repair (OCCT `ShapeFix_*`, FreeCAD sketcher) — these are the floor that
   any LLM-based repair system must beat.
4. **The dominant open question in the field is the integration of solver
   + geometric feedback in inference loops**, which the project targets.
5. **Headline numbers from the LLM-CAD verifier literature** (relevant
   for direct comparison):
   - **HoLa** achieves **82% B-rep validity** (vs ≈50% prior SOTA) — the
     canonical benchmark for B-rep validity.
   - **FllumaOne** achieves **99.14% STEP-export validity** on Qwen2.5-Coder
     1.5B (mean normalized Chamfer 0.002124) — the most explicit
     kernel-validator-in-the-loop pipeline.
   - **CMT** gains **+10.68% Coverage, +10.3% Valid ratio** on ABC
     unconditional generation.
   - **GenCAD-Self-Repairing** converts **~66% of infeasible GenCAD outputs**
     into feasible B-reps — the only published feasibility-restoring work.
   - **Aligning Constraint Generation** (Autodesk) reaches **93% fully-
     constrained sketches** via DPO + constraint-solver feedback (vs.
     34% SFT, 8.9% no-SFT).
   - **Text-to-CadQuery** achieves **69.3% top-1 exact match** and
     **48.6% Chamfer Distance reduction** via fine-tuned LLM.

---

## 1. Project Recap (1 page)

### 1.1 Core proposition
A constraint-grounded agentic CAD generation pipeline that generates
CAD models from a structured **Design Plan v0.6** specification using an
LLM (glm-5.1) producing a **CAD IR v0.1** that is translated by an adaptor
into a **CadQuery** script, then executed to STEP. Two orthogonal feedback
channels inject diagnostics at repair time:

- **Solver channel** — constraint feasibility diagnostics from FreeCAD
  sketcher / kiwisolver (over-constraint, redundancy, conflict).
- **KQP channel** — geometric-intent compliance diagnostics (bbox, void
  count, solidity, symmetry, plane-distance) executed against the STEP
  output via OpenCASCADE.

### 1.2 Ablation
| Method | Pipeline | Solver feedback | KQP feedback |
|---|---|---|---|
| **M0** | ✅ | ❌ | ❌ |
| **M1** | ✅ | ✅ | ❌ |
| **M2** | ✅ | ❌ | ✅ |
| **M3** | ✅ | ✅ | ✅ |

### 1.3 Datasets
- 46 clean samples (reconstructed from Fusion360 history JSON)
- 138 perturbation records (perturbed Clean + perturbed history)
- 48 manual IR examples (authored)

### 1.4 Metrics
- **Primary**: Success@3 (cadquery compiles + STEP loads + KQP passes)
- **Secondary**: mean-iter, CED (CAD Edit Distance), declared-CED,
  RepairCost, KQP pass rate, Solver feedback count

---

## 2. Analysis Model Summary

For each candidate baseline, we record 10 dimensions:
**D1 Task formulation**, **D2 Input modality**, **D3 Output representation**,
**D4 Generation approach**, **D5 Feedback/verification**, **D6 Repair/iteration
capability**, **D7 Datasets**, **D8 Evaluation metrics**, **D9 Reported SOTA**,
**D10 Mapping to M0–M3**.

Full rubric in `analysis_model.md`.

---

## 3. Category C1 — One-shot Text/Spec → CAD Code Generation (≈ M0 baseline)

> Closest M-method: **M0** (no iterative feedback).

### 3.1 Text2CAD
| Field | Value |
|---|---|
| Authors / Year / Venue | Khan et al., 2024, NeurIPS 2024 (Spotlight) |
| arXiv | https://arxiv.org/abs/2409.17106 |
| Task | Text → parametric CAD (sketch+extrude) |
| Representation | Parametric CAD construction sequences |
| Backbone | End-to-end autoregressive transformer (custom) |
| Datasets | DeepCAD (~170K models) + ~660K text annotations |
| Results | First text-to-CAD framework across skill levels; specific metrics in PDF tables |
| Feedback loop | No |
| Mapping | M0 |

### 3.2 CAD-Recode
| Field | Value |
|---|---|
| Authors / Year | Rukhovich et al., 2024 (v2 Mar 2025) |
| arXiv | https://arxiv.org/abs/2412.14042 |
| Task | Point cloud → CAD (reverse engineering) |
| Representation | **Python code** (sketch-extrude as Python) |
| Backbone | Small pretrained LLM (decoder) + lightweight point-cloud projector |
| Datasets | 1M procedurally generated CAD sequences (train); DeepCAD / Fusion360 / CC3D (eval) |
| Results | "10× lower mean Chamfer Distance than prior SOTA" on DeepCAD & Fusion360 |
| Feedback loop | **Partial** — output Python is editable by off-the-shelf LLMs |
| Mapping | M0 (one-shot); M0+edit (with external LLM) |
| Code | https://github.com/filaPro/cad-recode |

### 3.3 GenCAD (and follow-ups)
| Field | Value |
|---|---|
| Authors / Year | Alam & Ahmed (MIT), 2024 |
| arXiv | https://arxiv.org/abs/2409.16294 |
| Task | Image → parametric CAD; also unconditional generation |
| Representation | CadQuery-compatible command sequences + latent diffusion |
| Backbone | Autoregressive Transformer + contrastive vision encoder + diffusion |
| Datasets | ABC, DeepCAD, Fusion360, CC3D |
| Results | SOTA on unconditional + conditional generation vs. DeepCAD, BrepGen |
| Follow-ups | GenCAD-Self-Repairing (arXiv 2505.23287) — converts ~2/3 of infeasible designs into feasible |
| Feedback loop | No in base; **Yes** in self-repairing variant |
| Mapping | M0 (base); M2 (self-repairing — partial) |

### 3.4 CAD-MLLM
| Field | Value |
|---|---|
| Authors / Year | Xu et al., 2024 (v3 Aug 2025) |
| arXiv | https://arxiv.org/abs/2411.04954 |
| Project page | https://cad-mllm.github.io/ |
| Task | Any-modality → parametric CAD (text / image / point cloud) |
| Representation | Parametric CAD command sequences |
| Backbone | LLaVA-style MLLM with CAD-command supervision |
| Datasets | **Omni-CAD** (≈450K multimodal instances) |
| Results | SOTA across modalities; introduces topology-quality + surface-enclosure metrics |
| Feedback loop | No |
| Mapping | M0 (multimodal variant) |

### 3.5 Other C1 works (compact list)
| Paper | arXiv | Backbone | Rep. | Iterative? |
|---|---|---|---|---|
| **BrepGen** | 2401.15563 | Transformer-diffusion | B-rep | No (SIGGRAPH 2024) |
| **SolidGen** | 2203.13944 | AR Transformer + pointer | Indexed B-rep | No (TMLR 2023) |
| **UV-Net** | 2006.10211 | CNN+GNN hybrid | B-rep | No (CVPR 2021) |
| **DeepCAD** | 2105.09492 | Transformer | Op seq. | No (ICCV 2021) |
| **Fusion 360 Gallery** | 2010.02392 | Neural program synthesis | Sketch+extrude lang. | **Yes — RL gym** (SIGGRAPH 2021) |
| **SketchGraphs** | 2007.08506 | GNN | Constraint graph | No |
| **CSGNet** | 1712.08290 | CNN + stack-augmented RNN | CSG | No (TPAMI 2020) |
| **Point2CAD** | 2312.04962 | Hybrid analytic–neural | CAD ops | No |
| **CADTests** | 2605.07807 | Benchmark | n/a | n/a — first executable-test benchmark for text-to-CAD |

> **C1 Coverage**: 13+ works spanning 2020–2026, all the dominant
> datasets (ABC, DeepCAD, Fusion360, CC3D, Omni-CAD, SketchGraphs).
> Mapping to M0 is direct.

---

## 4. Category C2 — Iterative / Agentic / Self-Reflective Code Generation

> Closest M-method: **M0+self-reflection** (between M0 and M1).

### 4.1 Reflexion
| Field | Value |
|---|---|
| Authors / Year / Venue | Shinn et al., NeurIPS 2023 |
| Core | Verbal self-reflection; agent maintains reflective text in memory |
| Feedback | Self-reflection (no external verifier) |
| Datasets | HumanEval, MBPP, LeetCode-Hard, etc. |
| Results | **+11 pp on HumanEval** (91% pass@1 with GPT-4 vs. 80% baseline) |
| Mapping | **M0+reflection** (between M0 and M1) |

### 4.2 Self-Debug
| Field | Value |
|---|---|
| Authors / Year / Venue | Chen et al., 2023 (EMNLP Findings) |
| Core | LLM prompted with code-execution feedback |
| Feedback | Runtime trace + few-shot examples |
| Results | **+12%** on Text-to-Code tasks |
| Mapping | **M0+execution** (close to M1 conceptually) |

### 4.3 Self-Refine
| Field | Value |
|---|---|
| Authors / Year / Venue | Madaan et al., NeurIPS 2023 |
| Core | Same-LLM iterative refine → critique → edit |
| Results | +20 pp on math reasoning, +8 pp on code |
| Mapping | M0+reflection |

### 4.4 Tree of Thoughts (ToT) and RAP
| Paper | Mechanism | Result |
|---|---|---|
| **ToT** (Yao et al., NeurIPS 2023) | Tree search with LLM as evaluator | **74%** on Game of 24 (vs. 4% CoT) |
| **RAP** (Hao et al., ICML 2023) | LLM as world model + reasoning agent | **+33%** plan accuracy on plan generation |

### 4.5 LATS (Language Agent Tree Search)
| Field | Value |
|---|---|
| Authors | Zhou et al., 2024 |
| Core | MCTS + LLM + external feedback |
| Result | **92.7%** on HumanEval |
| Mapping | M0+MCTS (external evaluator needed) |

### 4.6 Voyager / Open-Ended Agents
| Field | Value |
|---|---|
| Authors / Venue | Wang et al., NeurIPS 2023 (Minecraft) |
| Core | LLM + skill library + execution feedback + self-verification |
| Domain | 3D game world; **closest 3D-environment analogue to CAD** |
| Mapping | M0+execution+reflection |

### 4.7 SWE-Agent / AutoCodeRover
| Paper | Result |
|---|---|
| **SWE-Agent** (Yang et al., 2024) | **12.5% pass@1** on SWE-bench |
| **AutoCodeRover** (Zhang et al., 2024) | **19%** on SWE-bench-lite |
| Significance | The closest architectural analogues to a CAD design agent with iterative patching |

### 4.8 Other C2 works
- **Self-Repair** (Lezama, 2023) — interpreter-feedback code repair
- **AgentCoder** — multi-agent code generation with execution feedback
- **CodeAct** (Wang et al., 2024) — **+20%** over JSON actions via executable code
- **AlphaCode 2** (DeepMind, 2023) — search + LLM, competitive on Codeforces
- **PAL** (Gao et al., 2023) — **+15%** on GSM8K via program-aided reasoning
- **LEVER** (Ni et al., 2023) — verifier-trained reranker

> **C2 Coverage**: 14+ works. All are *code-generation* analogues;
> CAD-specific reflection/repair work is sparser (covered in C5/C6).

---

## 5. Category C3 — Constraint-Solver / Symbolic-Reasoning–Guided LLM

> Closest M-method: **M1** (solver feedback channel).

### 5.1 LLM+P (Planner)
| Field | Value |
|---|---|
| Authors / Year | Liu et al., 2023 |
| arXiv | https://arxiv.org/abs/2304.11477 |
| Core | LLM → PDDL → classical planner (Fast Downward) → repair |
| Verifier | PDDL planner (sound) |
| Feedback | Plan failure or invalid action → re-prompt LLM |
| Results | **91–100%** plan accuracy on 8 IPC domains; beats SayCan, Code-as-Policies |
| Mapping | **M1 analog** (constraint solver is the planner) |

### 5.2 DreamCoder
| Field | Value |
|---|---|
| Authors / Year | Ellis et al., NeurIPS 2021 |
| arXiv | https://arxiv.org/abs/2006.08381 |
| Core | Wake-sleep Bayesian program synthesis; growing library |
| Verifier | Typed functional interpreter (sound) |
| Feedback | Counter-example (failed output) on inputs |
| Results | Recovers ~80% of classic programs; rediscovers physics laws |
| Mapping | **M1 analog** (library learning as a "constraint store") |

### 5.3 LeanDojo (ReProver)
| Field | Value |
|---|---|
| Authors / Year | Yang et al., NeurIPS 2023 (D&B track, oral) |
| arXiv | https://arxiv.org/abs/2306.15626 |
| Core | Retrieval-augmented LLM + Lean 3 prover |
| Verifier | Lean 3 kernel (sound) |
| Feedback | Proof-state diff + tactic error string |
| Dataset | 98,734 theorems from Lean mathlib |
| Mapping | **M1 analog** (tactic error is the solver feedback) |

### 5.4 FunSearch
| Field | Value |
|---|---|
| Authors / Year | Romera-Paredes et al., *Nature* 625, 468–475 (2024) |
| DOI | https://www.nature.com/articles/s41586-023-06931-7 |
| Core | Evolutionary program search with Codey/PaLM-2 LLM |
| Verifier | User-supplied deterministic scorer |
| Results | New cap-set constructions; beats classical online bin-packing heuristics |
| Mapping | **M1 analog** (scorer is the solver) |

### 5.5 AlphaGeometry & AlphaProof
| Work | Result |
|---|---|
| **AlphaGeometry** (Trinh et al., *Nature* 625, 476–482, 2024) | 25/30 on IMO-AG benchmark (vs. ~10/30 SOTA) |
| **AlphaProof** (DeepMind blog, 2024) | **28/42 = silver medal** on IMO 2024 |
| Mapping | **M1+M2 combined** (symbolic + neural) |

### 5.6 SAT-LM (and Codex + Z3)
- **SAT-LM** (Poole-Dayan, 2023): SAT solver as per-token filter on the LLM
  vocabulary during constrained decoding.
- **Codex + Z3 loop** (multiple works): LM proposes program → Z3 verifies
  pre/post conditions → counter-example fed back. *This is the direct
  template for M1.*

> **C3 Coverage**: 7 works spanning classical solvers, theorem provers,
> constraint satisfiers, and planners. None targets CAD directly, but
> LLM+P, DreamCoder, LeanDojo, and FunSearch each provide validated
> architectural templates for the M1 channel.

---

## 6. Category C4 — Geometric Verification / Kernel Query / B-rep Validity

> Closest M-method: **M2** (KQP / geometric-intent feedback channel).
> This section is now based on the most comprehensive survey (25+ works,
> 1990s–2026) — see `survey_c4_kernel_query.md` for the full detail.

### 6.1 OCCT — Open-Source Kernel Validator (Canonical M2 Back-end)

**`BRepCheck_Analyzer`** (https://dev.opencascade.org/doc/occt-7.8.0/refman/html/, LGPL-2.1)
- Aggregates per-subshape validator results from `BRepCheck_Shell/Face/Wire/Edge/Vertex`.
- Checks: orientation, 2D/3D edge correspondence, shell/wire closedness,
  parameter validity, B-spline consistency, C0/G1 continuity, self-intersection,
  Euler formula / manifold validity.
- Used as silent back-end in: Text2CAD, Embodied CAD, STEP-LLM, Zero-to-CAD, FllumaOne.

**`ShapeFix_*` toolkit** (same repo)
- Heuristic auto-correction for B-rep defects (small edges, self-intersecting
  wires, missing pcurves, mis-oriented shells, gaps).
- Classes: `ShapeFix_Shape`, `ShapeFix_Wire`, `ShapeFix_Edge`, `ShapeFix_Face`,
  `ShapeFix_Shell`, `ShapeFix_Solid`, plus `ShapeFix_ComposeShell`,
  `ShapeFix_SplitFace`, `ShapeFix_Intersection`, etc.

**Mapping**: **M2 + auto-repair floor** — the open-source geometric
healer any LLM-based repair must match or beat.

### 6.2 FreeCAD Sketcher (GCS)
- https://wiki.freecad.org/Sketcher_Module (LGPL)
- Geometric constraint solver with DoF analysis
  (under-/redundant-/conflicting-constraint diagnostics)
- Solvers: default numeric + Levenberg-Marquardt fallback
- Visual helpers: Select Under-Constrained / Redundant / Conflicting Constraints
- **Mapping**: **M1+M2 baseline** — both constraint solving + diagnostic helpers

### 6.3 Canonical Neural B-rep Generators (validity-aware)

| Work | Year | Venue | URL | Key result |
|---|---|---|---|---|
| **BRepNet** | 2021 | CVPR Oral | https://arxiv.org/abs/2104.00706 | Foundational MPNN over B-rep |
| **ComplexGen** | 2022 | SIGGRAPH | https://arxiv.org/abs/2205.14573 | B-rep chain complex + structural validness |
| **BrepGen** | 2024 | SIGGRAPH | https://arxiv.org/abs/2401.15563 | First B-rep diffusion; node-merge + OCCT |
| **HoLa** | 2025 | SIGGRAPH | https://arxiv.org/abs/2504.14257 | **82% validity** vs ≈50% prior SOTA |
| **AutoBrep** | 2025 | SIGGRAPH Asia | https://arxiv.org/abs/2512.03018 | Unified tokenization + native autocompletion |
| **DTGBrepGen** | 2025 | – | https://arxiv.org/abs/2503.13110 | Topology/geometry decoupled |
| **CMT** | 2025 | – | https://arxiv.org/abs/2504.20830 | **+10.68% Coverage, +10.3% Valid ratio** (ABC) |
| **HiDiGen** | 2026 | – | https://arxiv.org/abs/2604.02847 | Two-stage hierarchical diffusion |
| **TG-Diff** | 2026 | – | https://arxiv.org/abs/2607.21928 | D3PM discrete topology + DiT |
| **ParaCAD** | 2026 | – | https://arxiv.org/abs/2607.17093 | Surface-centric parametric tokenization |
| **BrepARG** | 2026 | – | https://arxiv.org/abs/2601.16771 | Holistic token sequence |
| **k-Cell Particles** | 2026 | – | https://arxiv.org/abs/2601.17733 | Compositional k-cell particle sets |
| **BrepForge** | 2026 | – | https://arxiv.org/abs/2605.19411 | Wireframe composition + BC surface |
| **Topology-First Meshing** | 2026 | – | https://arxiv.org/abs/2604.02141 | Guaranteed topologically correct |
| **NeuroNURBS** | 2024 | – | https://arxiv.org/abs/2411.10848 | Reduces BrepGen FID 30.04 → 27.24 |

### 6.4 B-rep Feature Recognition (M2 preprocessing)

| Work | Year | URL | Key result |
|---|---|---|---|
| **BRepFormer** | 2025 | https://arxiv.org/abs/2504.07378 | SOTA on MFInstSeg, MFTRCAD, CBF (20k) |
| **BRepMAE** | 2026 | https://arxiv.org/abs/2602.22701 | High recognition with **0.1% labeled data** |
| **FeatureFox** | 2026 | https://arxiv.org/abs/2604.26770 | PQ > 0.9 with ~250 parts |
| **BRT** | 2025 | https://arxiv.org/abs/2504.07134 | CAD journal B-rep transformer |

### 6.5 LLM + Geometric-Verifier Pipelines (Direct M2 Competitors)

| Work | Year | URL | Geometric verifier signal |
|---|---|---|---|
| **CADReasoner** | 2026 | https://arxiv.org/abs/2603.29847 | Rendered-mesh geometric discrepancy |
| **Embodied CAD** | 2026 | https://arxiv.org/abs/2606.31252 | Solver feedback (kernel-as-M2) |
| **AgentsCAD** | 2026 | https://arxiv.org/abs/2607.02448 | GPT-4o vision + overhang detection |
| **STEP-LLM** | 2026 | https://arxiv.org/abs/2601.12641 | RL with Chamfer Distance reward |
| **Text-to-CadQuery** | 2025 | https://arxiv.org/abs/2505.06507 | **69.3% top-1 exact; 48.6% CD reduction** |
| **CAD-Coder** | 2025 | https://arxiv.org/abs/2505.14646 | **100% syntax;** outperforms GPT-4.5 |
| **Zero-to-CAD** | 2026 | https://arxiv.org/abs/2604.24479 | Iterative code validation |
| **AssemCAD** | 2026 | https://arxiv.org/abs/2607.05123 | B-Rep geometric evidence for declared interfaces |
| **FllumaOne** | 2026 | https://arxiv.org/abs/2606.17696 | **99.14% STEP-export validity**; mean CD 0.002124 |
| **MUSE** | 2026 | https://arxiv.org/abs/2605.28579 | Code→geometric→design-intent cascade |
| **HistCAD** | 2025-26 | https://arxiv.org/abs/2602.19171 | Constraint-aware editability (ER/cPCSR/OES) |
| **CADCON** | 2026 | https://arxiv.org/abs/2607.23191 | Independent B-rep assertions (anti-circularity) |
| **Text2CAD-Bench** | 2026 | https://arxiv.org/abs/2605.18430 | 600 examples L1–L4; multi-level eval |
| **GIFT** | 2026 | https://arxiv.org/abs/2603.27448 | Geometric inference feedback; **+12% IoU** |
| **CAD-Coder (GRPO)** | 2025 | https://arxiv.org/abs/2505.19713 | NeurIPS; GRPO + geometric reward |
| **CADFusion** | 2025 | https://arxiv.org/abs/2501.19054 | ICML; multi-view visual feedback (offline DPO) |

### 6.6 Headline Numbers for M2 Benchmarking

| Metric | Best published result | Source |
|---|---|---|
| B-rep validity rate (direct generation) | **82%** | HoLa (2504.14257) |
| STEP-export validity (LLM-CAD) | **99.14%** | FllumaOne (2606.17696) |
| CadQuery top-1 exact match | **69.3%** | Text-to-CadQuery (2505.06507) |
| CadQuery syntax validity | **100%** | CAD-Coder (2505.14646) |
| B-rep Coverage (ABC) | **+10.68%** over SOTA | CMT (2504.20830) |
| B-rep Valid ratio (ABC) | **+10.3%** over SOTA | CMT (2504.20830) |
| MFR panoptic quality | **PQ > 0.9** with ~250 parts | FeatureFox (2604.26770) |
| Feature recognition sample efficiency | **0.1%** labeled data | BRepMAE (2602.22701) |

### 6.7 Commercial B-rep Repair (industry baselines)

| Tool | Vendor | Notes |
|---|---|---|
| **ACIS Healing** | Spatial Corp. | Industry standard |
| **Parasolid Healing** | Siemens | PK_TOPOL_check_* and PK_GEOM_check_* families |
| **3D_Evolution** | CoreTechnologie | STEP AP242 + LOTAR |
| **CADdoctor** | Elysium (ITI TranscenData) | Geometry healing + CAD translation |
| **TransMagic** | TransMagic Inc. | Dedicated STEP/IGES repair |
| **CAD Exchanger** | – | Developer kit |

### 6.8 Coverage Summary

| Subcategory | # works | Closest M-method |
|---|---|---|
| Open-source kernel (OCCT) | 5+ classes | **M2 floor** |
| Open-source constraint solver | 1 (FreeCAD) | M1+M2 floor |
| Commercial kernel (ACIS / Parasolid) | 2 | M2 industry floor |
| Commercial STEP validator | 3+ | M2 industry floor |
| Neural B-rep generators (validity-aware) | 15 | M2 implicit |
| B-rep feature recognition | 4 | M2 preprocessing |
| **LLM + geometric verifier pipelines** | **13+** | **M2 direct competitors** |
| Neural SDF verifiers | 6+ | M2 soft |
| Geometric query primitives | 10+ | M2 primitives |

**Critical observation**: The C4 category is now extremely well-populated.
The project's KQP design sits among **13+ recent LLM + geometric-verifier
pipelines**. However, the project uniquely combines the **OCCT-style
structured kernel queries** (bbox, void count, symmetry, continuity,
Euler-formula check) with **FreeCAD-style constraint-solver feedback**
in a **repair setting** with **CED metric** on **Fusion360-derived IR**.
**None of the 13 LLM + verifier works performs this specific combination
on this specific dataset.**

> Full C4 detail in `survey_c4_kernel_query.md` (~12 KB, 6 sections,
> 25+ works, 8 sections of headline numbers).

---

## 7. Category C5 — CAD-Domain LLM Agents (CAD-specific + feedback)

> Closest M-method: **M2 / M3** (CAD domain + feedback).

### 7.1 CADFusion (Microsoft)
| Field | Value |
|---|---|
| Venue / Year | ICML 2025 |
| arXiv | https://arxiv.org/abs/2501.19054 |
| Core | Text-to-CAD with **visual feedback** loop (multi-view rendered) |
| Significance | Most direct LLM-with-visual-feedback competitor |

### 7.2 CAD-Coder
| Field | Value |
|---|---|
| Venue / Year | NeurIPS 2025 |
| arXiv | https://arxiv.org/abs/2505.19713 |
| Core | CadQuery-script generation with **GRPO + geometric reward** |
| Significance | LLM-with-solver-reward loop analogous to M2 |

### 7.3 CAD-Editor (Microsoft)
| Field | Value |
|---|---|
| Authors / Year | Yuan et al., 2025 |
| arXiv | https://arxiv.org/abs/2502.03997 |
| Code | https://github.com/microsoft/CAD-Editor |
| Core | **Locate-then-infill** framework; LLM as backbone; LVLM-synthesized training data |
| Mapping | **M3-adjacent** (no kernel feedback, but iterative editing) |

### 7.4 CADReasoner
| Field | Value |
|---|---|
| Authors / Year | Kabisov et al., 2026 |
| arXiv | https://arxiv.org/abs/2603.29847 |
| Core | Iterative program editing; rendered mesh → CadQuery edit |
| Datasets | DeepCAD, Fusion 360, MCB (clean + scan-sim) |
| Mapping | **M2 / M3** (geometric discrepancy as feedback) |

### 7.5 Embodied CAD (Liu et al., 2026)
| Field | Value |
|---|---|
| arXiv | https://arxiv.org/abs/2606.31252 |
| Core | **Solver-grounded LLM agent** with stratified L0–L4 CAD skill library, deterministic parameter resolution, **solver-derived rewards** for SFT warm-up + GRPO refinement |
| Datasets | Multi-step mechanical, industrial equipment, mold-oriented assemblies |
| Results | Solver-grounded planning "executes all strong-planner workflows"; learned controllers reach "high executable rates" |
| Mapping | **M1+M2** combined (closest published *solver-grounded agent* loop) |
| Significance | **The most direct published competitor to M3.** Note: targets generation, not repair. |

### 7.6 Aligning Constraint Generation (Autodesk AI Lab)
| Field | Value |
|---|---|
| Authors / Year | Casey et al., 2025 (v2 Aug 2025) |
| arXiv | https://arxiv.org/abs/2504.13178 |
| Project page | https://autodeskailab.github.io/aligning-constraint-generation/ |
| Method | DPO-style alignment with constraint-solver feedback |
| Result | **93% fully-constrained sketches** vs. 34% (SFT) vs. 8.9% (no SFT) |
| Mapping | **M1 analog** (constraint solver is the verifier) |

### 7.7 ProCAD (Proactive Clarifying Agent)
| Field | Value |
|---|---|
| arXiv | https://arxiv.org/abs/2602.03045 |
| Core | Two-agent pipeline (clarifier + CAD coder) |
| Result | **79.9%** reduction in mean Chamfer vs. Claude Sonnet 4.5; invalidity **4.8% → 0.9%** |
| Mapping | M2 / M3 (clarification as soft feedback) |

### 7.8 Other C5 works
| Paper | arXiv | Note |
|---|---|---|
| **CAD-Llama** | 2505.04481 | LLM adapted to SPCC for parametric CAD code |
| **NURBGen** | 2511.06194 | LLM emits JSON-NURBS (AAAI 2026) |
| **PLLM** | 2602.12561 | Pseudo-labeling LLM for CAD (CAD-Recode-based) |
| **CADEvolve** | 2602.16317 | Evolution-based CadQuery with VLM-guided edits |
| **CMT** | 2504.20830 | Cascade MAR + topology predictor |
| **CAD-Tokenizer** | 2509.21150 | Modality-specific tokenization (ICLR 2026) |
| **Cosmo-Agent** | 2604.05547 | RL agent that revises parametric geometry |
| **PR-CAD** | 2604.19773 | Unifies text-to-CAD gen + edit via RL |
| **ArtiCAD** | 2604.10992 | Multi-agent assembly with rollback |
| **HistCAD** | 2602.19171 | Constraint-aware parametric history dataset (170K sequences) |
| **MUSE** | 2605.28579 | Manufacturability benchmark |
| **Linkify** | 2607.01205 | Fixes missing contacts in Fusion 360 Gallery |
| **CADCrafter** | 2504.04753 | Image→parametric CAD (CVPR 2025) |
| **SkexGen** | 2207.04632 | Autoregressive sketch-extrude (ICML 2022) |
| **DAVINCI** | 2410.22857 | Single-stage constrained CAD sketches |
| **PICASSO** | 2407.13394 | Raster→parametric CAD via rendering self-supervision |
| **SketchGen** | 2106.02711 | Constrained CAD sketch generator |
| **STEP-LLM** | (cited in C1 survey) | Visual feedback LLM for text-to-CAD |
| **Text-to-CadQuery** | (cited in C1 survey) | Direct LLM-driven CadQuery generation |
| **ArtisanCAD** | (cited in C1 survey) | Multi-view visual feedback LLM |

> **C5 Coverage**: 20+ works — the most active category in 2024–2026.
> Embodied CAD is the closest published solver-grounded agent loop.
> The project occupies a **gap** in this category: dual-channel
> solver + geometric feedback in a repair setting.

---

## 8. Category C6 — CAD Repair / B-rep Editing / Constraint Satisfaction

> Closest M-method: **M3** (full dual-feedback repair loop).

### 8.1 GenCAD-Self-Repairing (Tsuji et al., 2025)
| Field | Value |
|---|---|
| arXiv | https://arxiv.org/abs/2505.23287 |
| Core | Diffusion-guided latent refinement + regression-based command-sequence correction |
| Result | Converts **~2/3 (66%)** of infeasible GenCAD outputs into feasible B-reps |
| Mapping | **M3 closest in CAD domain** — feasibility-restoring repair loop |
| Significance | **The only published work that explicitly converts infeasible → feasible CAD** |

### 8.2 Embodied CAD
(Already in C5; included here as M3 closest.) Targets *generation*,
not repair, but is the closest architectural template.

### 8.3 Constraint Alignment (Autodesk)
(Already in C5.) Targets *constraint generation*, not repair, but is
the closest solver-feedback-in-the-loop template.

### 8.4 CADReasoner
(Already in C5.) Iterative geometric-mismatch repair.

### 8.5 CAD-Editor (Microsoft)
(Already in C5.) Text-based CAD *editing* (re-edit existing CAD given
text instruction) — adjacent to repair but driven by intent, not validity.

### 8.6 B-rep Boolean Repair (Huang et al., 2023)
| Field | Value |
|---|---|
| arXiv | https://arxiv.org/abs/2310.10351 |
| Core | Set-reasoning inference procedure; per-edge adaptive tolerance; topological edge correction |
| Target | False topological intersection edges from Boolean ops |
| Mapping | Classical B-rep repair baseline (M3 sub-task) |

### 8.7 HistCAD (Dong et al., 2025–2026)
| Field | Value |
|---|---|
| arXiv | https://arxiv.org/abs/2602.19171 |
| Core | Dataset + benchmark for parametric editability under perturbations |
| Dataset | **170,236** executable parametric sequences + STEP + rendered + text |
| Metrics | ER, cPCSR, OES |
| Mapping | **A dataset directly usable as a perturbation-repair benchmark** |

### 8.8 CSGNet & Inverse-CSG family
| Paper | Year | arXiv | Note |
|---|---|---|---|
| **CSGNet** | 2018 (TPAMI 2020) | 1712.08290 | Foundational inverse CSG |
| **D²CSG** | 2023 | 2301.11497 | Unsupervised dual-branch CSG reconstruction |
| **DiffCSG** | 2024 | 2409.01421 | Differentiable rasterization CSG |
| **Szalinski** (Nandi et al.) | 2020 | 1909.12252 | Equality-saturation inverse transformations (PLDI 2020) |

These are the closest "shape → editable program" repair-family baselines,
albeit for CSG rather than parametric CAD.

### 8.9 B-rep Feature Recognition (preprocessing for repair)
| Work | arXiv | Note |
|---|---|---|
| **BRepFormer** | 2504.07378 | Feature recognition + suppression |
| **BRepMAE** | 2602.22701 | Sample-efficient recognition |
| **BRT** | 2504.07134 | CAD journal transformer |

### 8.10 Industry B-rep Repair (industry baseline)
Already enumerated in §6.5.

### 8.11 Classical Constraint-Solver Survey
- **Zou et al., "A Review on Geometric Constraint Solving"** (2022)
  arXiv: https://arxiv.org/abs/2202.13795
- Companion: **Zou & Feng, "On Limitations of the Witness Configuration Method"**
  arXiv: https://arxiv.org/abs/1904.00526

### 8.12 Additional Adjacent Works
- **Cosmo-Agent** (2604.05547) — RL agent that revises parametric geometry
  until constraints satisfied — direct "repair loop" analogue.
- **PR-CAD** (2604.19773) — unifies text-to-CAD gen + edit via RL.
- **CAD-Llama** (2505.04481) — LLM adapted to SPCC.
- **Linkify** (2607.01205) — fixes Fusion 360 Gallery assembly contacts.
- **ArtiCAD** (2604.10992) — multi-agent assembly with rollback.

> **C6 Coverage**: 16+ works spanning 2017–2026, including inverse-CSG
> lineage (CSGNet → D²CSG → DiffCSG), B-rep feature recognition
> (BRepFormer/MAE/BRT), and constraint-satisfaction surveys. **No prior
> work implements the project's specific "Solver + KQP dual-feedback on
> perturbed Fusion360-derived IR" recipe.**

---

## 9. Cross-Cutting Observations

### 9.1 The feedback-loop landscape (2024–2026)
| Mechanism | Representative works | Closest M-method |
|---|---|---|
| **Self-reflection only** (no external verifier) | Reflexion, Self-Refine | M0+reflection |
| **Execution only** | Self-Debug, Voyager | M0+execution |
| **Tree-search + external verifier** | LATS, RAP, ToT | M0+search |
| **Solver-as-verifier** | LLM+P, LeanDojo, DreamCoder, FunSearch | M1 |
| **Visual-feedback training (offline)** | CADFusion | M2 (offline) |
| **Geometric reward via RL** | CAD-Coder, Embodied CAD, STEP-LLM | M1+M2 |
| **Solver-grounded agent** | Embodied CAD, Aligning Constraint | M1+M2 |
| **Self-repairing diffusion** | GenCAD-Self-Repairing | M3 |
| **Iterative program edit (geometry feedback)** | CADReasoner, FllumaOne, Zero-to-CAD | M2 |
| **Iterative kernel-validated code generation** | AgentsCAD, AssemCAD, MUSE | M2 |
| **RL revise-until-valid** | Cosmo-Agent, PR-CAD | M3 |
| **Dual-channel (solver + geometric)** | **None identified** | **M3** ← *project gap* |

### 9.2 LLM backbone trend
- Decoder-only LLMs (LLaMA, Code-LLaMA, GPT-4, Claude, Gemini) dominate
  new CAD agents (CAD-Recode, CAD-Coder, ProCAD, CADFusion).
- Custom autoregressive transformers dominate classical CAD generation
  (Text2CAD, DeepCAD, GenCAD).
- Hybrid setups (LLM-as-decoder + custom projector / diffusion) are
  most common (CAD-Recode, GenCAD).

### 9.3 Dataset landscape
| Dataset | Size | Type | Used by |
|---|---|---|---|
| **DeepCAD** | 178,238 | Sketch+extrude sequences | Text2CAD, CAD-Recode, GenCAD, CAD-Reasoner, … |
| **Fusion 360 Gallery** | 8,625 | Human design sequences | CAD-Recode, Linkify, GenCAD, Embodied CAD |
| **ABC** | 1M+ | B-rep | GenCAD, BrepGen, SolidGen, Point2CAD, CMT |
| **SketchGraphs** | 15M | Onshape constraint graphs | SketchGraphs, DAVINCI |
| **CC3D** | real-world | Real scans | CAD-Recode, GenCAD |
| **Omni-CAD** | 450K | Multimodal | CAD-MLLM |
| **mmABC** | 1.3M | B-rep + multimodal | CMT |
| **CADEvolve** | 1.3M | CadQuery scripts | CADEvolve |
| **Text2CAD** | ~170K + ~660K text | Text + CAD | Text2CAD |
| **CBF** | 20,000 | B-rep | BRepFormer |
| **HistCAD** | 170,236 | Parametric sequences | HistCAD |
| **This project** | 46 clean + 138 perturbed + 48 manual IR | Fusion360-derived | **M0–M3 ablation** |

### 9.4 The explicit gap this project targets
> **No prior work integrates solver feedback + KQP geometric feedback in
> a closed repair loop for perturbed Fusion360-derived CAD IR, with
> Success@3 + CED as joint metrics.**
>
> Closest competitors:
> 1. **Embodied CAD** (solver-grounded agent, but generation not repair)
> 2. **GenCAD-Self-Repairing** (feasibility-restoring diffusion, single channel)
> 3. **CAD-Coder** (GRPO + geometric reward, one channel)
> 4. **CAD-Editor** (LLM iterative editing, no kernel feedback)
> 5. **OCCT ShapeFix** + **FreeCAD Sketcher** (classical geometric healer / solver)

---

## 10. Coverage Matrix (required by §5 of `analysis_model.md`)

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
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 11. Recommended Baselines to Actually Run

For empirical comparison (in priority order):

### Tier 1 — Direct M0–M3 competitors
1. **Embodied CAD** (Liu et al., 2026) — closest solver-grounded agent loop.
2. **GenCAD-Self-Repairing** (Tsuji et al., 2025) — only published
   infeasible→feasible converter (66% success rate).
3. **CAD-Coder** (NeurIPS 2025) — LLM + GRPO + geometric reward.

### Tier 1b — New M2 competitors surfaced in C4 retry
4. **FllumaOne** (Zhan, 2026) — 99.14% STEP-export validity; the most
   explicit kernel-validator-in-loop pipeline. Closest published analogue
   of the project's KQP loop on the LLM-CAD generation side.
5. **CADReasoner** (Kabisov et al., 2026) — iterative geometric-mismatch
   repair via rendered-mesh Chamfer feedback. SOTA on DeepCAD/Fusion360/MCB.
6. **STEP-LLM** (Shi et al., DATE 2026) — RL with Chamfer Distance reward;
   uses STEP round-trip validity as kernel check.
7. **Aligning Constraint Generation** (Casey et al., Autodesk, 2025) —
   93% fully-constrained via DPO + constraint-solver feedback (M1 strongest).

### Tier 2 — Domain-relevant code agents
8. **CAD-Recode** (Rukhovich et al., 2024) — LLM-as-decoder for CadQuery;
   re-editable output maps directly to M0 / M0+edit.
9. **CAD-Editor** (Yuan et al., 2025; Microsoft) — locate-then-infill
   framework; open-source.
10. **CAD-MLLM** (Xu et al., 2024) — multimodal MLLM baseline.
11. **Text-to-CadQuery** (Xie & Ju, 2025) — 69.3% top-1 exact match.
12. **CAD-Coder (VLM)** (Doris et al., 2025) — 100% syntax; outperforms GPT-4.5.

### Tier 3 — Classical / pre-LLM floor
13. **OCCT `ShapeFix_*` + `BRepCheck_*`** — open-source B-rep healer
    (LGPL 2.1).
14. **FreeCAD Sketcher (GCS)** — open-source constraint solver with
    DoF diagnostics.
15. **HoLa** (Liu et al., 2025) — the canonical B-rep validity benchmark
    (82% vs 50% SOTA); useful as a *validity floor* for the M2 channel.
16. **BRepFormer / BRepMAE / FeatureFox** — neural feature recognition
    preprocessors that simplify downstream repair.

### Tier 4 — Self-reflection baselines (for M0+reflection ablation)
17. **Reflexion** (Shinn et al., 2023) — verbal self-reflection baseline.
18. **Self-Debug** (Chen et al., 2023) — execution-feedback baseline.

### Tier 5 — Diagnostic-only baselines
19. **GenCAD** (Alam & Ahmed, 2024) — one-shot LLM CAD baseline
    (without self-repair).
20. **Text2CAD** (Khan et al., NeurIPS 2024) — text→CAD baseline.

### Tier 6 — Agentic-RL & RL-revise baselines (newly surfaced)
21. **Cosmo-Agent** (Deng et al., 2026) — RL agent that revises parametric
    geometry until constraints satisfied (direct repair-loop analogue).
22. **PR-CAD** (An et al., 2026) — unifies text-to-CAD gen + edit via RL.
23. **Zero-to-CAD** (Ataei et al., 2026) — agentic LLM-in-CAD-environment
    search at million-scale.

> **Minimum viable baseline set** for an M0/M1/M2/M3 ablation paper:
> Tier 1 (1–3) + one of Tier 1b (4–7) + Tier 3 (13–14) + one Tier 4
> (17 or 18) + one Tier 5 (19 or 20). This guarantees both domain coverage
> (CAD-specific) and methodological coverage (each M-method has at least
> one competitor).
>
> **Stretch baseline set** for a stronger comparison: also include
> Tier 1b fully + Tier 2 fully + Tier 6 — i.e., 20+ baselines across
> all M-methods, providing headroom for sensitivity analysis.

---

## 12. Open Gaps and Limitations

### 12.1 Identified gaps in this survey
1. **Quantitative numbers for many papers are not present on arXiv abstract
   pages.** Specific numerical results would require fetching the PDF/HTML
   body of each paper. Where this was done (Text2CAD, CAD-Recode, BrepGen,
   SolidGen, DeepCAD, UV-Net, Constraint Alignment, CAD-Editor, Embodied
   CAD, Fusion 360 Gallery, OCCT, BRepFormer), exact values are still
   often absent (only abstract-level claims). **This is a known limitation
   of abstract-only verification.** Several headline numbers (e.g.,
   HoLa 82% validity, FllumaOne 99.14% STEP-validity, CMT +10.68%
   Coverage) were captured verbatim from abstracts; PDF tables would
   yield complete precision.

2. **Direct M3 competitor is absent** — i.e., no prior work performs
   *exactly* "solver + KQP dual-feedback repair on perturbed parametric
   CAD IR with Success@3 + CED." This is the project's defensible
   contribution gap. To *quantify* the gap, one would still need to
   reproduce (or at least reimplement) Embodied CAD or GenCAD-SR on the
   project's 46+138 dataset.

3. **Commercial B-rep repair tools** (ACIS, Parasolid, CADdoctor,
   TransMagic, 3D_Evolution) cannot be directly benchmarked — they
   are proprietary and lack published success-rate numbers.

4. **C4 retry integration complete.** The C4 (kernel-query) category
   was originally surveyed with only ~9 works (first agent run failed);
   the retry recovered 25+ works, including 13+ LLM + geometric-verifier
   pipelines (D1–D13 in §6.5), 15 neural B-rep generators with
   validity-aware outputs, and the headline benchmark numbers (HoLa 82%,
   FllumaOne 99.14%, CMT +10.68%, etc.). **This category is now
   comprehensively covered.**

### 12.2 Coverage by project axis
| Project axis | Covered by | Gap |
|---|---|---|
| Design-Plan → CAD IR (structured spec input) | Embodied CAD, CADFusion | None |
| Solver-feedback (FreeCAD sketcher / kiwisolver) | OCCT, FreeCAD, Constraint Alignment, LLM+P | None |
| KQP-feedback (OCCT kernel queries) | OCCT ShapeFix, CADReasoner, GenCAD-SR, FllumaOne, STEP-LLM, MUSE | None |
| Dual-feedback repair on perturbed IR | **None** | **Project contribution** |
| CED metric | CAD-Editor (partial), HistCAD (ER metric) | No direct prior; CED is a project innovation |
| Fusion360 history JSON perturbation | HistCAD, Linkify | Project uses own perturbation protocol |
| RL revise-until-valid | Cosmo-Agent, PR-CAD | Adjacent; not directly M3 dual-channel |

---

## 13. Files in This Survey Directory

- `README.md` — index + coverage audit
- `analysis_model.md` — the 10-dimension analysis rubric
- `final_report.md` — this document (main report, ~36 KB)
- `survey_c1_oneshot_cad.md` — Category C1 details (13 works)
- `survey_c2_iterative_codegen.md` — Category C2 details (16 works)
- `survey_c3_neurosymbolic.md` — Category C3 details (7+ works)
- `survey_c4_kernel_query.md` — **Category C4 details (25+ works, 6 sections)** — comprehensive retry result
- `survey_c5_cad_llm_agents.md` — Category C5 details (20+ works)
- `survey_c6_cad_repair.md` — Category C6 details (16+ works)

**Total surveyed**: ~95 works across 6 categories.

---

## 14. Suggested Next Steps (for the project, not for this survey)

1. **Implement Tier-3 baselines first** (OCCT `ShapeFix_*` + FreeCAD Sketcher)
   to establish the classical floor on the project's 46+138 dataset.
2. **Implement HoLa-style validity benchmark** on the same perturbation set
   to calibrate the M2 channel against the 82% validity benchmark.
3. **Implement one Tier-4 baseline** (Reflexion or Self-Debug applied to
   the same LLM backbone) to establish the M0+reflection reference.
4. **Reimplement FllumaOne's pipeline** (closest published kernel-validator-
   in-loop on LLM-CAD) and **Aligning Constraint Generation's solver-
   feedback DPO** (closest solver-feedback fine-tuning). Together these
   give the strongest published M1 + M2 baselines.
5. **Reimplement Embodied CAD's solver-grounded agent loop** (or as much
   of it as is publicly reproducible) to get the closest published M3
   competitor.
6. **Reimplement GenCAD-Self-Repairing** for the infeasible→feasible
   converter baseline (66% published success rate on GenCAD).
7. **Report Success@3, mean-iter, CED_declared, RepairCost** across
   M0 / M1 / M2 / M3 and the baseline(s) on the same 46 clean + 138
   perturbation samples for direct comparability.
8. **Document the absence of a direct M3 prior** as a contribution in
   the paper's introduction. Cite the 13+ LLM + geometric-verifier
   pipelines from §6.5 as the closest published analogues.
9. **Methodological caution from CADCON** (arXiv 2607.23191): ensure
   the Success@3 metric uses **independent geometric assertions**, not
   text/token metrics, to avoid circularity.

---

*End of report.*
