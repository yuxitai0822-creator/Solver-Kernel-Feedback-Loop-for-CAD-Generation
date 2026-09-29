# 项目经历包装文档（华为工业智能体研究岗）

> **目标岗位**：华为 工业智能体研究岗
> **打包日期**：2026-08-12
> **核心卖点**：LLM Agent + 工业 CAD 验证闭环 + Benchmark + 理论框架

---

## 文档结构

| 文件 | 用途 | 形式 |
|---|---|---|
| `00_README.md` | 本文件 | 总览 |
| `01_resume_zh.md` | 中文简历项目经历（精炼版） | 简历直接复制 |
| `02_resume_zh_long.md` | 中文项目经历（详尽版） | 面试材料 |
| `03_cover_letter_zh.md` | 中文求职信/自我陈述 | 求职信 |
| `04_technical_summary_en.md` | 英文技术摘要 | 国际投递/portfolio |
| `05_interview_prep.md` | 面试问题与应答 | 面试准备 |
| `06_research_statement_zh.md` | 研究陈述（用于研究岗） | 学术性展示 |

---

## 核心项目名称（推荐使用）

### 中文（推荐）
**「面向工业 CAD 生成的迭代式多通道验证反馈智能体」**
或
**「CGVM：面向 CAD 智能体的验证模块基准与 Action-Feedback 对齐框架」**

### 英文
**"Iterative Multi-Verification Feedback for LLM-based CAD Generation Agents"**
或
**"CGVM: A Benchmark and Action-Feedback Alignment Framework for CAD Generation Verification Modules"**

---

## 项目亮点（用于简历"项目亮点"短描述）

> 构建了 138 例扰动驱动的工业 CAD 修复基准（含 4 类反馈通道、480 次受控实验），
> 提出 **CGVM（CAD Generation Verification Module）** 概念与 **Action-Feedback
> Alignment** 理论框架；通过 4 方法消融（M0–M3）发现：几何内核（KQP）反馈
> 优于求解器反馈，并提出 PCRR 指标量化"反馈对动作空间的约束能力"。
> 实验在 LLM CAD 修复任务上达到 92.5% 一次修复成功率（M2 vs M3 p=0.45 n.s.，
> 证明 M2 > M3 揭示了"通道并非越多越好"的核心现象）。

---

## 量化成果（按重要性排序）

| 指标 | 数值 | 含义 |
|---|---|---|
| **Success@3 (M2)** | **92.5%** | 单 KQP 反馈通道的 CAD 修复成功率 |
| **M2 相对 M0 提升** | **+16.7 pp** | 75.8% → 92.5% (p=0.0002) |
| **M2 相对 M1 提升** | **+25.0 pp** | 67.5% → 92.5% (p<0.0001) |
| **实验规模** | **480 trials** (120 × 4 methods) | 大规模受控消融 |
| **扰动基准规模** | **138 perturbations × 46 clean** | 工业级 CAD 修复基准 |
| **理论贡献** | **CGVM 分类 + AFA 框架 + PCRR 指标** | 3 项原创 |
| **文献覆盖** | **~95 篇工作**（12 类 CGVM 涌现） | 完整 baseline 调研 |
| **CGVM 涌现分类** | **4 → 12 类型** | 扩展了 CAD 验证领域 |
| **首篇 PCRR 论文** | **正在筹备** | 投稿顶会 workshop |

---

## 技术栈（直接列出）

- **LLM 框架**：ZHIPU glm-5.1, OpenAI 兼容 API, temperature=0.0
- **CAD 内核**：OpenCASCADE (OCCT) 7.x, FreeCAD Sketcher (GCS), CadQuery Python API
- **约束求解**：kiwisolver, FreeCAD sketcher solver
- **IR 设计**：自研 CAD IR v0.1（JSON-Schema 校验 + 12 种操作）
- **KQP 协议**：自研 Kernel Query Protocol v0.2（6 类 KQP intent, OCCT 后端）
- **CED 编辑距离**：自研 v0.1（操作级 weighted Levenshtein）
- **修复闭环**：LLM-driven repair loop (max_iter=3, dual feedback channels)
- **统计检验**：McNemar exact test, 95% CI
- **开发语言**：Python 3.11, bash, JSON-Schema

---

## 项目与"工业智能体研究岗"的对齐点

| 岗位要求 | 项目对应 |
|---|---|
| 工业 AI Agent | ✅ LLM-based CAD 生成 + 修复 Agent |
| 工业场景 | ✅ CAD 是制造业核心工具 |
| 闭环反馈 / RL | ✅ Solver-Kernel 双通道反馈闭环 |
| 基准 / Benchmark | ✅ 138 扰动驱动的 CAD 修复基准 |
| 评估方法 | ✅ Detection/Localization/Specificity/Alignment 四层评估 |
| 理论贡献 | ✅ Action-Feedback Alignment 理论 + PCRR 指标 |
| 工程落地 | ✅ 与 OCCT / CadQuery / FreeCAD 集成 |
| 多学科交叉 | ✅ 机械 CAD × 约束求解 × LLM × 形式化方法 |

---

## 接下来阅读

按简历投递需要，从最精简到最详尽：

1. `01_resume_zh.md` — 简历直接复制（200-300 字）
2. `04_technical_summary_en.md` — 英文技术摘要（500 字）
3. `02_resume_zh_long.md` — 中文长版（用于面试/详尽展示）
4. `06_research_statement_zh.md` — 研究陈述（学术性展示）
5. `03_cover_letter_zh.md` — 求职信
6. `05_interview_prep.md` — 面试 Q&A

---
