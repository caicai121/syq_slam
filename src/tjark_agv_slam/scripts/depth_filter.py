#!/usr/bin/env python3
"""
Depth image filter for ORB-SLAM2.
Removes NaN and inf values from Gazebo depth camera output.
Bypasses cv_bridge to avoid Python/OpenCV compatibility issues.
"""

import rospy
from sensor_msgs.msg import Image
import numpy as np

pub = None


def depth_callback(msg):
    # Gazebo depth camera outputs 32-bit float (32FC1)
    if msg.encoding not in ('32FC1', 'float32'):
        rospy.logwarn_throttle(5, "Unexpected depth encoding: %s", msg.encoding)
        return

    # Convert byte data to numpy float32 array
    cv_image = np.frombuffer(msg.data, dtype=np.float32).copy()
    cv_image = cv_image.reshape((msg.height, msg.width))

    # Replace NaN and inf with 0.0
    cv_image = np.nan_to_num(cv_image, nan=0.0, posinf=0.0, neginf=0.0)

    # Build filtered message
    filtered_msg = Image()
    filtered_msg.header = msg.header
    filtered_msg.height = msg.height
    filtered_msg.width = msg.width
    filtered_msg.encoding = msg.encoding
    filtered_msg.is_bigendian = msg.is_bigendian
    filtered_msg.step = msg.step
    filtered_msg.data = cv_image.tobytes()

    pub.publish(filtered_msg)


def main():
    global pub
    rospy.init_node('depth_filter')
    rospy.loginfo("Depth filter node started")

    pub = rospy.Publisher('/my_camera/depth/image_filtered', Image, queue_size=10)
    rospy.Subscriber('/my_camera/depth/image_raw', Image, depth_callback)

    rospy.spin()


if __name__ == '__main__':
    main()
