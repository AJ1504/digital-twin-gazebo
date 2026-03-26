"""
Week 3-4: Joint Controller for MJCF Humanoid
Controls robot joints via ROS 2 topics.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
import math
import time


class JointController(Node):
    """Control MJCF humanoid joints via ROS 2."""

    def __init__(self):
        super().__init__('joint_controller')

        # MJCF humanoid joint names (DeepMind MuJoCo model)
        self.arm_joints = [
            'left_shoulder4', 'left_shoulder3', 'left_shoulder2',
            'left_elbow',
            'right_shoulder4', 'right_shoulder3', 'right_shoulder2',
            'right_elbow',
        ]

        self.leg_joints = [
            'left_hip_x', 'left_hip_y', 'left_hip_z',
            'left_knee',
            'left_ankle_x', 'left_ankle_y',
            'right_hip_x', 'right_hip_y', 'right_hip_z',
            'right_knee',
            'right_ankle_x', 'right_ankle_y',
        ]

        self.torso_joints = ['abdomen_x', 'abdomen_y', 'abdomen_z']

        # Publishers for each joint
        self.joint_pubs = {}
        all_joints = self.arm_joints + self.leg_joints + self.torso_joints
        for joint in all_joints:
            topic = f'/model/humanoid_robot/joint/{joint}/cmd_pos'
            self.joint_pubs[joint] = self.create_publisher(Float64, topic, 10)

        self.get_logger().info(f'Joint Controller ready ({len(all_joints)} joints)')

    def move_joint(self, joint_name: str, angle_rad: float):
        """Command a joint to a target angle (radians)."""
        if joint_name in self.joint_pubs:
            msg = Float64()
            msg.data = angle_rad
            self.joint_pubs[joint_name].publish(msg)
            self.get_logger().info(f'{joint_name} -> {math.degrees(angle_rad):.1f}°')
        else:
            self.get_logger().warn(f'Unknown joint: {joint_name}')

    def arms_up(self):
        """Raise both arms."""
        self.move_joint('left_shoulder4', -1.5)
        self.move_joint('right_shoulder4', -1.5)

    def arms_down(self):
        """Lower both arms."""
        self.move_joint('left_shoulder4', 0.0)
        self.move_joint('right_shoulder4', 0.0)

    def wave(self):
        """Wave right arm."""
        self.move_joint('right_shoulder4', -1.5)
        time.sleep(0.5)
        for _ in range(3):
            self.move_joint('right_elbow', -0.8)
            time.sleep(0.4)
            self.move_joint('right_elbow', 0.0)
            time.sleep(0.4)
        self.move_joint('right_shoulder4', 0.0)


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
