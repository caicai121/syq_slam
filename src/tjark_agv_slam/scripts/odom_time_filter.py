#!/usr/bin/env python3
"""
odom_time_filter.py - 过滤重复时间戳的 odom 消息。

Gazebo diff_drive 插件在机器人静止时可能发布重复时间戳的 odom，
Cartographer 对时间戳要求严格，重复时间戳会触发 map_by_time.h 断言失败。

本节点订阅 /odom，仅转发时间戳严格递增的消息到 /odom_filtered。
"""

import rospy
from nav_msgs.msg import Odometry


class OdomTimeFilter:
    def __init__(self):
        self.last_stamp = None
        self.pub = rospy.Publisher("/odom_filtered", Odometry, queue_size=50)
        self.sub = rospy.Subscriber("/odom", Odometry, self.callback, queue_size=100)
        rospy.loginfo("odom_time_filter started: /odom -> /odom_filtered")

    def callback(self, msg):
        stamp = msg.header.stamp
        if self.last_stamp is None or stamp > self.last_stamp:
            self.last_stamp = stamp
            self.pub.publish(msg)
        else:
            rospy.logwarn_throttle(
                5.0,
                "Dropped repeated or non-increasing odom timestamp: %.9f <= %.9f",
                stamp.to_sec(),
                self.last_stamp.to_sec(),
            )


if __name__ == "__main__":
    rospy.init_node("odom_time_filter")
    OdomTimeFilter()
    rospy.spin()
