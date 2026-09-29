# schema/ — history2cq

## 说明

本模块**没有独立 schema**。

`history2cq` 的输入是 `data/phase0_initial/history/<sid>.json`（Fusion360 Gallery Reconstruction r1.0.1 格式），不属于本模块管理的 schema。

输出（CadQuery Python 源）是代码字符串，由 `core/compiler.py::compile_history()` 确定性生成。