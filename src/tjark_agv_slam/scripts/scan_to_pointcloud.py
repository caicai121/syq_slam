#!/usr/bin/env python3
"""
Convert /scan (polar: angle + range) to PointCloud2 (Cartesian: x,y,z).
Publishes to /scan_pointcloud for visualization in RViz.

Usage:
    # Terminal 1: start gazebo + robot (gmapping.launch or any launch with laser)
    # Terminal 2:
    rosrun tjark_agv_slam scan_to_pointcloud.py
    # Terminal 3: RViz
    #   Fixed Frame = laser_link
    #   Add -> PointCloud2 -> Topic = /scan_pointcloud
"""

import rospy
import numpy as np
from sensor_msgs.msg import LaserScan, PointCloud2, PointField


def scan_cb(msg):
    angles = np.arange(msg.angle_min,
                       msg.angle_max + msg.angle_increment * 0.5,
                       msg.angle_increment)
    if len(angles) > len(msg.ranges):
        angles = angles[:len(msg.ranges)]

    ranges = np.array(msg.ranges)
    valid = (ranges > msg.range_min) & (ranges < msg.range_max) & np.isfinite(ranges)
    angles = angles[valid]
    ranges = ranges[valid]

    xs = ranges * np.cos(angles)
    ys = ranges * np.sin(angles)
    zs = np.zeros_like(xs)

    points = list(zip(xs, ys, zs))

    pc = PointCloud2()
    pc.header = msg.header          # frame_id = laser_link
    pc.height = 1
    pc.width = len(points)
    pc.fields = [
        PointField('x', 0, PointField.FLOAT32, 1),
        PointField('y', 4, PointField.FLOAT32, 1),
        PointField('z', 8, PointField.FLOAT32, 1),
    ]
    pc.is_bigendian = False
    pc.point_step = 12
    pc.row_step = pc.point_step * len(points)
    pc.is_dense = True
    pc.data = np.array(points, dtype=np.float32).tobytes()

    pub.publish(pc)

    # Print a few representative rays for intuition
    if len(ranges) > 0:
        fwd_idx = np.argmin(np.abs(angles))
        left_idx = np.argmin(np.abs(angles - np.pi / 2))
        back_idx = np.argmin(np.abs(angles - np.pi))
        right_idx = np.argmin(np.abs(angles + np.pi / 2))
        rospy.loginfo_throttle(2.0,
            "Scan→Cloud | total=%d pts | front=(%.2f,%.2f) | left=(%.2f,%.2f) | back=(%.2f,%.2f) | right=(%.2f,%.2f)",
            len(points),
            xs[fwd_idx], ys[fwd_idx],
            xs[left_idx], ys[left_idx],
            xs[back_idx], ys[back_idx],
            xs[right_idx], ys[right_idx],
        )


def main():
    global pub
    rospy.init_node("scan_to_pointcloud")
    pub = rospy.Publisher("/scan_pointcloud", PointCloud2, queue_size=1)
    rospy.Subscriber("/scan", LaserScan, scan_cb)
    rospy.loginfo("scan_to_pointcloud running. Publish /scan_pointcloud, frame_id=laser_link")
    rospy.spin()


if __name__ == "__main__":
    main()
