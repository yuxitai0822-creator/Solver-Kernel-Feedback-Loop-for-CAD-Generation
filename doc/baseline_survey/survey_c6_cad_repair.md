# Category C6 — CAD Repair / B-rep Editing / Constraint Satisfaction

> **Closest M-method**: M3 (full dual-feedback repair loop)
> **Survey count**: 16+ works (2017–2026)

---

## Works Surveyed

### Tier 1 — Closest M3 competitors (already covered in C5)

#### 1. Embodied CAD (Liu et al., 2026)
- **URL**: https://arxiv.org/abs/2606.31252
- Targets generation, not repair, but provides architectural template.

#### 2. GenCAD-Self-Repairing (Tsuji et al., 2025)
- **URL**: https://arxiv.org/abs/2505.23287
- **66%** infeasible → feasible conversion — the only published feasibility-restoring work.

#### 3. CADReasoner (Kabisov et al., 2026)
- **URL**: https://arxiv.org/abs/2603.29847
- Iterative geometric-mismatch repair.

#### 4. CAD-Editor (Yuan et al., Microsoft, 2025)
- **URL**: https://arxiv.org/abs/2502.03997
- **Code**: https://github.com/microsoft/CAD-Editor
- Text-based CAD editing (intent-driven, not validity-driven).

#### 5. Constraint Alignment (Casey et al., Autodesk, 2025)
- **URL**: https://arxiv.org/abs/2504.13178
- Constraint-solver-in-the-loop constraint generation.

### Tier 2 — Classical / pre-LLM CAD repair

#### 6. B-rep Boolean Repair (Huang et al., 2023)
- **URL**: https://arxiv.org/abs/2310.10351
- **Method**: Set-reasoning inference procedure; per-edge adaptive tolerance
- **Target**: False topological intersection edges from Boolean ops
- **Mapping**: Classical B-rep repair baseline

#### 7. Szalinski (Nandi et al., PLDI 2020)
- **URL**: https://arxiv.org/abs/1909.12252
- **Method**: Equality saturation + inverse transformations
- **Target**: Unstructured mesh → editable CSG program
- **Mapping**: CSG repair baseline

### Tier 3 — Inverse-CSG family

#### 8. CSGNet (Sharma et al., TPAMI 2020)
- **URL**: https://arxiv.org/abs/1712.08290
- **Extended**: https://arxiv.org/abs/1912.11393
- **Method**: Neural encoder–decoder (CNN + stack-augmented RNN) + RL
- **Mapping**: Foundational CSG repair baseline

#### 9. D²CSG (Yu et al., 2023)
- **URL**: https://arxiv.org/abs/2301.11497
- **Method**: Unsupervised dual-branch CSG reconstruction
- **Mapping**: Inverse-CSG

#### 10. DiffCSG (Yuan et al., 2024)
- **URL**: https://arxiv.org/abs/2409.01421
- **Method**: Differentiable rasterization-based CSG optimization
- **Mapping**: Inverse-CSG (differentiable)

### Tier 4 — B-rep feature recognition (repair preprocessing)

#### 11. BRepFormer (Dai et al., ICMR 2025)
- **URL**: https://arxiv.org/abs/2504.07378
- **Dataset**: CBF (20,000 B-rep models)
- **Mapping**: Repair preprocessing

#### 12. BRepMAE (2026)
- **URL**: https://arxiv.org/abs/2602.22701
- **Method**: Masked graph autoencoder for B-rep
- **Mapping**: Repair preprocessing

#### 13. BRT (2025)
- **URL**: https://arxiv.org/abs/2504.07134
- **Method**: B-rep transformer (CAD journal)
- **Mapping**: Repair preprocessing

### Tier 5 — Industry baselines

#### 14. ACIS Healing (Spatial Corp.)
- Whitepaper: *Healing as an Essential Function: Preserving Design Intent in 3D Models*
  https://www.spatial.com/
- Industry standard for B-rep healing

#### 15. Parasolid Healing (Siemens)
- Industry standard, integrated with Teamcenter Visualization

#### 16. 3D_Evolution (CoreTechnologie)
- STEP AP242 import + Intelligent Data Healing + LOTAR GVP STEP validator

#### 17. CADdoctor (Elysium)
- Geometry healing + CAD translation suite

#### 18. TransMagic (TransMagic Inc.)
- Dedicated STEP/IGES repair product

### Tier 6 — Constraint-satisfaction surveys

#### 19. Zou et al., "A Review on Geometric Constraint Solving" (2022)
- **URL**: https://arxiv.org/abs/2202.13795
- **Type**: Survey
- **Coverage**: Classical decomposition-based + modern (classification-based,
  over/under-constrained)

#### 20. Zou & Feng, "On Limitations of the Witness Configuration Method" (2019)
- **URL**: https://arxiv.org/abs/1904.00526
- **Type**: Failure-mode analysis of modern decomposition method

### Tier 7 — Adjacent RL-based CAD repair

#### 21. Cosmo-Agent (Deng et al., 2026)
- **URL**: https://arxiv.org/abs/2604.05547
- **Core**: RL agent that revises parametric geometry until constraints satisfied
- **Mapping**: M3 (direct "repair loop" analogue)

#### 22. PR-CAD (An et al., 2026)
- **URL**: https://arxiv.org/abs/2604.19773
- **Core**: Unifies text-to-CAD gen + edit via RL
- **Mapping**: M3-adjacent

#### 23. CAD-Llama (Li et al., 2025)
- **URL**: https://arxiv.org/abs/2505.04481
- **Core**: LLM adapted to SPCC for parametric CAD code
- **Mapping**: M0 (but with parametric editability)

#### 24. Linkify (Jignasu, Grandi, 2026)
- **URL**: https://arxiv.org/abs/2607.01205
- **Core**: Corrects missing/erroneous contacts in Fusion 360 Gallery assembly dataset
- **Mapping**: Assembly repair baseline

#### 25. ArtiCAD (Shui et al., 2026)
- **URL**: https://arxiv.org/abs/2604.10992
- **Core**: Multi-agent assembly with rollback
- **Mapping**: M3 (assembly)

#### 26. HistCAD (Dong et al., 2025–2026)
- **URL**: https://arxiv.org/abs/2602.19171
- **Core**: Constraint-aware parametric history dataset + benchmark
- **Dataset**: 170,236 executable parametric sequences + STEP + text
- **Metrics**: ER, cPCSR, OES
- **Mapping**: **A dataset directly usable as a perturbation-repair benchmark**

### Other datasets used in C6

| Dataset | arXiv | Use |
|---|---|---|
| **DeepCAD** | 2105.09492 | Baseline source for perturbation |
| **Fusion 360 Gallery** | 2010.02392 | Human design sequences (linkify target) |
| **ABC** | (used in CSGNet, D²CSG, DiffCSG) | CSG repair |
| **MCB** | (CADReasoner) | Reverse engineering |

---

## Coverage summary

| Subcategory | # works | Closest M-method |
|---|---|---|
| Solver-grounded CAD agent | 1 | M3 (Embodied CAD) |
| Feasibility-restoring repair | 1 | M3 (GenCAD-SR) |
| Iterative CAD program edit | 1 | M2/M3 (CADReasoner) |
| Classical B-rep repair | 1 | (algorithmic, no LLM) |
| Inverse-CSG | 3 | CSG repair baseline |
| B-rep feature recognition | 3 | Repair preprocessing |
| Industry B-rep repair | 5 | Industry baseline |
| Constraint-satisfaction | 2 (survey + analysis) | M1 baseline |
| RL-based CAD repair | 3 | M3 (Cosmo-Agent, PR-CAD) |
| Adjacent datasets | 4 (HistCAD, DeepCAD, Fusion360, ABC) | Benchmark |

**Critical observation**: The C6 category confirms there is **no prior work
implementing the project's specific "Solver + KQP dual-feedback on perturbed
Fusion360-derived IR" recipe**. The closest competitors are
- **Embodied CAD** (solver-grounded, but generation)
- **GenCAD-Self-Repairing** (single-channel feasibility repair)
- **CADReasoner** (iterative geometric-mismatch repair)
- **Cosmo-Agent** (RL revise-until-valid)
