# syq_SLAM

基于 tjark_agv 机器人模型在 Gazebo 仿真环境中实现激光 SLAM（Gmapping）与视觉 SLAM（ORB-SLAM2）的学习工程。

## 工程概述

本项目包含：
- **tjark_agv**：原始机器人模型包（URDF、meshes、传感器 Gazebo 插件）
- **tjark_agv_slam**：SLAM 扩展包（launch、worlds、rviz、scripts、配置文件）
- **mycar**：早期测试包，作为学习过程与辅助验证保留
- **gazebo_test**：早期测试包，作为学习过程与辅助验证保留

**tjark_agv_slam** 是当前主要 SLAM 工程成果，包含完整的建图与仿真流程；**tjark_agv** 是机器人模型与仿真基础；mycar 和 gazebo_test 是独立的学习实验包。

支持的 SLAM 方案：
- **Gmapping（激光 SLAM）**：2D 激光雷达建图
- **Cartographer（激光 SLAM）**：2D 激光雷达建图，支持 submap、闭环检测与全局优化
- **ORB-SLAM2（视觉 SLAM）**：RGB-D 稀疏特征点建图

## 项目亮点

- 基于 Gazebo 搭建 AGV 仿真环境；
- 完成机器人模型、激光雷达、RGB-D 相机等传感器配置；
- 实现 Gmapping 激光 SLAM 建图流程；
- 接入 ORB-SLAM2 RGB-D 视觉 SLAM 流程；
- 编写调试脚本，对 odom、scan、map、Gazebo 真值等数据进行辅助分析；
- 将早期测试包与主 SLAM 工程统一整理为可版本管理的 ROS 工作空间。

## 环境要求

本项目测试环境：
- **OS**：Ubuntu 20.04 LTS
- **ROS**：ROS Noetic
- **Gazebo**：Gazebo 11（随 ROS Noetic 安装）

> 上述环境为已验证的测试环境，其他兼容环境可能也可以运行，但未经验证。

可能需要以下依赖：
```bash
sudo apt-get update
sudo apt-get install -y \
  ros-noetic-gazebo-ros-pkgs \
  ros-noetic-gazebo-ros-control \
  ros-noetic-robot-state-publisher \
  ros-noetic-joint-state-publisher \
  ros-noetic-teleop-twist-keyboard \
  ros-noetic-slam-gmapping \
  ros-noetic-rviz \
  ros-noetic-cv-bridge \
  python3-pip
```

Python 依赖：
```bash
pip3 install numpy Pillow
```

## 目录结构

```
catkin_ws/
├── .gitignore
├── README.md
├── .catkin_workspace
└── src/
    ├── CMakeLists.txt          # catkin 顶层 CMakeLists
    ├── tjark_agv/              # 原始机器人模型包
    │   ├── launch/
    │   ├── meshes/             # STL 模型文件（含 base_body.STL ~5.1MB）
    │   ├── urdf/               # URDF / xacro
    │   ├── config/
    │   └── package.xml
    ├── tjark_agv_slam/         # SLAM 扩展包
    │   ├── launch/             # 启动文件
    │   │   ├── gmapping.launch
    │   │   ├── cartographer.launch
    │   │   └── orb_slam2.launch
    │   ├── config/             # 配置文件
    │   │   ├── tjark_agv_2d.lua
    │   │   └── orb_slam2_tjark.yaml
    │   ├── scripts/            # 调试与辅助脚本
    │   ├── rviz/               # RViz 预配置
    │   ├── urdf/               # wrapper xacro
    │   ├── worlds/             # Gazebo 世界文件
    │   └── package.xml
    ├── mycar/                  # 早期测试/实验包
    └── gazebo_test/            # 早期测试/实验包
├── build/                      # [未提交] catkin 编译产物
├── devel/                      # [未提交] catkin 编译产物
└── .git/                       # Git 仓库
```

## 未提交到仓库的文件

以下文件/目录因体积或第三方版权原因**未纳入 Git 版本控制**：

| 文件/目录 | 原因 |
|-----------|------|
| `src/ORB_SLAM2/` | 第三方库，需自行 clone |
| `ORB_SLAM2/Vocabulary/ORBvoc.txt`（~139MB） | ORB-SLAM2 词袋文件，需自行下载/解压 |
| `build/`, `devel/`, `build_isolated/`, `devel_isolated/`, `log/` | catkin 编译生成目录 |
| `.vscode/`, `.claude/`, `src/.vscode/` | IDE/工具配置 |
| `*.bag`, `*.pcd`, `*.ply`, `*.mp4`, `*.avi` | 运行时数据文件 |
| `*.zip`, `*.tar.gz` | 压缩包 |

## 第三方依赖：ORB-SLAM2

ORB-SLAM2 **不包含在本仓库中**，需要用户自行准备。

### 1. Clone ORB_SLAM2

以下使用官方仓库地址作为参考，如果你使用的是其他 fork 或修改版本，请替换为对应的仓库地址：

```bash
cd ~/catkin_ws/src
git clone https://github.com/raulmur/ORB_SLAM2.git ORB_SLAM2
cd ORB_SLAM2
chmod +x build.sh
./build.sh
```

### 2. 构建 ORB_SLAM2 的 ROS 节点

```bash
cd ~/catkin_ws/src/ORB_SLAM2/Examples/ROS/ORB_SLAM2
mkdir build
cd build
cmake .. -DROS_BUILD_TYPE=Release
make -j$(nproc)
```

### 3. 获取 ORBvoc.txt 词袋文件

```bash
cd ~/catkin_ws/src/ORB_SLAM2/Vocabulary
tar -xzvf ORBvoc.txt.tar.gz
# 解压后生成 ORBvoc.txt（约 139MB）
```

## 构建方式

在工作空间根目录执行：

```bash
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

建议将 `source` 命令加入 `~/.bashrc`：

```bash
echo "source ~/catkin_ws/devel/setup.bash" >> ~/.bashrc
```

## 运行方式

### Gmapping 激光 SLAM

一键启动完整仿真与建图链路：

```bash
roslaunch tjark_agv_slam gmapping.launch
```

启动后包含：
- Gazebo + boxhouse 世界环境
- 机器人模型
- Gmapping SLAM 节点
- 键盘遥控（`teleop_twist_keyboard`）
- RViz（预配置，显示 Map、LaserScan、RobotModel）

**建图操作**：用键盘驱动机器人在房间内行走，RViz 中实时显示地图。

**保存地图**：

```bash
rosrun map_server map_saver -f ~/my_map
# 生成 my_map.pgm 和 my_map.yaml
```

### Cartographer 2D 激光 SLAM

在原有 gmapping 仿真基础上，新增 Cartographer 2D 激光 SLAM 配置。Cartographer 源码和编译结果单独放在 `~/cartographer_ws` 中，不放入本仓库，避免影响原有 `catkin_ws` 工程。

启动前依次加载环境（**顺序不能反，catkin_ws 必须在 cartographer_ws 之前**）：

```bash
source ~/catkin_ws/devel/setup.bash
source ~/cartographer_ws/install_isolated/setup.bash
```

启动 Cartographer：

```bash
roslaunch tjark_agv_slam cartographer.launch
```

启动后包含：
- Gazebo + boxhouse 世界环境（与 gmapping 相同）
- 机器人模型（spawn 在 (-2, 0, 0.4)）
- odom 时间戳过滤节点（/odom -> /odom_filtered）
- Cartographer 2D SLAM 节点（使用 /scan 和 /odom_filtered）
- 占据栅格地图发布节点
- 键盘遥控
- RViz（显示 Map、Submaps、LaserScan、RobotModel、TF）

保存地图：

```bash
rosrun map_server map_saver -f ~/cartographer_map
```

注意：gmapping 和 Cartographer 不要同时启动，两者都会发布 `/map` 和 `map -> odom` TF，同时运行会冲突。后续可在相同 Gazebo 环境和相同运动路线下对比两种 SLAM 方法的建图效果。

### ORB-SLAM2 视觉 SLAM

一键启动完整视觉 SLAM 链路：

```bash
roslaunch tjark_agv_slam orb_slam2.launch
```

启动后包含：
- Gazebo + 机器人
- 深度图预处理节点（过滤 NaN/inf）
- ORB-SLAM2 RGB-D 节点
- 键盘遥控

### 调试脚本

| 脚本 | 功能 |
|------|------|
| `debug_odom.py` | 记录 odom vs Gazebo 真值到 CSV |
| `debug_gmapping.py` | 记录 odom、scan、map 元数据到 CSV |
| `debug_laser_tf.py` | 将 /scan 投影到 odom 帧并发布 PointCloud2 |
| `scan_to_pointcloud.py` | 将 /scan 转换为 PointCloud2 可视化 |

```bash
rosrun tjark_agv_slam debug_odom.py
rosrun tjark_agv_slam debug_gmapping.py
rosrun tjark_agv_slam scan_to_pointcloud.py
```

### 自动路线测试

用于 gmapping 和 Cartographer 同路线建图对比。脚本控制机器人走较大范围巡检路线：从起点出发 → 左转进入左上区域 → 绕过左侧障碍物 → 沿上方墙体向右 → 到达右上角 → 返回中间区域。

```bash
# 先启动 SLAM（gmapping 或 Cartographer），然后在另一个终端运行：
rosrun tjark_agv_slam auto_drive_square.py
```

参数：线速度 0.60 m/s，角速度 1.20 rad/s。可在脚本中调整各段动作的持续时间。首次测试建议在 Gazebo 中观察是否碰撞，根据实际情况微调。

## 核心参数说明

### 激光雷达（sensor.xacro）
- frame_id: `laser_link`
- 扫描范围: 0 ~ 2π，720 采样点
- 测距: 0.12m ~ 12.0m

### Gmapping 关键参数
- `linearUpdate`: 0.2（20cm 触发一次扫描匹配）
- `angularUpdate`: 0.1（~5.7° 触发一次扫描匹配）
- `particles`: 120
- `map_update_interval`: 1.0s
- `delta`: 0.05（地图分辨率 5cm）

> 以上参数以当前 `gmapping.launch` 文件中的实际配置为准，可根据环境和效果需求调整。

### ORB-SLAM2 配置
- 配置文件: `tjark_agv_slam/config/orb_slam2_tjark.yaml`
- 相机内参以当前配置文件中的实际值为准

### 底盘参数
- 轮距、轮径、左右轮关节等底盘参数以当前 `tjark_agv/urdf/` 中的 Xacro 文件为准

## 模型修改记录

以下对原始 `tjark_agv` 包的修改是为了使模型正确运行 SLAM：

| 文件 | 修改内容 |
|------|----------|
| `tjark_agv/urdf/tjark_agv.urdf` | `laser_to_body` rpy 修正，使 laser_link Z 轴朝上 |
| `tjark_agv/urdf/tjark_agv.sensor.xacro` | 激光雷达 `frameName` 改为 `laser_link`；相机 FOV/range 扩展 |
| `tjark_agv/urdf/tjark_agv.controller.xacro` | 底盘参数调整（轮径、轮距等），以匹配 URDF 实际尺寸；添加 `<odometrySource>encoder</odometrySource>` 使 odom 原点从机器人启动位置开始计数 |

### 里程计配置说明

diff_drive 插件中的 `odometrySource` 参数控制 odom 坐标系的原点：
- `world`（默认）：odom 原点在 Gazebo 世界原点 (0,0)
- `encoder`：odom 原点在机器人启动位置

当前使用 `encoder` 模式，确保机器人启动时 odom -> base_link 接近 (0,0,0)。

### odom 时间戳过滤

`odom_time_filter.py` 节点用于过滤 Gazebo diff_drive 插件发布的重复时间戳 odom 消息。Cartographer 对时间戳要求严格，重复时间戳会触发断言失败。该节点订阅 `/odom`，仅转发时间戳严格递增的消息到 `/odom_filtered`。
