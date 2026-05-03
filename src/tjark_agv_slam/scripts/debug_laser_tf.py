#!/usr/bin/env python3
"""
Laser TF direction verifier.
Projects /scan points into odom frame and publishes as PointCloud2.
Also prints front/left/right distances for quick orientation check.

Usage:
    rosrun tjark_agv_slam debug_laser_tf.py
    # In RViz, add PointCloud2, topic=/debug/laser_in_odom, Fixed Frame=odom
    # Drive robot to face a wall, check if red points align with Gazebo wall
"""

import rospy
import tf
import numpy as np
from sensor_msgs.msg import LaserScan, PointCloud2, PointField
from sensor_msgs import point_cloud2


def scan_to_points(scan):
    """Convert LaserScan to list of (x,y,z) in scan frame."""
    angles = np.arange(scan.angle_min, scan.angle_max + scan.angle_increment * 0.5, scan.angle_increment)
    if len(angles) > len(scan.ranges):
        angles = angles[:len(scan.ranges)]
    ranges = np.array(scan.ranges)
    valid = (ranges > scan.range_min) & (ranges < scan.range_max) & np.isfinite(ranges)
    angles = angles[valid]
    ranges = ranges[valid]
    xs = ranges * np.cos(angles)
    ys = ranges * np.sin(angles)
    zs = np.zeros_like(xs)
    return list(zip(xs, ys, zs)), angles, ranges


def make_pc2(points, frame_id, stamp):
    """Build a PointCloud2 message from list of (x,y,z)."""
    msg = PointCloud2()
    msg.header.stamp = stamp
    msg.header.frame_id = frame_id
    msg.height = 1
    msg.width = len(points)
    msg.fields = [
        PointField('x', 0, PointField.FLOAT32, 1),
        PointField('y', 4, PointField.FLOAT32, 1),
        PointField('z', 8, PointField.FLOAT32, 1),
    ]
    msg.is_bigendian = False
    msg.point_step = 12
    msg.row_step = msg.point_step * len(points)
    msg.is_dense = True
    msg.data = np.array(points, dtype=np.float32).tobytes()
    return msg


def main():
    rospy.init_node("debug_laser_tf")
    listener = tf.TransformListener()
    pc_pub = rospy.Publisher("/debug/laser_in_odom", PointCloud2, queue_size=1)
    scan_msg = None

    def scan_cb(msg):
        nonlocal scan_msg
        scan_msg = msg

    rospy.Subscriber("/scan", LaserScan, scan_cb)
    rospy.loginfo("Waiting for /scan and TF (odom -> laser_link)...")

    rate = rospy.Rate(2)
    while not rospy.is_shutdown():
        if scan_msg is None:
            rate.sleep()
            continue

        try:
            listener.waitForTransform("odom", scan_msg.header.frame_id, scan_msg.header.stamp, rospy.Duration(0.1))
            (trans, rot) = listener.lookupTransform("odom", scan_msg.header.frame_id, scan_msg.header.stamp)
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            rate.sleep()
            continue

        points_scan, angles, ranges = scan_to_points(scan_msg)
        if len(points_scan) == 0:
            rate.sleep()
            continue

        # Build 4x4 transform matrix
        from tf.transformations import quaternion_matrix
        M = quaternion_matrix(rot)
        M[0:3, 3] = trans

        # Transform points to odom frame
        pts = np.array(points_scan, dtype=np.float32)
        ones = np.ones((pts.shape[0], 1), dtype=np.float32)
        pts_h = np.hstack([pts, ones])  # Nx4
        pts_odom = (M @ pts_h.T).T[:, :3]
        points_odom = [(float(p[0]), float(p[1]), float(p[2])) for p in pts_odom]

        pc_pub.publish(make_pc2(points_odom, "odom", scan_msg.header.stamp))

        # Print orientation hints: front (~0 rad), left (~+pi/2), right (~-pi/2)
        front_idx = np.argmin(np.abs(angles))
        left_idx = np.argmin(np.abs(angles - np.pi / 2))
        right_idx = np.argmin(np.abs(angles + np.pi / 2))
        rospy.loginfo(
            "Laser in odom | front=%.2fm (%.1f deg) | left=%.2fm (%.1f deg) | right=%.2fm (%.1f deg)",
            ranges[front_idx], np.degrees(angles[front_idx]),
            ranges[left_idx], np.degrees(angles[left_idx]),
            ranges[right_idx], np.degrees(angles[right_idx]),
        )

        rate.sleep()


if __name__ == "__main__":
    main()
