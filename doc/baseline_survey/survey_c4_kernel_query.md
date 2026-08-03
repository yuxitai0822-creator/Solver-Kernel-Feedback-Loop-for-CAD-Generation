# Category C4 — Geometric Verification / Kernel Query / B-rep Validity

> **Closest M-method**: M2 (KQP / geometric-intent feedback channel)
> **Survey count**: 25+ works (1990s–2026)
> **Combined from**: Background agent (first attempt failed) + retry agent + direct WebFetch

---

## Section A — Kernel-level B-rep Validity Checkers

### A1. OCCT `BRepCheck_Analyzer` (Canonical)
- **URL**: https://dev.opencascade.org/doc/occt-7.8.0/refman/html/
- **Repo**: https://github.com/Open-Cascade-SAS/OCCT (LGPL-2.1)
- **Method**: Aggregates per-subshape validator results from `BRepCheck_Shell`, `BRepCheck_Face`, `BRepCheck_Wire`, `BRepCheck_Edge`, `BRepCheck_Vertex`. Reports `BRepCheck_Status` (valid / invalid / warning).
- **Checks**: orientation consistency, 2D/3D edge correspondence, edge/face counts, shell/wire closedness, curve/surface parameter validity, B-spline consistency, C0/G1 continuity, self-intersection detection, Euler formula / manifold validity.
- **Mapping**: **M2 back-end baseline** — canonical open-source kernel validator.
- **Used in LLM pipelines**: Text2CAD, Embodied CAD, STEP-LLM, Zero-to-CAD, FllumaOne (silent back-end).

### A2. OCCT `ShapeFix_*` Auto-correction Toolkit
- **Repo**: https://github.com/Open-Cascade-SAS/OCCT
- **Components**: `ShapeFix_Shape`, `ShapeFix_Wire`, `ShapeFix_Edge`, `ShapeFix_Face`, `ShapeFix_Shell`, `ShapeFix_Solid`, `ShapeFix_ComposeShell`, `ShapeFix_SplitFace`, `ShapeFix_Intersection`, `ShapeFix_FreeBounds`, `ShapeFix_ThinWall`, `ShapeFix_Normalize`.
- **Heuristics**: small edge removal, self-intersection fix, missing pcurves, mis-oriented shells, gap closure.
- **Mapping**: **M2 + repair** baseline (kernel + auto-correct).

### A3. FreeCAD Sketcher (GCS)
- **URL**: https://wiki.freecad.org/Sketcher_Module
- **Repo**: https://github.com/FreeCAD/FreeCAD
- **Method**: Degrees-of-freedom-driven GCS with primary numeric solver + LM fallback.
- **Checks**: under/fully/over-constrained classification; visual selectors for Under-Constrained / Redundant / Conflicting Constraints; supported geometric + dimensional constraint vocabulary.
- **Mapping**: **M1+M2 baseline** — both constraint solving + diagnostic helpers.

### A4. ACIS / Parasolid (commercial)
- **Vendor**: Spatial Corp. (ACIS/CGM) / Siemens (Parasolid).
- **APIs**: Parasolid `PK_TOPOL_check_*` and `PK_GEOM_check_*`; ACIS `api_check_entity`, `ATTRIB`-based audits.
- **Checks**: topology consistency, curve/surface parameter validity, self-intersection, closedness, G1/C1 continuity, sheet-body manifold, bbox/centroid queries.
- **Mapping**: Industry baseline (no public benchmarks).

### A5. Commercial STEP Validators
- **TransMagic**, **CADdoctor** (ITI TranscenData), **3D_Evolution** (CoreTechnologie), **CAD Exchanger**.
- **Checks**: Euler-Poincaré topology, curve/surface parameter integrity, sewing/gaps, tolerance thresholds.
- **Mapping**: Industry baseline.

---

## Section B — Canonical Neural B-rep Generative Models (with validity concerns)

### B1. BRepNet — Topological Message Passing for Solid Models
- **Authors / Venue**: Lambourne et al. (Autodesk), CVPR 2021 Oral
- **URL**: https://arxiv.org/abs/2104.00706
- **Method**: MPNN over B-rep half-edge / co-edge structure; operates directly on topology.
- **Mapping**: Foundational B-rep learning baseline (not directly M2).

### B2. ComplexGen — CAD Reconstruction by B-Rep Chain Complex Generation
- **Authors / Venue**: Guo et al. (Microsoft), SIGGRAPH 2022
- **URL**: https://arxiv.org/abs/2205.14573
- **Code**: https://github.com/guohaoxiang/ComplexGen (MIT)
- **Method**: B-rep chain complex as graph; sparse-CNN encoder + tri-path transformer decoder; "structural validness" loss.
- **Mapping**: B-rep reconstruction baseline.

### B3. BrepGen — B-rep Generative Diffusion
- **URL**: https://arxiv.org/abs/2401.15563 ; code https://github.com/samxuxiang/BrepGen
- **Venue**: SIGGRAPH 2024 (Autodesk + SFU)
- **Method**: Hierarchical tree latent + transformer diffusion; topology via node duplication; OCCT check post-hoc.
- **Mapping**: B-rep generation (validity implicit via node-merge + OCCT).

### B4. HoLa — B-Rep Generation using a Holistic Latent Representation
- **URL**: https://arxiv.org/abs/2504.14257
- **Project**: https://vcc.tech/research/2025/HolaBrep
- **Demo**: https://huggingface.co/spaces/YuXingyao/HoLa-BRep
- **Venue**: SIGGRAPH 2025
- **Method**: Holistic latent defined only on surfaces; topology re-derived via neural intersection.
- **Result**: **Validity rate 82% vs ≈50% for prior SOTA** — canonical benchmark for B-rep validity.
- **Mapping**: B-rep validity benchmark.

### B5. AutoBrep — Autoregressive B-Rep Generation
- **URL**: https://arxiv.org/abs/2512.03018
- **Code**: https://github.com/AutodeskAILab/AutoBrep (MIT)
- **Venue**: SIGGRAPH Asia 2025
- **Method**: Unified tokenization (latent geometry tokens + topological-reference tokens); breadth-first face-adjacency traversal; native autocompletion.
- **Mapping**: SOTA 2025 generator.

### B6. DTGBrepGen — Decoupling Topology and Geometry
- **URL**: https://arxiv.org/abs/2503.13110 ; code https://github.com/jinli99/DTGBrepGen
- **Venue**: 2025
- **Mapping**: B-rep generation.

### B7. CMT — Cascade MAR with Topology Predictor
- **URL**: https://arxiv.org/abs/2504.20830
- **Venue**: 2025
- **Result**: On ABC unconditional: **+10.68% Coverage, +10.3% Valid ratio** over SOTA; on mmABC image-conditioned: **+4.01 CD**.
- **Dataset**: mmABC (1.3M B-rep models).
- **Mapping**: Validity benchmark.

### B8. HiDiGen — Hierarchical Diffusion for B-Rep
- **URL**: https://arxiv.org/abs/2604.02847
- **Venue**: 2026
- **Mapping**: Two-stage hierarchical diffusion.

### B9. TG-Diff — Discrete Topology + Topology-Conditioned Geometry
- **URL**: https://arxiv.org/abs/2607.21928
- **Venue**: 2026
- **Mapping**: D3PM discrete topology + DiT for surfaces.

### B10. ParaCAD — Autoregressive B-Rep with Parametric Surfaces
- **URL**: https://arxiv.org/abs/2607.17093
- **Venue**: 2026
- **Mapping**: Surface-centric tokenization.

### B11. BrepARG — Holistic Token Sequence
- **URL**: https://arxiv.org/abs/2601.16771
- **Venue**: 2026
- **Mapping**: Holistic-token-sequence encoding.

### B12. k-Cell Particles ("Flatten The Complex")
- **URL**: https://arxiv.org/abs/2601.17733
- **Venue**: 2026
- **Mapping**: Compositional k-cell particle sets.

### B13. BrepForge — Factorized B-rep Synthesis
- **URL**: https://arxiv.org/abs/2605.19411
- **Venue**: 2026
- **Mapping**: Wireframe composition + boundary-conditioned surfaces.

### B14. Topology-First B-Rep Meshing
- **URL**: https://arxiv.org/abs/2604.02141
- **Venue**: 2026
- **Method**: Treats B-rep topology as invariant during meshing.
- **Mapping**: Algorithmic correctness.

### B15. NeuroNURBS — Surface-Parametric CAD
- **URL**: https://arxiv.org/abs/2411.10848
- **Venue**: 2024
- **Mapping**: Reduces BrepGen FID from 30.04 → 27.24.

---

## Section C — B-rep Feature Recognition (repair preprocessing)

### C1. BRepFormer (Dai et al., ICMR 2025)
- **URL**: https://arxiv.org/abs/2504.07378
- **Method**: Transformer that fuses face/edge geometry and topology.
- **Datasets**: MFInstSeg, MFTRCAD, **CBF (20,000 B-rep models, new)**.
- **Mapping**: Repair preprocessing.

### C2. BRepMAE (Yao et al., 2026)
- **URL**: https://arxiv.org/abs/2602.22701
- **Method**: Masked graph autoencoder over Geometric Attributed Adjacency Graph.
- **Result**: High recognition rates with **as little as 0.1%** labeled data.
- **Mapping**: Sample-efficient feature recognition.

### C3. FeatureFox (Fuchs et al., 2026)
- **URL**: https://arxiv.org/abs/2604.26770
- **Method**: Binary edge classifier + panoptic graph segmentation.
- **Result**: PQ > 0.9 with only ~250 training parts.
- **Mapping**: Sample-efficient MFR.

### C4. Older baselines (lineage)
- AAGNet, BRT-Net, BR-IPA, HierCAD, MFInstSeg, BRT (arXiv 2504.07134).

---

## Section D — LLM + Geometric-Verifier Pipelines (Direct M2 Matches)

### D1. CADReasoner (Kabisov et al., 2026)
- **URL**: https://arxiv.org/abs/2603.29847
- **Method**: Outputs CadQuery Python; rendered mesh fed back at each step; iterates by minimizing geometric discrepancy.
- **Datasets**: DeepCAD, Fusion 360, MCB.
- **Mapping**: **M2** (rendered-mesh geometric discrepancy).

### D2. Embodied CAD (Liu et al., 2026)
- **URL**: https://arxiv.org/abs/2606.31252
- **Method**: LLM agent with L0–L4 CAD skill library; solver feedback for planning, repair, learning; GRPO refinement.
- **Mapping**: **M1+M2** (kernel-as-M2-verifier).

### D3. AgentsCAD (George et al., 2026)
- **URL**: https://arxiv.org/abs/2607.02448
- **Method**: STEP → B-rep → overhang detection (≥45°) → face-adjacency topology → GraphSAGE semantic feature labels → Claude Sonnet design-reasoning agent → **GPT-4o vision-language verifier** for geometric integrity.
- **Mapping**: **M2** (multi-agent + visual verifier).

### D4. STEP-LLM (Shi et al., DATE 2026)
- **URL**: https://arxiv.org/abs/2601.12641
- **Method**: ~40K STEP-caption pairs; DFS reserialization of B-rep graph; CoT annotations; RAG; **RL with Chamfer Distance geometric reward**.
- **Mapping**: **M2** (geometric reward).

### D5. Text-to-CadQuery (Xie & Ju, 2025)
- **URL**: https://arxiv.org/abs/2505.06507
- **Code**: https://github.com/Text-to-CadQuery/Text-to-CadQuery
- **Result**: Best model **69.3% top-1 exact match; 48.6% Chamfer reduction**.
- **Mapping**: M0 with Chamfer-distance verification.

### D6. CAD-Coder (Doris et al., 2025)
- **URL**: https://arxiv.org/abs/2505.14646
- **Code**: https://github.com/anniedoris/CAD-Coder
- **Result**: **100% valid syntax rate**; highest 3D solid similarity; outperforms GPT-4.5 and Qwen2.5-VL-72B.
- **Mapping**: M0 with 3D solid similarity check.

### D7. Zero-to-CAD (Ataei et al., 2026)
- **URL**: https://arxiv.org/abs/2604.24479
- **Method**: Agentic LLM-in-CAD-environment search for ~1M executable sequences.
- **Mapping**: **M2** (iteratively validates generated code).

### D8. AssemCAD (Dong et al., 2026)
- **URL**: https://arxiv.org/abs/2607.05123
- **Method**: Builds Assembly Specification with typed parts + geometry-backed ports; **validates declared interfaces using concrete B-Rep geometric evidence**.
- **Mapping**: **M2** (assembly-level geometric verification).

### D9. FllumaOne (Zhan, 2026)
- **URL**: https://arxiv.org/abs/2606.17696
- **Performance (Qwen2.5-Coder-1.5B LoRA, 10k test split)**: 99.98% Python syntax validity; 99.97% Flluma build success; **99.14% STEP-export validity**; mean normalized Chamfer Distance 0.002124.
- **Mapping**: **M2** (full kernel-validator-in-loop pipeline) — the most explicit published pipeline.

### D10. MUSE (Dong et al., 2026)
- **URL**: https://arxiv.org/abs/2605.28579
- **Project**: https://dong7313.github.io/muse-benchmark/
- **Method**: Three-stage evaluation — code check → geometric check → design-intent alignment.
- **Mapping**: **M2** (benchmark for executable + geometric + design intent).

### D11. HistCAD (Dong et al., 2025-2026)
- **URL**: https://arxiv.org/abs/2602.19171
- **Method**: Records sketch primitives + constraints + feature ops + 3D boundary references.
- **Metrics**: Edit Reachability (ER), conditional Preserved Constraint Satisfaction Rate (cPCSR), Overall Editable Success (OES).
- **Mapping**: **M2** (constraint-aware parametric editability).

### D12. CADCON (Yang Xiao, 2026)
- **URL**: https://arxiv.org/abs/2607.23191
- **Method**: Re-scores conditioned generation by **independent geometric B-rep assertions** (not text/token metrics); derangement control.
- **Mapping**: **Methodological caution** for M2 measurement.

### D13. Text2CAD-Bench (Wang et al., 2026)
- **URL**: https://arxiv.org/abs/2605.18430
- **Method**: 600 curated examples L1–L4; multi-level evaluation framework.
- **Mapping**: Benchmark.

---

## Section E — Neural SDF + Verifier Methods

| Work | URL | Note |
|---|---|---|
| **DualBrep** (SIGGRAPH 2026) | https://arxiv.org/abs/2606.31579 | SDF (geometry) + UDF (topology) |
| **NH-Rep** (SIGGRAPH Asia 2022) | https://arxiv.org/abs/2209.10191 | Boolean tree over neural halfspace implicits |
| **NeurCADRecon** (SIGGRAPH 2024) | https://arxiv.org/abs/2404.13420 | Neural SDF with developability term |
| **UCSG-Net** (NeurIPS 2020) | https://arxiv.org/abs/2006.09102 | CSG parse trees + differentiable indicator |
| **NeurCross** (SIGGRAPH 2025) | https://arxiv.org/abs/2405.13745 | Neural SDF + cross fields |
| **ODW-loss scheduling** (ISVC 2025) | https://arxiv.org/abs/2511.03147 | Up to 35% CD improvement |

---

## Section F — Geometric Query Tools (primitives for M2)

| Query / Check | Open-source tool |
|---|---|
| Bbox | OCCT `Bnd_Box`; FreeCAD `BoundBox` |
| Volume | OCCT `BRepGProp`; FreeCAD `Part.Shape.Volume` |
| Centroid | OCCT `BRepGProp` |
| Symmetry | CAGD literature; no native OCCT |
| Self-intersection | OCCT `BRepCheck_SelfIntersectingWire` |
| Euler formula / V−E+F | OCCT `BRepCheck_Analyzer` |
| Continuity | OCCT `BRepCheck_NotG1` |
| Distance / closest-point | OCCT `BRepExtrema_DistShapeShape` |
| Void count / multi-solids | OCCT `TopExp_Explorer` |
| Sheet body vs solid | OCCT `BRepCheck_Shell` orientation |

---

## Headline numbers for M2 benchmarking

| Metric | Best published result | Source |
|---|---|---|
| B-rep validity rate (direct generation) | **82%** | HoLa (arXiv 2504.14257) |
| STEP-export validity (LLM-CAD) | **99.14%** | FllumaOne (arXiv 2606.17696) |
| CadQuery Python validity (LLM-CAD) | **100% syntax, 69.3% top-1 exact match** | CAD-Coder (2505.14646), Text-to-CadQuery (2505.06507) |
| B-rep Coverage (ABC unconditional) | **+10.68%** over SOTA | CMT (2504.20830) |
| B-rep Valid ratio (ABC unconditional) | **+10.3%** over SOTA | CMT (2504.20830) |
| MFR panoptic quality | PQ > 0.9 with ~250 parts | FeatureFox (2604.26770) |
| Feature recognition sample efficiency | 0.1% labeled data sufficient | BRepMAE (2602.22701) |

---

## Coverage summary

| Subcategory | # works | Closest M-method |
|---|---|---|
| Open-source kernel (OCCT) | 5+ classes | **M2 floor** |
| Open-source constraint solver | 1 (FreeCAD) | M1+M2 floor |
| Commercial kernel (ACIS / Parasolid) | 2 | M2 industry floor |
| Commercial STEP validator | 3+ | M2 industry floor |
| Neural B-rep generators (validity-aware) | 15 | M2 implicit |
| B-rep feature recognition | 4 | M2 preprocessing |
| LLM + geometric verifier pipelines | 13+ | **M2 direct competitors** |
| Neural SDF verifiers | 6+ | M2 soft |
| Geometric query primitives | 10+ | M2 primitives |

**Critical observation**: The C4 category is now extremely well-populated.
**The project's KQP design sits among 13+ recent LLM + geometric-verifier
pipelines (D1–D13 above).** However, the project uniquely combines the
**OCCT-style structured kernel queries** (bbox, void count, symmetry,
continuity) with **FreeCAD-style constraint-solver feedback** in a
**repair setting** with **CED metric** on **Fusion360-derived IR**. None
of the 13 LLM + verifier works performs this specific combination on
this specific dataset.
