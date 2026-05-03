cmake_minimum_required(VERSION 3.0.2)
project(tjark_agv_slam)

find_package(catkin REQUIRED COMPONENTS
  roscpp
  rospy
  std_msgs
  sensor_msgs
  nav_msgs
  geometry_msgs
  tf
)

catkin_package(
  CATKIN_DEPENDS roscpp rospy std_msgs sensor_msgs nav_msgs geometry_msgs tf
)

include_directories(
  ${catkin_INCLUDE_DIRS}
)

# Install launch files
install(DIRECTORY launch/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/launch
)

# Install config files
install(DIRECTORY config/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/config
)

# Install rviz files
install(DIRECTORY rviz/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/rviz
)
