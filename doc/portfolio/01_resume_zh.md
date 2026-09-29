# 项目经历 · 简历版（精炼）

> **目标岗位**：华为 工业智能体研究岗
> **适用场景**：简历中的"项目经历"或"科研项目"栏目（200-400 字）
> **可直接复制到简历**

---

## 项目 1：面向工业 CAD 生成的迭代式多通道验证反馈智能体
**时间**：2026.04 – 2026.08
**角色**：项目主导（设计、实验、理论框架、benchmark 发布）
**核心技术栈**：LLM (ZHIPU glm-5.1)、OpenCASCADE、FreeCAD Sketcher、kiwisolver、Python

### 项目简介
针对 LLM 直接生成工业 CAD 质量低、错误难定位的问题，构建了基于
**求解器内核（Solver） + 几何内核（Kernel）双通道反馈**的迭代式 CAD
智能体；提出 **CGVM（CAD Generation Verification Module）** 概念与
**Action-Feedback Alignment** 理论框架，建立了 138 例扰动驱动的 CAD
修复基准。

### 关键成果
1. **构建 138 例扰动驱动基准**：覆盖 9 类几何扰动（envelope / extrude / radius
 / void count / extent type / inner-outer 关系），配套 KQP（Kernel Query
 Protocol）协议与 CED（CAD Edit Distance）操作级编辑距离。
2. **完成 480 次受控消融实验**（4 方法 × 120 三元组），证明 **KQP-only
 反馈通道（M2）达到 92.5% 一次修复成功率**，显著优于无反馈（M0 =75.8%,
 p=0.0002）与求解器反馈（M1 =67.5%, p<0.0001）。
3. **发现"反馈通道非单调增益"反直觉现象**：M2 + M3（合并反馈）显著
 **不优于** M2 单独（89.2% vs 92.5%, p=0.45 n.s.），揭示了**几何内核反馈的
 修复行动对齐度（action alignment）显著高于求解器反馈**。
4. **提出 PCRR（Problem Candidate Reduction Rate）指标**：基于
 problem space 而非 action space 衡量反馈的"行动约束能力"，将反馈-行动
 映射解耦为 CGVM 责任与 LLM 工程知识两个独立环节。
5. **系统化文献综述**：覆盖约 95 篇相关工作，归纳出 12 类 CGVM
（视觉/执行/求解器/几何意图/LLM 语义/CSG 程序/可编辑性/工程知识/
 隐式场/多模态混合/特征识别/训练时）与 5 个正交维度（参考类型/匹配机制/
 应用时机/行动对齐/诊断粒度）。
6. **首篇论文筹备中**：CGVM Benchmark and Action-Feedback Alignment Framework，
 投稿方向：顶会 workshop / benchmark paper（ICML, NeurIPS, ACL area）。

### 个人贡献
- 设计了 CGVM 分类体系与 Action-Feedback Alignment 理论框架
- 实现 OCCT / CadQuery / FreeCAD Sketcher 的诊断反馈通道
- 完成 4 方法消融实验 + McNemar 显著性检验
- 提出 PCRR 指标与 problem space 形式化定义
- 主笔 5 份研究文档（综述、taxonomy、action taxonomy、framework 评估、PCRR 提案）

---

## 项目 2（推荐补充）：CGVM 文献综述与 12 类验证模块分类
**时间**：2026.06 – 2026.07
**角色**：综述主导

针对"CAD 生成验证"领域缺乏系统化分类的问题，调研了约 95 篇相关工作
（Text2CAD、CAD-Recode、CAD-Coder、GenCAD、CSGNet、ComplexGen、BrepGen、
 AutoBrep、HoLa、UV-Net、SolidGen、Embodied CAD、CAD-Editor、HistCAD 等），
从 4 类原始 CGVM 涌现出 **12 类分类体系**（按 5 个正交维度组织：参考类型/
 匹配机制/应用时机/行动对齐/诊断粒度），识别出 6 个新研究空白
（Knowledge-Driven、LLM-Semantic、CSG-Program vs Geometry Intent 张力、
 Multi-Modal Hybrid 组合规则、Training-Time vs Inference-Time、Feature Recognition
 作为反馈环）。

---

## 技能关键词（用于简历筛选）

**LLM / Agent**：LLM Agent 闭环、Iterative Repair、Self-Debug、Reflection
**CAD / 几何**：OpenCASCADE、CadQuery、FreeCAD Sketcher、B-rep、Sketch-and-Extrude
**求解 / 优化**：kiwisolver、Constraint Solver、GCS、Topological Invariant
**Benchmark / 评估**：138 扰动驱动基准、McNemar 检验、Success@K、CED、
 Detection Recall、Localization Coverage、Diagnostic Specificity
**理论框架**：CGVM 分类、Action-Feedback Alignment、PCRR 指标

---
