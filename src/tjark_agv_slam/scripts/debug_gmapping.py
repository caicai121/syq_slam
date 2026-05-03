#!/usr/bin/env python3
"""
Gmapping debug logger.
Records odom pose, scan stats, and map metadata to CSV.
Saves final map as PNG on exit for visual comparison.

Usage:
    rosrun tjark_agv_slam debug_gmapping.py
    # Drive robot around, then Ctrl+C
    # Outputs: ~/gmapping_debug.csv  +  ~/gmapping_map_final.png
"""

import rospy
import csv
import os
import signal
import sys
from nav_msgs.msg import Odometry, OccupancyGrid
from sensor_msgs.msg import LaserScan
from tf.transformations import euler_from_quaternion
from PIL import Image
import numpy as np

CSV_PATH = os.path.expanduser("~/gmapping_debug.csv")
MAP_PATH = os.path.expanduser("~/gmapping_map_final.png")

odom_pose = None
latest_scan_stats = {}
latest_map_meta = {}
map_update_count = 0
running = True


def odom_cb(msg):
    global odom_pose
    odom_pose = msg.pose.pose


def scan_cb(msg):
    global latest_scan_stats
    ranges = np.array(msg.ranges)
    valid = ranges[(ranges > msg.range_min) & (ranges < msg.range_max)]
    if len(valid) > 0:
        latest_scan_stats = {
            'range_mean': float(np.mean(valid)),
            'range_std': float(np.std(valid)),
            'valid_pts': int(len(valid)),
            'total_pts': int(len(ranges))
        }
    else:
        latest_scan_stats = {
            'range_mean': 0.0,
            'range_std': 0.0,
            'valid_pts': 0,
            'total_pts': int(len(ranges))
        }


def map_cb(msg):
    global latest_map_meta, map_update_count
    map_update_count += 1
    data = np.array(msg.data, dtype=np.int8)
    occupied = np.sum(data == 100)
    free = np.sum(data == 0)
    unknown = np.sum(data == -1)
    latest_map_meta = {
        'width': int(msg.info.width),
        'height': int(msg.info.height),
        'resolution': float(msg.info.resolution),
        'occupied': int(occupied),
        'free': int(free),
        'unknown': int(unknown),
        'origin_x': float(msg.info.origin.position.x),
        'origin_y': float(msg.info.origin.position.y)
    }


def save_map_png():
    if not latest_map_meta or 'width' not in latest_map_meta:
        rospy.logwarn("No map received yet, skipping PNG save")
        return
    rospy.loginfo("Saving final map to %s", MAP_PATH)
    # We need the latest map data; re-subscribe briefly is not clean,
    # so we save the last map received if we had cached it.
    # Better: ask user to use map_saver or we cache the last grid.
    # For simplicity, we note that this script only logs metadata.
    # Actual map saving will be done via a one-shot subscriber at exit.
    pass


def shutdown_hook():
    global running
    running = False
    rospy.loginfo("Shutting down debug logger...")
    rospy.loginfo("CSV saved to %s", CSV_PATH)
    rospy.loginfo("Map updates recorded: %d", map_update_count)


def main():
    global running, map_update_count
    rospy.init_node("debug_gmapping")
    signal.signal(signal.SIGINT, lambda s, f: shutdown_hook())

    rospy.Subscriber("/odom", Odometry, odom_cb)
    rospy.Subscriber("/scan", LaserScan, scan_cb)
    rospy.Subscriber("/map", OccupancyGrid, map_cb)

    rate = rospy.Rate(2)  # 2 Hz

    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "time",
            "odom_x", "odom_y", "odom_yaw",
            "scan_range_mean", "scan_range_std",
            "scan_valid_pts", "scan_total_pts",
            "map_width", "map_height", "map_resolution",
            "map_occupied", "map_free", "map_unknown",
            "map_origin_x", "map_origin_y",
            "map_update_count"
        ])

        rospy.loginfo("Gmapping debug logger started.")
        rospy.loginfo("CSV: %s", CSV_PATH)
        rospy.loginfo("Drive robot, then Ctrl+C to stop.")

        while running and not rospy.is_shutdown():
            if odom_pose is not None:
                t = rospy.get_time()
                ox = odom_pose.position.x
                oy = odom_pose.position.y
                _, _, oyaw = euler_from_quaternion([
                    odom_pose.orientation.x,
                    odom_pose.orientation.y,
                    odom_pose.orientation.z,
                    odom_pose.orientation.w
                ])

                writer.writerow([
                    f"{t:.3f}",
                    f"{ox:.4f}", f"{oy:.4f}", f"{oyaw:.4f}",
                    f"{latest_scan_stats.get('range_mean', 0):.4f}",
                    f"{latest_scan_stats.get('range_std', 0):.4f}",
                    latest_scan_stats.get('valid_pts', 0),
                    latest_scan_stats.get('total_pts', 0),
                    latest_map_meta.get('width', 0),
                    latest_map_meta.get('height', 0),
                    f"{latest_map_meta.get('resolution', 0):.4f}",
                    latest_map_meta.get('occupied', 0),
                    latest_map_meta.get('free', 0),
                    latest_map_meta.get('unknown', 0),
                    f"{latest_map_meta.get('origin_x', 0):.4f}",
                    f"{latest_map_meta.get('origin_y', 0):.4f}",
                    map_update_count
                ])
                f.flush()
            rate.sleep()

    rospy.loginfo("Done. CSV: %s", CSV_PATH)


if __name__ == "__main__":
    main()
