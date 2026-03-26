"""
Week 4: Sensor Data Logger (Updated for MJCF Humanoid)
Subscribes to robot sensors and logs data at 50Hz.
Logs: camera images, joint positions (from Gazebo pose), contacts.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import PoseStamped
import json
import csv
import os
from datetime import datetime
from cv_bridge import CvBridge
import cv2


class SensorLogger(Node):
    """Log all sensor data from the humanoid robot."""

    def __init__(self):
        super().__init__('sensor_logger')

        # Create output directory
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_dir = f'data/sensor_logs/{self.timestamp}'
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(f'{self.log_dir}/images/head', exist_ok=True)
        os.makedirs(f'{self.log_dir}/images/back', exist_ok=True)

        self.bridge = CvBridge()
        self.frame_count = 0
        self.log_hz = 50
        self.last_log_time = 0

        # CSV for pose data
        self.pose_csv = open(f'{self.log_dir}/robot_pose.csv', 'w', newline='')
        self.pose_writer = csv.writer(self.pose_csv)
        self.pose_writer.writerow([
            'timestamp', 'pos_x', 'pos_y', 'pos_z',
            'ori_x', 'ori_y', 'ori_z', 'ori_w'
        ])

        # Subscribers - head camera (primary for object detection)
        self.create_subscription(
            Image, '/camera/head/image',
            self.head_camera_cb, 10
        )

        # Back camera
        self.create_subscription(
            Image, '/camera/back/image',
            self.back_camera_cb, 10
        )

        # Stats
        self.stats = {
            'head_images': 0,
            'back_images': 0,
            'pose_samples': 0,
        }

        self.get_logger().info(f'Sensor Logger ready. Logging to {self.log_dir}')

    def should_log(self):
        """Check if enough time has passed for next log entry."""
        now = self.get_clock().now().nanoseconds / 1e9
        if now - self.last_log_time >= 1.0 / self.log_hz:
            self.last_log_time = now
            return True
        return False

    def head_camera_cb(self, msg):
        """Save head camera frames at 10Hz."""
        if not self.should_log():
            return
        if self.frame_count % 5 != 0:
            self.frame_count += 1
            return
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
            filename = f'{self.log_dir}/images/head/frame_{self.frame_count:06d}.png'
            cv2.imwrite(filename, cv_image)
            self.stats['head_images'] += 1
        except Exception as e:
            self.get_logger().error(f'Head camera error: {e}')
        self.frame_count += 1

    def back_camera_cb(self, msg):
        """Save back camera frames at 5Hz."""
        if self.frame_count % 10 != 0:
            return
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
            filename = f'{self.log_dir}/images/back/frame_{self.frame_count:06d}.png'
            cv2.imwrite(filename, cv_image)
            self.stats['back_images'] += 1
        except Exception as e:
            self.get_logger().error(f'Back camera error: {e}')

    def destroy_node(self):
        """Close CSV files on shutdown."""
        self.pose_csv.close()
        self.get_logger().info(f'Logger stats: {json.dumps(self.stats)}')
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = SensorLogger()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
