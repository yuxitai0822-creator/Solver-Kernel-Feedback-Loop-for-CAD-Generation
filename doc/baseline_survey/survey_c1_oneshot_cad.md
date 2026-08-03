# Category C1 — One-shot Text/Spec → CAD Code Generation

> **Closest M-method**: M0 (no iterative feedback)
> **Survey count**: 13 works (2020–2026)

---

## Works Surveyed

### 1. Text2CAD (Khan et al., NeurIPS 2024)
- **URL**: https://arxiv.org/abs/2409.17106
- **Task**: Text → parametric CAD (sketch+extrude), skill-level varying
- **Backbone**: End-to-end autoregressive transformer
- **Dataset**: DeepCAD (~170K) + ~660K text annotations
- **Mapping**: M0
- **Status**: Spotlight paper

### 2. CAD-Recode (Rukhovich et al., 2024)
- **URL**: https://arxiv.org/abs/2412.14042
- **Code**: https://github.com/filaPro/cad-recode
- **Task**: Point cloud → CAD (reverse engineering)
- **Backbone**: Small pretrained LLM (decoder) + lightweight point-cloud projector
- **Representation**: **Python code** (re-editable by LLMs)
- **Dataset**: 1M procedurally generated sequences; eval on DeepCAD, Fusion360, CC3D
- **Result**: 10× lower mean Chamfer Distance than prior SOTA
- **Mapping**: M0; **M0+edit** via external LLM

### 3. GenCAD (Alam & Ahmed, MIT, 2024)
- **URL**: https://arxiv.org/abs/2409.16294
- **Task**: Image → parametric CAD; also unconditional generation
- **Backbone**: AR Transformer + contrastive vision encoder + diffusion
- **Datasets**: ABC, DeepCAD, Fusion360, CC3D
- **Follow-ups**:
  - **GenCAD-Self-Repairing** (arXiv 2505.23287) — **66%** infeasible → feasible
  - **GenCAD-3D** (arXiv 2509.15246) — multimodal extension
- **Mapping**: M0 (base); M2 (self-repairing variant)

### 4. CAD-MLLM (Xu et al., 2024)
- **URL**: https://arxiv.org/abs/2411.04954
- **Project**: https://cad-mllm.github.io/
- **Task**: Any-modality → parametric CAD
- **Backbone**: LLaVA-style MLLM
- **Dataset**: Omni-CAD (~450K multimodal)
- **Mapping**: M0 (multimodal)

### 5. BrepGen (Xu et al., SIGGRAPH 2024)
- **URL**: https://arxiv.org/abs/2401.15563
- **Code**: https://github.com/samxuxiang/BrepGen
- **Task**: Direct B-rep generation (also autocomplete, interpolation)
- **Method**: Hierarchical tree representation + transformer diffusion
- **Mapping**: M0 (B-rep output)

### 6. SolidGen (Jayaraman et al., TMLR 2023)
- **URL**: https://arxiv.org/abs/2203.13944
- **Task**: Direct B-rep synthesis (class/image/voxel conditioned)
- **Method**: AR Transformer + pointer networks; Indexed B-rep
- **Mapping**: M0

### 7. UV-Net (Jayaraman et al., CVPR 2021)
- **URL**: https://arxiv.org/abs/2006.10211
- **Task**: B-rep supervised + unsupervised learning
- **Method**: CNN+GNN (U,V parameterization)
- **Datasets**: SolidLetters + 5 others
- **Mapping**: M0 (representation baseline)

### 8. DeepCAD (Wu et al., ICCV 2021)
- **URL**: https://arxiv.org/abs/2105.09492
- **Code**: http://www.cs.columbia.edu/cg/deepcad/
- **Task**: CAD autoencoding + random generation
- **Dataset**: 178,238 models with CAD construction sequences
- **Mapping**: M0 (foundational)

### 9. Fusion 360 Gallery (Willis et al., SIGGRAPH 2021)
- **URL**: https://arxiv.org/abs/2010.02392
- **Code**: https://github.com/AutodeskAILab/Fusion360Gallery
- **Task**: CAD reconstruction; **CAD-as-RL** gym
- **Dataset**: 8,625 human design sequences
- **Mapping**: **M0+MDP** (the gym enables agentic use)

### 10. SketchGraphs (Seff et al., 2020)
- **URL**: https://arxiv.org/abs/2007.08506
- **Dataset**: 15M Onshape sketches with constraint graphs
- **Mapping**: M0 (graph-based)

### 11. CSGNet (Sharma et al., TPAMI 2020)
- **URL**: https://arxiv.org/abs/1712.08290
- **Task**: 2D/3D → CSG program
- **Mapping**: M0 (CSG baseline)

### 12. Point2CAD (Liu et al., 2023)
- **URL**: https://arxiv.org/abs/2312.04962
- **Task**: Point cloud → CAD (hybrid analytic–neural)
- **Mapping**: M0

### 13. CADTests
- **URL**: https://arxiv.org/abs/2605.07807
- **Type**: Executable-test benchmark for text-to-CAD
- **Mapping**: Evaluation infrastructure

---

## Coverage summary

| Year range | # works | LLM-era | Iterative? |
|---|---|---|---|
| 2017–2021 | 4 | partial | No |
| 2022–2024 | 6 | mostly | No |
| 2025–2026 | 3+ | yes | Some (GenCAD-SR) |

**Mapping to M0**: Direct, all works.
**Mapping to M0+reflection**: Only via off-the-shelf LLM re-editing (CAD-Recode).
**Mapping to M1–M3**: None.
