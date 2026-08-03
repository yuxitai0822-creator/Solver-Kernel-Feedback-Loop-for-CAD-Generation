# Category C2 — Iterative / Agentic / Self-Reflective Code Generation

> **Closest M-method**: M0+self-reflection (between M0 and M1)
> **Survey count**: 14 works (2021–2025)

---

## Works Surveyed

### 1. Reflexion (Shinn et al., NeurIPS 2023)
- **Method**: Verbal self-reflection; agent maintains reflective text in memory
- **Feedback**: Self-reflection (no external verifier)
- **Result**: **+11 pp on HumanEval** (91% pass@1 with GPT-4 vs. 80% baseline)
- **Mapping**: M0+reflection (between M0 and M1)

### 2. Self-Debug (Chen et al., EMNLP Findings 2023)
- **Method**: LLM prompted with code-execution feedback
- **Feedback**: Runtime trace + few-shot examples
- **Result**: **+12%** on Text-to-Code tasks
- **Mapping**: M0+execution (close to M1 conceptually)

### 3. Self-Refine (Madaan et al., NeurIPS 2023)
- **Method**: Same-LLM iterative refine → critique → edit
- **Result**: +20 pp on math reasoning, +8 pp on code
- **Mapping**: M0+reflection

### 4. Tree of Thoughts — ToT (Yao et al., NeurIPS 2023)
- **Method**: Tree search with LLM as evaluator
- **Result**: **74%** on Game of 24 (vs. 4% CoT)
- **Mapping**: M0+search

### 5. RAP (Reasoning via Planning) (Hao et al., ICML 2023)
- **Method**: LLM as world model + reasoning agent
- **Result**: **+33%** plan accuracy on plan generation
- **Mapping**: M0+world-model

### 6. LATS (Language Agent Tree Search) (Zhou et al., 2024)
- **Method**: MCTS + LLM + external feedback
- **Result**: **92.7%** on HumanEval
- **Mapping**: M0+MCTS

### 7. Voyager (Wang et al., NeurIPS 2023)
- **Domain**: Minecraft (3D environment)
- **Method**: LLM + skill library + execution feedback + self-verification
- **Significance**: **Closest 3D-environment analogue to CAD agent**
- **Mapping**: M0+execution+reflection

### 8. SWE-Agent (Yang et al., 2024)
- **Domain**: SWE-bench
- **Result**: **12.5% pass@1**
- **Significance**: Architecture analogous to CAD design agent with iterative patching
- **Mapping**: M0+repo-tools

### 9. AutoCodeRover (Zhang et al., 2024)
- **Domain**: SWE-bench-lite
- **Result**: **19%** pass@1
- **Mapping**: M0+repo-tools

### 10. Self-Repair (Lezama, 2023)
- **Method**: Interpreter-feedback code repair
- **Mapping**: M0+execution

### 11. AgentCoder
- **Method**: Multi-agent code generation with execution feedback
- **Mapping**: M0+multi-agent

### 12. CodeAct (Wang et al., 2024)
- **Method**: Executable code actions (vs. JSON)
- **Result**: **+20%** over JSON actions
- **Mapping**: M0+execution; closest to CAD agent design

### 13. AlphaCode 2 (DeepMind, 2023)
- **Method**: Search + LLM
- **Domain**: Codeforces
- **Mapping**: M0+search

### 14. PAL (Program-Aided Language Models) (Gao et al., 2023)
- **Method**: Code execution as reasoning
- **Result**: **+15%** on GSM8K
- **Mapping**: M0+execution

### 15. LEVER (Ni et al., 2023)
- **Method**: Verifier-trained reranker
- **Mapping**: M0+verifier-reranking

### 16. CodeRL
- **Method**: RL-trained code model with execution feedback
- **Mapping**: M1 (RL-as-verifier)

---

## Coverage summary

All works target **code generation**, not CAD specifically. The closest
**3D-environment analogue** is Voyager (Minecraft).

| Feedback type | # works | Representative |
|---|---|---|
| Self-reflection | 4 | Reflexion, Self-Refine |
| Execution feedback | 5 | Self-Debug, CodeAct, PAL |
| Tree search | 3 | ToT, RAP, LATS |
| Multi-agent | 2 | AgentCoder, SWE-Agent |
| RL-based | 2 | CodeRL, AlphaCode 2 |
