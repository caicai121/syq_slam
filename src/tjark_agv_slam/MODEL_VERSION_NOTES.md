# 模型版本说明

记录时间:2026-05-17
工程:`~/catkin_ws/src/`

> 这份文档用于明确 4 个 `tjark_agv*` 模型包的定位,避免后续把已抛弃的路线误当主线。

---

## v1: `tjark_agv`

- 历史稳定 baseline。
- 早期 gmapping / Cartographer / AMCL 实验主线,跑通过完整的建图+定位流程。
- 已在 commit `fdddedf` 完成 base_link 旋转中心重构,在 commit `fe1fa5f` 封档。
- **保留用途**:历史对照,可能继续作为参考实现。
- **不是当前主线**。

入口 launch(都在 `tjark_agv_slam/launch/`):
- `gmapping.launch`
- `cartographer.launch`
- `amcl_gazebo.launch`

模型 wrapper:`tjark_agv_slam/urdf/tjark_agv_slam.xacro`

---

## v2: `tjark_agv_v2`

- **错误路线 / 排查尝试,后续不再使用**。
- 基于老师 V2 车模手工修补过多次(轮距、轮径、激光朝向、frame name 等),但发现方向和模型理解存在问题,放弃。
- 包内多个 `.bak_*` 备份记录了排查过程。
- **保留原因**:作为失败记录,避免后续重复踩坑;不作为正式主线。
- **不要把它当成"当前实战模型"或"未来主线"**。

入口 launch(只为 v2 排查存在,不再演进):
- `gmapping_v2.launch`
- `cartographer_v2.launch`
- `gazebo_v2.launch`
- `test_spawn_v2_*.launch`
- `test_v2_laser_check.launch`

模型 wrapper:`tjark_agv_slam/urdf/tjark_agv_slam_v2.xacro`

---

## v3: `tjark_agv_v3`

- **后续正式主线**。
- 从共享文件夹 `/mnt/hgfs/windows_ubuntu_share/tjark_agv-master.zip` 干净拷贝并改名得到(内部 `package.xml` / `CMakeLists.txt` / `xacro` 引用都已改成 `tjark_agv_v3`)。
- 内容与 master 在 urdf/mesh/sensor/controller/color 上是 byte-identical(除名称外)。
- **后续所有新实验、调参、launch、SLAM 入口都基于 v3**。

入口 launch:
- `gmapping_v3.launch` ✅ 已存在
- `cartographer_v3.launch` ✅ 已仿照 `cartographer.launch` 创建

模型 wrapper:`tjark_agv_slam/urdf/tjark_agv_slam_v3.xacro`

---

## test: `tjark_agv_test`

- **临时测试包,不是正式 SLAM 模型**。
- 用途:检查老师新包的 TF 坐标系、模型结构、导出差异。
- 与 v3 同源(都是 master.zip 改名拷贝),但作为沙盒,可放心做破坏性实验而不影响 v3 主线。
- **不要写成正式版本,后续可能删除**。

入口 launch:
- `display_tjark_agv_test.launch`(仅 RViz 静态显示)

---

## SLAM 工程入口:`tjark_agv_slam`

`tjark_agv_slam` 是统一 SLAM 工程入口,内含 launch / world / rviz / config / scripts。

| 模型版本 | gmapping | cartographer | 其他 |
|---|---|---|---|
| v1 (`tjark_agv`) | `gmapping.launch` | `cartographer.launch` | `amcl_gazebo.launch` |
| v2 (`tjark_agv_v2`) | `gmapping_v2.launch` | `cartographer_v2.launch` | (失败路线,不再演进) |
| v3 (`tjark_agv_v3`) | `gmapping_v3.launch` | `cartographer_v3.launch` | 后续新增都走 v3 |
| test (`tjark_agv_test`) | — | — | `display_tjark_agv_test.launch` |

**核心原则**:
1. **后续新建 launch / config / 实验,以 v3 为目标,model 名用 `tjark_agv_v3`,wrapper 用 `tjark_agv_slam_v3.xacro`**。
2. **不要再把 v2 当当前主线**。
3. v1(`tjark_agv`)保留为历史 baseline,不要删除。
4. test 包随时可丢弃,不依赖它。
