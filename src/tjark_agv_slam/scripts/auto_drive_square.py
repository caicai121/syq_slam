#!/usr/bin/env python3
"""
auto_drive_square.py - 大范围自动巡检路线，用于 gmapping 和 Cartographer 同路线建图对比。

路线：从起点出发 → 左转进入左上区域 → 绕过左侧障碍物 → 沿上方墙体向右 → 到达右上角 → 返回中间区域

用法：
  rosrun tjark_agv_slam auto_drive_square.py
"""

import rospy
from geometry_msgs.msg import Twist

# 速度参数 (×2)
LINEAR_SPEED = 0.60   # m/s
ANGULAR_SPEED = 1.20  # rad/s

# 角度时间常量 (angular.z = 1.20 rad/s, 时间 ÷2)
TURN_45 = 0.65   # 45° = 0.785 rad, 0.785 / 1.20 ≈ 0.65 s
TURN_90 = 1.3    # 90° = 1.571 rad, 1.571 / 1.20 ≈ 1.3 s


def move(pub, linear_x, angular_z, duration):
    """发布速度指令并持续指定时间"""
    twist = Twist()
    twist.linear.x = linear_x
    twist.angular.z = angular_z
    rate = rospy.Rate(10)
    t0 = rospy.Time.now()
    while (rospy.Time.now() - t0).to_sec() < duration:
        pub.publish(twist)
        rate.sleep()


def stop(pub, duration=0.5):
    """持续发布零速度"""
    twist = Twist()
    rate = rospy.Rate(10)
    t0 = rospy.Time.now()
    while (rospy.Time.now() - t0).to_sec() < duration:
        pub.publish(twist)
        rate.sleep()


def drive_patrol():
    rospy.init_node('auto_drive_square', anonymous=True)
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    rospy.sleep(1.0)  # 等待 publisher 连接

    rospy.loginfo("Auto drive patrol: starting in 2.0 seconds...")
    rospy.sleep(2.0)

    try:
        rospy.loginfo("Step 1: turn left 45 deg, heading 0 -> -45")
        move(pub, 0, ANGULAR_SPEED, TURN_45)
        stop(pub)

        rospy.loginfo("Step 2: move forward to left-upper area, 7.8 s")
        move(pub, LINEAR_SPEED, 0, 7.8)
        stop(pub)

        rospy.loginfo("Step 3: turn right 45 deg, heading -45 -> 0")
        move(pub, 0, -ANGULAR_SPEED, TURN_45)
        stop(pub)

        rospy.loginfo("Step 4: move forward around left obstacle, 4.0 s")
        move(pub, LINEAR_SPEED, 0, 4.0)
        stop(pub)

        rospy.loginfo("Step 5: turn right 90 deg, heading 0 -> +90")
        move(pub, 0, -ANGULAR_SPEED, TURN_90)
        stop(pub)

        rospy.loginfo("Step 6: move along upper area, 12.0 s")
        move(pub, LINEAR_SPEED, 0, 12.0)
        stop(pub)

        rospy.loginfo("Step 7: turn right 90 deg")
        move(pub, 0, -ANGULAR_SPEED, TURN_90)
        stop(pub)

        rospy.loginfo("Step 8: move to right-upper area, 12.5 s")
        move(pub, LINEAR_SPEED, 0, 12.5)
        stop(pub)

        rospy.loginfo("Step 9: turn right 90 deg for returning")
        move(pub, 0, -ANGULAR_SPEED, TURN_90)
        stop(pub)

        rospy.loginfo("Step 10: move back to middle area, 4.0 s")
        move(pub, LINEAR_SPEED, 0, 4.0)
        stop(pub)

        rospy.loginfo("Step 11: turn right 90 deg")
        move(pub, 0, -ANGULAR_SPEED, TURN_90)
        stop(pub)

        rospy.loginfo("Step 12: move to center area, 2.0 s")
        move(pub, LINEAR_SPEED, 0, 2.0)
        stop(pub)

    except rospy.ROSInterruptException:
        pass
    finally:
        rospy.loginfo("Auto drive patrol: finished. Stopping robot.")
        stop(pub, 2.0)


if __name__ == '__main__':
    drive_patrol()
