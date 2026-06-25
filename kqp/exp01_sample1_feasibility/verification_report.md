# Exp01 验证报告：Kernel Query Program 对 Sample 1 的可行性验证

> **实验目标**：以第一个 sanity sample（`100243_9fb796fe_0005`，1.9×1.9 矩形 → OneSide 拉伸 20.0）为例，手写 KQP 查询其 STEP 文件的拓扑/尺寸/特征/健康指标，与 JSON GT 数据逐项比对，验证"Kernel Query Program 能否通过 OpenCascade 正确读取并验证 CAD 生成结果"。

---

## 1. Sample 建模序列回顾

| 步骤 | 操作 | 具体参数 |
|---|---|---|
| 1 | 在 XZ 基准平面创建 Sketch1 | plane origin=(0,0,0), normal=(0,1,0) |
| 2 | 画 1.9×1.9 矩形轮廓 | 4 条 SketchLine，5 个 Point3D |
| 3 | 添加水平/垂直约束 | 2×Horizontal + 2×Vertical |
| 4 | 添加驱动尺寸 | 2×SketchLinearDimension，value=1.9, is_driving=true |
| 5 | 选择封闭 profile | 1 profile, 1 outer loop, 4 curves |
| 6 | OneSide 拉伸 20.0 | NewBodyFeatureOperation, distance=20.0, taper=0.0 |

**JSON GT (properties)**:
- body=1, shell=1, face=6, edge=12, vertex=8, loop=6
- bbox min=(-58.278, 0.0, 12.040), max=(-56.378, 20.0, 13.940)
- bbox size: x=1.9, y=20.0, z=1.9
- volume=72.2, area=159.22
- surface_types: PlaneSurfaceType×6
- center_of_mass: (-57.328, 10.0, 12.990)

---

## 2. KQP 查询的指标

KQP 通过 OpenCascade (OCP 7.8.x, cadquery 2.8.0) 直接读取 STEP 文件，查询以下四类指标：

### A 类：拓扑查询（6 项）

| 指标 | KQP 实现 | GT 值 | KQP 结果 | 匹配 |
|---|---|---|---|---|
| body_count | `TopTools_IndexedMapOfShape(shape, TopAbs_SOLID).Extent()` | 1 | **1** | ✅ |
| shell_count | `TopTools_IndexedMapOfShape(shape, TopAbs_SHELL).Extent()` | 1 | **1** | ✅ |
| face_count | `TopTools_IndexedMapOfShape(shape, TopAbs_FACE).Extent()` | 6 | **6** | ✅ |
| edge_count | `TopTools_IndexedMapOfShape(shape, TopAbs_EDGE).Extent()` | 12 | **12** | ✅ |
| vertex_count | `TopTools_IndexedMapOfShape(shape, TopAbs_VERTEX).Extent()` | 8 | **8** | ✅ |
| wire_count | `TopTools_IndexedMapOfShape(shape, TopAbs_WIRE).Extent()` | — | **6** | (JSON 无此字段) |

> **关键发现**：必须使用 `TopTools_IndexedMapOfShape` 做**去重计数**。`TopExp_Explorer` 递归遍历会重复计算共享边/顶点（本例 edge=24, vertex=48，是 GT 的 2 倍）。去重后结果完全精确。

### B 类：尺寸查询（9 项）

| 指标 | KQP 实现 | GT 值 (cm) | KQP 结果 (mm→cm) | 匹配 |
|---|---|---|---|---|
| bbox_x (width) | `Bnd_Box` 尺寸 ×0.1 | 1.9 | **1.9** | ✅ |
| bbox_y (height) | 同上 | 20.0 | **20.0** | ✅ |
| bbox_z (depth) | 同上 | 1.9 | **1.9** | ✅ |
| height_along_normal | bbox 沿 sketch_normal=(0,1,0) 投影 | 20.0 | **20.0** | ✅ |
| in_plane_side_1 | 非拉伸轴尺寸 | 1.9 | **1.9** | ✅ |
| in_plane_side_2 | 非拉伸轴尺寸 | 1.9 | **1.9** | ✅ |
| volume | `BRepGProp.VolumeProperties` ×0.1³ | 72.2 | **72.2** | ✅ |
| surface_area | `BRepGProp.SurfaceProperties` ×0.1² | 159.22 | **159.22** | ✅ |
| center_of_mass | `GProp.CentreOfMass` ×0.1 | (-57.328, 10.0, 12.990) | **(-57.328, 10.0, 12.990)** | ✅ |

> **关键发现**：STEP 内部单位是 **毫米**，JSON properties 单位是 **厘米**。转换系数 `×0.1`（长度）、`×0.001`（体积）、`×0.01`（面积）。转换后所有 9 项尺寸指标与 GT 完全匹配。

### C 类：特征查询（4 项）

| 指标 | KQP 实现 | GT 值 | KQP 结果 | 匹配 |
|---|---|---|---|---|
| surface_type=Plane | `BRep_Tool.Surface(face).DynamicType().Name()` | PlaneSurfaceType ×6 | **Plane ×6** | ✅ |
| all_faces_planar | 每个 face 的 Surface DynamicType == "Geom_Plane" | 隐含（6 面) | **true** | ✅ |
| planar_face_count | — | — | **6** | ✅ (GT face_count=6) |
| cylinder_face_count | — | — | **0** | ✅ (无孔) |

> GT 用 `PlaneSurfaceType` 命名，KQP 用 `Geom_Plane` → 去掉 `Geom_` 前缀后映射为 `Plane`。KQP compiler 需要建立 `Geom_*` → `*SurfaceType` 的映射表（如 `Geom_Plane→PlaneSurfaceType`，`Geom_CylindricalSurface→CylindricalSurfaceType`）。

### D 类：健康查询（3 项）

| 指标 | KQP 实现 | 期望 | KQP 结果 | 匹配 |
|---|---|---|---|---|
| is_solid | shape.ShapeType() == TopAbs_SOLID | true | **true** | ✅ |
| euler_characteristic | V-E+F = 8-12+6 | 2 (闭体) | **2** | ✅ |
| euler_check | 与理论值比较 | 2 | **2==2** | ✅ |

---

## 3. 逐项比对汇总

| 类别 | 查询项数 | 完全匹配 | 偏差 | 备注 |
|---|---|---|---|---|
| A 拓扑 | 5 (与 GT 对比) | **5/5** | 0 | 去重计数法正确 |
| B 尺寸 | 9 | **9/9** | 0 | mm→cm 转换正确 |
| C 特征 | 3 (与 GT 对比) | **3/3** | 0 | 曲面类型映射需建表 |
| D 健康 | 2 (与 GT 对比) | **2/2** | 0 | 欧拉校验通过 |
| **合计** | **19** | **19/19** | **0** | **100% 精确匹配** |

---

## 4. 实验中发现的关键技术细节

### 4.1 单位转换（mm vs cm）

Fusion360 Gallery 的 STEP 文件（由 ST-Developer/STEP Tools 生成）内部使用**毫米**，而 JSON `properties` 中的数值（bounding_box、volume、area、center_of_mass）使用**厘米**。转换规则：

| 物理量 | STEP → JSON | 系数 |
|---|---|---|
| 长度（坐标、距离、半径） | mm → cm | ×0.1 |
| 面积 | mm² → cm² | ×0.01 |
| 体积 | mm³ → cm³ | ×0.001 |

> **KQP compiler 必须在输出期望值时标注单位，并在比对时统一单位**。建议：KQP 输出始终使用 mm（内核原生），比对时根据 JSON properties 的 cm 值做转换。

### 4.2 拓扑计数：去重 vs 递归

| 方法 | body | shell | face | edge | vertex | 与 GT 匹配 |
|---|---|---|---|---|---|---|
| `TopExp_Explorer`（递归） | 1 | 1 | 6 | **24** | **48** | ❌ edge/vertex ×2 |
| `TopTools_IndexedMapOfShape`（去重） | 1 | 1 | 6 | **12** | **8** | ✅ 完全匹配 |

原因：`TopExp_Explorer` 对每个 face 的 wire 中的边/顶点独立计数，共享边被重复计入。`IndexedMapOfShape` 通过 handle 去重，与 Fusion360 的 `*_count` 定义一致。

> **KQP 必须使用 `TopTools_IndexedMapOfShape`**，这是本实验最重要的技术发现之一。

### 4.3 OCP API 版本差异

本环境 cadquery 2.8.0 绑定的 OCP 与网上教程/文档有以下差异：

| 教程写法 | 实际 OCP | 正确写法 |
|---|---|---|
| `topods.Face(...)` | 无此模块 | `TopoDS.Face(...)` |
| `BRep_Tool.Surface_(...)` | 无此方法 | `BRep_Tool.Surface_s(...)` |
| `brepbndlib_Add(...)` | 无此函数 | `BRepBndLib.Add_s(...)` |
| `brepgprop_VolumeProperties(...)` | 无此函数 | `BRepGProp.VolumeProperties_s(...)` |
| `surf.DynamicType()` 返回 str | 返回 `Standard_Type` 对象 | `surf.DynamicType().Name()` |
| `BRep_Tool.Surface_s` 返回 copy | 可能返回 copy | 2-arity 版本接受 Location 参数 |

> 这是 OCP 7.8.x 的 pybind11 封装特征。KQP compiler 应封装一套 `ocp_helpers.py` 来屏蔽这些差异。

### 4.4 曲面类型映射

| OCP `DynamicType().Name()` | Fusion JSON `surface_type` | 映射 |
|---|---|---|
| `Geom_Plane` | `PlaneSurfaceType` | Plane → PlaneSurfaceType |
| `Geom_CylindricalSurface` | `CylindricalSurfaceType` | 需验证 |
| `Geom_ConicalSurface` | `ConicalSurfaceType` | 需验证 |
| `Geom_SphericalSurface` | `SphericalSurfaceType` | 需验证 |
| `Geom_ToroidalSurface` | `ToroidalSurfaceType` | 需验证 |
| `Geom_BSplineSurface` | `BSplineSurfaceType` | 需验证 |

---

## 5. 结论

**Kernel Query Program 可行性验证通过。**

- KQP 通过 OpenCascade 直接读取 STEP 文件，**19/19 项指标与 JSON GT 100% 精确匹配**。
- 四类查询（拓扑/尺寸/特征/健康）**全部可执行**，返回结果正确。
- 三个关键工程细节已确认：① mm→cm 单位转换 ② `IndexedMapOfShape` 去重计数 ③ OCP pybind11 API 封装差异。
- 下一步可基于此经验实现确定性 KQP compiler，将"JSON properties → KQP"的映射自动化。
