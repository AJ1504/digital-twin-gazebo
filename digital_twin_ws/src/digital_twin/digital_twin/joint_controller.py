"""
Week 4: Robot Joint Control Script
Controls humanoid robot joints via ROS 2 topics.
Provides simple position commands for arm movements.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from sensor_msgs.msg import JointState
import math
import time


class JointController(Node):
    """Control robot joints via ROS 2."""

    def __init__(self):
        super().__init__('joint_controller')

        # Joint publishers (for Gazebo joint controller plugin)
        self.joint_pubs = {}
        joints = [
            'left_shoulder_pitch', 'left_elbow_pitch', 'left_wrist',
            'right_shoulder_pitch', 'right_elbow_pitch', 'right_wrist',
            'neck',
        ]
        for joint in joints:
            topic = f'/model/humanoid_robot/joint/{joint}/cmd_pos'
            self.joint_pubs[joint] = self.create_publisher(Float64, topic, 10)

        # Subscribe to joint states
        self.joint_states_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_states_callback,
            10
        )
        self.current_joint_states = {}

        self.get_logger().info('Joint Controller ready')

    def joint_states_callback(self, msg):
        """Store current joint states."""
        for i, name in enumerate(msg.name):
            if i < len(msg.position):
                self.current_joint_states[name] = msg.position[i]

    def move_joint(self, joint_name: str, angle_rad: float):
        """Command a joint to a target angle (radians)."""
        if joint_name in self.joint_pubs:
            msg = Float64()
            msg.data = angle_rad
            self.joint_pubs[joint_name].publish(msg)
            self.get_logger().info(f'{joint_name} -> {math.degrees(angle_rad):.1f}°')
        else:
            self.get_logger().warn(f'Unknown joint: {joint_name}')

    def wave(self):
        """Demo: wave the right arm."""
        self.move_joint('right_shoulder_pitch', -1.5)
        time.sleep(0.5)
        for _ in range(3):
            self.move_joint('right_elbow_pitch', -0.8)
            time.sleep(0.4)
            self.move_joint('right_elbow_pitch', 0.0)
            time.sleep(0.4)
        self.move_joint('right_shoulder_pitch', 0.0)

    def arms_up(self):
        """Demo: raise both arms."""
        self.move_joint('left_shoulder_pitch', -2.5)
        self.move_joint('right_shoulder_pitch', -2.5)

    def arms_down(self):
        """Demo: lower both arms."""
        self.move_joint('left_shoulder_pitch', 0.0)
        self.move_joint('right_shoulder_pitch', 0.0)


def main(args=None):
    rclpy.init(args=args)
    controller = JointController()

    # Demo sequence
    print("Running demo: wave")
    controller.wave()
    time.sleep(1)

    print("Running demo: arms up")
    controller.arms_up()
    time.sleep(2)

    print("Running demo: arms down")
    controller.arms_down()

    controller.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
