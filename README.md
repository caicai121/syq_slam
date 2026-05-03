# tjark_agv SLAM

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
- **ORB-SLAM2（视觉 SLAM）**：RGB-D 稀疏特征点建图

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
    │   │   └── orb_slam2.launch
    │   ├── config/             # 配置文件
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
| `tjark_agv/urdf/tjark_agv.controller.xacro` | 底盘参数调整（轮径、轮距等），以匹配 URDF 实际尺寸 |
