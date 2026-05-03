#!/usr/bin/env python3
"""
Odom debug logger.
Records odom pose vs Gazebo ground truth pose to CSV for analysis.
Usage:
    rosrun tjark_agv_slam debug_odom.py
    # Drive robot around, then Ctrl+C
    # CSV saved to ~/odom_debug.csv
"""

import rospy
import csv
import os
from nav_msgs.msg import Odometry
from gazebo_msgs.msg import ModelStates
from tf.transformations import euler_from_quaternion

CSV_PATH = os.path.expanduser("~/odom_debug.csv")

odom_pose = None
gt_pose = None


def odom_cb(msg):
    global odom_pose
    odom_pose = msg.pose.pose


def gazebo_cb(msg):
    global gt_pose
    try:
        idx = msg.name.index("tjark_agv")
        gt_pose = msg.pose[idx]
    except ValueError:
        pass


def main():
    rospy.init_node("debug_odom")
    rospy.Subscriber("/odom", Odometry, odom_cb)
    rospy.Subscriber("/gazebo/model_states", ModelStates, gazebo_cb)

    rate = rospy.Rate(2)  # 2 Hz

    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "time",
            "odom_x", "odom_y", "odom_yaw",
            "gt_x", "gt_y", "gt_yaw",
            "err_x", "err_y", "err_yaw"
        ])

        rospy.loginfo("Debug odom logger started. Saving to %s", CSV_PATH)
        rospy.loginfo("Drive the robot around, then Ctrl+C to stop.")

        while not rospy.is_shutdown():
            if odom_pose is not None and gt_pose is not None:
                t = rospy.get_time()

                ox = odom_pose.position.x
                oy = odom_pose.position.y
                _, _, oyaw = euler_from_quaternion([
                    odom_pose.orientation.x,
                    odom_pose.orientation.y,
                    odom_pose.orientation.z,
                    odom_pose.orientation.w
                ])

                gx = gt_pose.position.x
                gy = gt_pose.position.y
                _, _, gyaw = euler_from_quaternion([
                    gt_pose.orientation.x,
                    gt_pose.orientation.y,
                    gt_pose.orientation.z,
                    gt_pose.orientation.w
                ])

                writer.writerow([
                    f"{t:.3f}",
                    f"{ox:.4f}", f"{oy:.4f}", f"{oyaw:.4f}",
                    f"{gx:.4f}", f"{gy:.4f}", f"{gyaw:.4f}",
                    f"{ox-gx:.4f}", f"{oy-gy:.4f}", f"{oyaw-gyaw:.4f}"
                ])
                f.flush()

            rate.sleep()

    rospy.loginfo("Saved to %s", CSV_PATH)


if __name__ == "__main__":
    main()
