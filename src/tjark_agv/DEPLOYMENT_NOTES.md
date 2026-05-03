# tjark_agv 机器人模型部署记录

> 记录时间：2026-04-26  
> ROS 版本：Noetic (Ubuntu 20.04)  
> 虚拟机：VMware Workstation

---

## 1. 前置环境

- **系统**：Ubuntu 20.04 LTS（VMware 虚拟机）
- **ROS**：Noetic
- **工作空间**：`~/catkin_ws`
- **文件传输**：VMware 共享文件夹 `/mnt/hgfs/windows_ubuntu_share/`
- **终端**：Terminator

---

## 2. 整体流程

```
Windows 共享文件夹
      ↓
拷贝 tjark_agv.zip 到 ~/catkin_ws/src/
      ↓
解压 → catkin_make 编译
      ↓
RViz 静态显示验证
      ↓
Gazebo 动态仿真验证
      ↓
键盘控制运动
```

---

## 3. 详细步骤

### 3.1 获取模型包

从 VMware 共享文件夹复制到工作空间：

```bash
cp /mnt/hgfs/windows_ubuntu_share/tjark_agv.zip ~/catkin_ws/src/
cd ~/catkin_ws/src/
unzip tjark_agv.zip
```

解压后包结构：

```
tjark_agv/
├── CMakeLists.txt
├── package.xml
├── config/
│   └── joint_names_tjark_agv.yaml
├── launch/
│   ├── display.launch      # RViz 显示
│   ├── gazebo.launch       # Gazebo 仿真
│   └── tjark_agv.launch
├── meshes/                 # STL 模型文件
├── textures/
├── urdf/
│   ├── tjark_agv.urdf          # SolidWorks 导出的裸 URDF
│   ├── tjark_agv.xacro         # 总入口 xacro
│   ├── tjark_agv.motor.xacro   # 电机传动配置
│   ├── tjark_agv.sensor.xacro  # 传感器插件（雷达、相机）
│   ├── tjark_agv.controller.xacro  # 差速驱动插件
│   └── tjark_agv.color.xacro   # 材质颜色
└── export.log
```

### 3.2 编译工作空间

```bash
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

### 3.3 RViz 静态显示

启动 display.launch：

```bash
source ~/catkin_ws/devel/setup.bash
roslaunch tjark_agv display.launch
```

RViz 中手动配置：
1. 左下角 **Add** → 选择 **RobotModel** → **OK**
2. 左上角 **Fixed Frame** 输入 `base_link`，按 **Enter** 确认
3. 模型即显示出来

> **注意**：SolidWorks 导出的 URDF 材质定义格式与 RViz 不兼容，模型显示为纯白色，属于正常现象，不影响结构和仿真。

### 3.4 Gazebo 仿真

#### 3.4.1 加载自定义世界

使用已有的 `gazebo_test/worlds/my_boxhouse.world` 环境：

```bash
source ~/catkin_ws/devel/setup.bash
roslaunch tjark_agv gazebo.launch
```

Gazebo 启动后等待约 5 秒，机器人模型自动生成在世界中。

#### 3.4.2 键盘控制

另开一个终端运行键盘控制节点：

```bash
rosrun teleop_twist_keyboard teleop_twist_keyboard.py
```

控制按键：

| 按键 | 动作 |
|------|------|
| `i` | 前进 |
| `k` | 停止 |
| `,` | 后退 |
| `j` | 左转 |
| `l` | 右转 |
| `q` / `z` | 加速 / 减速 |

> 控制终端必须保持焦点（鼠标点击终端窗口），不是在 Gazebo 窗口里按键。

---

## 4. 遇到的错误与解决方案

### 4.1 `joint_state_publisher_gui` 未找到

**现象**：
```
[rospack] Error: package 'joint_state_publisher_gui' not found
```

**根因**：`joint_state_publisher_gui` 包未安装。

**解决**：将 `display.launch` 中的 `joint_state_publisher_gui` 改为 `joint_state_publisher`（基础版，ROS 自带）：

```xml
<node name="joint_state_publisher" pkg="joint_state_publisher" type="joint_state_publisher" />
```

### 4.2 RViz 启动报错：找不到 `urdf.rviz` 配置文件

**现象**：
```
[ERROR]: RViz 无法打开文件 $(find tjark_agv)/urdf.rviz
```

**根因**：`display.launch` 中通过 `-d` 参数指定了一个不存在的 RViz 配置文件。

**解决**：去掉 `args` 参数，让 RViz 以默认空配置启动，手动添加 RobotModel：

```xml
<node name="rviz" pkg="rviz" type="rviz" />
```

### 4.3 RViz 中 Fixed Frame 输完 `base_link` 又跳回 `map`

**根因**：输入框未按 Enter 确认；或 `base_link` 坐标系在 TF 树中尚未发布。

**解决**：
1. 在 Fixed Frame 输入框输入 `base_link` 后，**必须按 Enter 键确认**
2. 确认 `joint_state_publisher` 和 `robot_state_publisher` 节点已正常运行

### 4.4 `teleop_twist_keyboard` 持续输出 `Waiting for subscriber to connect to /cmd_vel`

**现象**：键盘控制终端一直等待 `/cmd_vel` 订阅者。

**根因**：
1. `teleop_twist_keyboard` 放在 launch 文件中启动时，没有标准输入（stdin）权限，无法接收键盘按键
2. Gazebo 中的差速驱动插件未加载，导致没有节点订阅 `/cmd_vel`

**解决**：
1. 从 `gazebo.launch` 中移除 `teleop_twist_keyboard` 节点
2. 改为在独立终端中运行：
   ```bash
   rosrun teleop_twist_keyboard teleop_twist_keyboard.py
   ```

### 4.5 Gazebo spawn 超时：`Spawn service failed. Exiting.`

**现象**：
```
SpawnModel: Entity pushed to spawn queue, but spawn service timed out
```

**根因**：Gazebo 尚未完全初始化（physics 未就绪），`spawn_model` 就开始生成模型，导致超时。

**解决**：在 `gazebo.launch` 的 `spawn_model` 节点上添加 5 秒启动延迟：

```xml
<node name="spawn_model" pkg="gazebo_ros" type="spawn_model"
      args="-urdf -model tjark_agv -param robot_description -x 0 -y 0 -z 0.1"
      output="screen"
      launch-prefix="bash -c 'sleep 5; $0 $@' " />
```

### 4.6 模型名冲突：`Failure - entity already exists`

**现象**：
```
SpawnModel: Failure - entity already exists.
```

**根因**：上次运行的 Gazebo 残留进程未关闭，模型 `tjark_agv` 仍在内存中。

**解决**：强制清理所有 Gazebo 和 ROS 残留进程后重启：

```bash
killall -9 gzserver gzclient rosmaster
```

### 4.7 Gazebo 中机器人无响应，`/cmd_vel` 无人订阅

**现象**：
- `teleop_twist_keyboard` 正常启动，但持续输出 `Waiting for subscriber to connect to /cmd_vel`
- `rostopic list` 中没有 `/cmd_vel` 和 `/odom`

**根因**：`gazebo.launch` 通过 `textfile` 加载了裸 URDF（`tjark_agv.urdf`），而该文件**不包含任何 Gazebo 插件标签**。差速驱动插件、激光雷达插件、深度相机插件都定义在 `*.xacro` 文件中，必须通过 xacro 展开才能生效。

**解决**：将 launch 文件中的参数加载方式从 `textfile` 改为 `xacro` 命令展开：

```xml
<!-- 错误：加载裸 URDF，无 Gazebo 插件 -->
<param name="robot_description" textfile="$(find tjark_agv)/urdf/tjark_agv.urdf" />

<!-- 正确：加载 xacro，展开后包含所有 Gazebo 插件 -->
<param name="robot_description" command="$(find xacro)/xacro $(find tjark_agv)/urdf/tjark_agv.xacro" />
```

---

## 5. 机器人功能说明

### 5.1 机械结构

| 部件 | 说明 |
|------|------|
| `base_link` / `base_body` | 底盘与主体框架 |
| `left_wheel` / `right_wheel` | 左右主动轮（差速驱动） |
| `RF_link` / `RB_link` | 右前、右后万向从动轮 |
| `LF_link` / `LB_link` | 左前、左后万向从动轮 |

**驱动方式**：差速驱动（左轮与右轮速度差控制转向）。

### 5.2 传感器配置

#### RPLidar 激光雷达

- 安装位置：`laser_link`
- 扫描角度：360°（0 ~ 2π）
- 采样点数：720
- 测距范围：0.12 m ~ 12.0 m
- ROS 话题：`/scan`
- Gazebo 中显示为蓝色扫描光束

#### RGB-D 深度相机

- 安装位置：`camera_link`
- 分辨率：640 × 480
- 深度范围：0.05 m ~ 3.0 m
- ROS 话题：
  - `/my_camera/color/image_raw` — 彩色图像
  - `/my_camera/depth/image_raw` — 深度图像
  - `/my_camera/depth/points` — 点云数据

### 5.3 控制参数

- **轮距**（wheelSeparation）：0.4 m
- **轮径**（wheelDiameter）：0.12 m
- **控制接口**：`hardware_interface/VelocityJointInterface`
- **速度指令话题**：`/cmd_vel`
- **里程计话题**：`/odom`
- **里程计坐标系**：`odom`
- **机器人基坐标系**：`base_link`

---

## 6. 关键文件修改记录

### 6.1 `launch/display.launch`

```diff
- <node name="joint_state_publisher_gui" pkg="joint_state_publisher_gui" type="joint_state_publisher_gui" />
+ <node name="joint_state_publisher" pkg="joint_state_publisher" type="joint_state_publisher" />

- <node name="rviz" pkg="rviz" type="rviz" args="-d $(find tjark_agv)/urdf.rviz" />
+ <node name="rviz" pkg="rviz" type="rviz" />
```

### 6.2 `launch/gazebo.launch`

修改后完整内容：

```xml
<launch>
  <!-- 加载机器人描述（使用 xacro 展开，包含 Gazebo 插件） -->
  <param name="robot_description"
         command="$(find xacro)/xacro $(find tjark_agv)/urdf/tjark_agv.xacro" />

  <!-- 启动 gazebo，加载自定义世界 -->
  <include file="$(find gazebo_ros)/launch/empty_world.launch">
    <arg name="world_name" value="$(find gazebo_test)/worlds/my_boxhouse.world" />
  </include>

  <!-- 静态 TF：base_link → base_footprint -->
  <node name="tf_footprint_base" pkg="tf" type="static_transform_publisher"
        args="0 0 0 0 0 0 base_link base_footprint 40" />

  <!-- 在 gazebo 中生成机器人，延迟 5 秒等 Gazebo 就绪 -->
  <node name="spawn_model" pkg="gazebo_ros" type="spawn_model"
        args="-urdf -model tjark_agv -param robot_description -x 0 -y 0 -z 0.1"
        output="screen"
        launch-prefix="bash -c 'sleep 5; $0 $@' " />

  <!-- 机器人状态发布 -->
  <node name="robot_state_publisher" pkg="robot_state_publisher"
        type="robot_state_publisher" />
</launch>
```

---

## 7. 快速启动命令速查

```bash
# 编译
cd ~/catkin_ws && catkin_make

# RViz 静态显示
source ~/catkin_ws/devel/setup.bash
roslaunch tjark_agv display.launch

# Gazebo 仿真（含自定义世界）
source ~/catkin_ws/devel/setup.bash
roslaunch tjark_agv gazebo.launch

# 键盘控制（另开终端）
rosrun teleop_twist_keyboard teleop_twist_keyboard.py

# 清理残留进程
killall -9 gzserver gzclient rosmaster
```

---

## 8. 后续可扩展方向

- **SLAM 建图**：使用 `gmapping` 或 `cartographer`，订阅 `/scan` 话题
- **自主导航**：配置 `move_base` + `amcl`，实现定点巡航
- **视觉感知**：订阅 `/my_camera/depth/points` 进行点云处理
- **真机部署**：将 Gazebo 中的控制器参数迁移到真实机器人底盘
