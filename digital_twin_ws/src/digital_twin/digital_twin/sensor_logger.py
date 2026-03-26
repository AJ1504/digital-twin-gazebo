"""
Week 4: Sensor Data Logger
Subscribes to all robot sensors and logs data at 50Hz.
Logs: joint positions, torques, camera images, contact sensors, IMU.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState, Image, Imu
from geometry_msgs.msg import WrenchStamped
from std_msgs.msg import Float64
import json
import csv
import os
from datetime import datetime
from cv_bridge import CvBridge
import cv2
import numpy as np


class SensorLogger(Node):
    """Log all sensor data from the humanoid robot."""

    def __init__(self):
        super().__init__('sensor_logger')

        # Create output directory
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_dir = f'data/sensor_logs/{self.timestamp}'
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(f'{self.log_dir}/images', exist_ok=True)

        self.bridge = CvBridge()
        self.frame_count = 0
        self.log_hz = 50  # 50Hz logging rate
        self.last_log_time = 0

        # CSV files for data logging
        self.joint_csv = open(f'{self.log_dir}/joint_states.csv', 'w', newline='')
        self.joint_writer = csv.writer(self.joint_csv)
        self.joint_writer.writerow([
            'timestamp', 'joint_name', 'position', 'velocity', 'effort'
        ])

        self.imu_csv = open(f'{self.log_dir}/imu_data.csv', 'w', newline='')
        self.imu_writer = csv.writer(self.imu_csv)
        self.imu_writer.writerow([
            'timestamp', 'ang_x', 'ang_y', 'ang_z',
            'lin_x', 'lin_y', 'lin_z'
        ])

        self.contact_csv = open(f'{self.log_dir}/contacts.csv', 'w', newline='')
        self.contact_writer = csv.writer(self.contact_csv)
        self.contact_writer.writerow([
            'timestamp', 'sensor', 'force_x', 'force_y', 'force_z'
        ])

        # Subscribers
        self.create_subscription(
            JointState, '/joint_states',
            self.joint_states_cb, 10
        )
        self.create_subscription(
            Imu, '/model/humanoid_robot/link/torso/sensor/imu_sensor/imu',
            self.imu_cb, 10
        )
        self.create_subscription(
            Image, '/camera/image',
            self.camera_cb, 10
        )

        # Contact sensors (left/right foot)
        for side in ['left_foot', 'right_foot']:
            topic = f'/model/humanoid_robot/link/{side}/sensor/contact/contact'
            self.create_subscription(
                WrenchStamped, topic,
                lambda msg, s=side: self.contact_cb(msg, s), 10
            )

        # Stats
        self.stats = {
            'joint_states': 0,
            'imu': 0,
            'images': 0,
            'contacts': 0
        }

        self.get_logger().info(f'Sensor Logger ready. Logging to {self.log_dir}')

    def should_log(self):
        """Check if enough time has passed for next log entry."""
        now = self.get_clock().now().nanoseconds / 1e9
        if now - self.last_log_time >= 1.0 / self.log_hz:
            self.last_log_time = now
            return True
        return False

    def joint_states_cb(self, msg):
        if not self.should_log():
            return
        ts = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        for i, name in enumerate(msg.name):
            pos = msg.position[i] if i < len(msg.position) else 0
            vel = msg.velocity[i] if i < len(msg.velocity) else 0
            eff = msg.effort[i] if i < len(msg.effort) else 0
            self.joint_writer.writerow([ts, name, pos, vel, eff])
        self.stats['joint_states'] += 1

    def imu_cb(self, msg):
        if not self.should_log():
            return
        ts = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        self.imu_writer.writerow([
            ts,
            msg.angular_velocity.x, msg.angular_velocity.y, msg.angular_velocity.z,
            msg.linear_acceleration.x, msg.linear_acceleration.y, msg.linear_acceleration.z
        ])
        self.stats['imu'] += 1

    def camera_cb(self, msg):
        """Save camera frames at reduced rate (10Hz for storage)."""
        if self.frame_count % 5 != 0:  # Every 5th frame = ~10Hz at 50Hz
            self.frame_count += 1
            return
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
            filename = f'{self.log_dir}/images/frame_{self.frame_count:06d}.png'
            cv2.imwrite(filename, cv_image)
            self.stats['images'] += 1
        except Exception as e:
            self.get_logger().error(f'Camera error: {e}')
        self.frame_count += 1

    def contact_cb(self, msg, sensor_name):
        if not self.should_log():
            return
        ts = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        f = msg.wrench.force
        self.contact_writer.writerow([ts, sensor_name, f.x, f.y, f.z])
        self.stats['contacts'] += 1

    def destroy_node(self):
        """Close CSV files on shutdown."""
        self.joint_csv.close()
        self.imu_csv.close()
        self.contact_csv.close()
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
