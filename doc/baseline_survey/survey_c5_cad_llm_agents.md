# Category C5 — CAD-Domain LLM Agents (CAD-specific + feedback)

> **Closest M-method**: M2 / M3 (CAD domain + feedback)
> **Survey count**: 20+ works (2022–2026)

---

## Works Surveyed

### Tier 1 — Closest M3 competitors

#### 1. Embodied CAD (Liu et al., 2026)
- **URL**: https://arxiv.org/abs/2606.31252
- **Core**: Solver-grounded LLM agent with stratified L0–L4 CAD skill library
- **Components**: Action grammar + deterministic parameter resolution + solver-derived rewards
- **Training**: SFT warm-up + GRPO refinement
- **Domains**: Mechanical, industrial equipment, mold-oriented assemblies
- **Result**: Solver-grounded planning executes all strong-planner workflows;
  learned controllers reach high executable rates
- **Mapping**: **M1+M2** combined
- **Significance**: **Closest published solver-grounded agent loop**

#### 2. CAD-Coder (NeurIPS 2025)
- **URL**: https://arxiv.org/abs/2505.19713
- **Core**: CadQuery + GRPO + **geometric reward**
- **Mapping**: **M2** (LLM with geometric reward)

#### 3. CADFusion (ICML 2025)
- **URL**: https://arxiv.org/abs/2501.19054
- **Core**: LLM + multi-view **visual feedback** (offline DPO training)
- **Mapping**: **M2** (visual feedback)

#### 4. CADReasoner (Kabisov et al., 2026)
- **URL**: https://arxiv.org/abs/2603.29847
- **Core**: Iterative program editing; rendered mesh → CadQuery edit
- **Datasets**: DeepCAD, Fusion 360, MCB (clean + scan-sim)
- **Mapping**: **M2 / M3** (geometric discrepancy as feedback)

#### 5. GenCAD-Self-Repairing (Tsuji et al., 2025)
- **URL**: https://arxiv.org/abs/2505.23287
- **Core**: Diffusion + regression-based command-sequence correction
- **Result**: **66%** infeasible → feasible
- **Mapping**: **M3 closest in CAD domain**

### Tier 2 — Domain LLM agents

#### 6. CAD-Editor (Yuan et al., Microsoft, 2025)
- **URL**: https://arxiv.org/abs/2502.03997
- **Code**: https://github.com/microsoft/CAD-Editor
- **Core**: Locate-then-infill framework; LLM backbone; LVLM-synthesized training data
- **Mapping**: M3-adjacent (no kernel feedback)

#### 7. CAD-Recode (Rukhovich et al., 2024)
- **URL**: https://arxiv.org/abs/2412.14042
- **Code**: https://github.com/filaPro/cad-recode
- **Core**: LLM-as-decoder for CadQuery; Python output re-editable
- **Mapping**: M0 / M0+edit

#### 8. Aligning Constraint Generation (Casey et al., Autodesk AI Lab, 2025)
- **URL**: https://arxiv.org/abs/2504.13178
- **Project**: https://autodeskailab.github.io/aligning-constraint-generation/
- **Core**: DPO-style alignment with **constraint-solver feedback**
- **Result**: **93%** fully-constrained vs. 34% (SFT) vs. 8.9% (no SFT)
- **Mapping**: **M1 analog**

#### 9. ProCAD (Proactive Clarifying Agent)
- **URL**: https://arxiv.org/abs/2602.03045
- **Core**: Two-agent pipeline (clarifier + CAD coder)
- **Result**: **79.9%** reduction in mean Chamfer vs. Claude Sonnet 4.5;
  invalidity **4.8% → 0.9%**
- **Mapping**: M2 / M3 (clarification as soft feedback)

#### 10. CAD-MLLM (Xu et al., 2024)
- **URL**: https://arxiv.org/abs/2411.04954
- **Project**: https://cad-mllm.github.io/
- **Core**: LLaVA-style MLLM with CAD-command supervision
- **Dataset**: Omni-CAD (~450K multimodal)
- **Mapping**: M0 (multimodal)

#### 11. PLLM (Pseudo-Labeling LLMs for CAD)
- **URL**: https://arxiv.org/abs/2602.12561
- **Core**: Self-training; samples from LLM + selects high-fidelity executions
- **Mapping**: M2 (with execution feedback)

#### 12. CADEvolve
- **URL**: https://arxiv.org/abs/2602.16317
- **Core**: Evolution-based CadQuery with VLM-guided edits
- **Mapping**: M2/M3 (validation feedback)

#### 13. Cosmo-Agent
- **URL**: https://arxiv.org/abs/2604.05547
- **Core**: RL agent revises parametric geometry until constraints satisfied
- **Mapping**: M3 (direct "repair loop" analogue)

### Tier 3 — Adjacent

#### 14. CAD-Llama
- **URL**: https://arxiv.org/abs/2505.04481
- **Core**: LLM adapted to SPCC for parametric CAD code
- **Mapping**: M0 (LLM-tuning baseline)

#### 15. NURBGen (AAAI 2026)
- **URL**: https://arxiv.org/abs/2511.06194
- **Core**: Fine-tuned LLM emits JSON-NURBS
- **Mapping**: M0

#### 16. CMT (Cascade MAR with Topology Predictor)
- **URL**: https://arxiv.org/abs/2504.20830
- **Core**: MAR + topology predictor
- **Result**: +10.68% Coverage, +10.3% Valid ratio (ABC); +4.01 CD on image cond.
- **Dataset**: mmABC (1.3M B-rep multimodal)
- **Mapping**: M0 (with topology)

#### 17. CAD-Tokenizer (ICLR 2026)
- **URL**: https://arxiv.org/abs/2509.21150
- **Mapping**: Tokenization infrastructure

#### 18. PR-CAD
- **URL**: https://arxiv.org/abs/2604.19773
- **Core**: Unifies text-to-CAD gen + edit via RL
- **Mapping**: M3-adjacent

#### 19. ArtiCAD
- **URL**: https://arxiv.org/abs/2604.10992
- **Core**: Multi-agent assembly with rollback
- **Mapping**: M3 (assembly CAD)

#### 20. CADCrafter (CVPR 2025)
- **URL**: https://arxiv.org/abs/2504.04753
- **Core**: Image→parametric CAD; synthetic textureless data
- **Mapping**: M0 (image-conditioned)

---

## Coverage summary

| Subcategory | # works | Closest M-method |
|---|---|---|
| Solver-grounded agents | 2 | M1+M2 (Embodied CAD, Constraint Alignment) |
| LLM + geometric reward | 2 | M2 (CAD-Coder, CADFusion) |
| Iterative program edit | 1 | M2 (CADReasoner) |
| Feasibility-restoring repair | 1 | M3 (GenCAD-Self-Repairing) |
| Multi-agent clarification | 1 | M2/M3 (ProCAD) |
| RL revise-until-valid | 1 | M3 (Cosmo-Agent) |
| MLLM for CAD | 1 | M0 (CAD-MLLM) |
| Other domain LLM | 11+ | M0 / M0+edit |

**Critical observation**: Embodied CAD is the **closest published solver-grounded
agent loop**, but targets *generation*, not *repair*. The project's M3
repair setting remains a **unique** design point.
