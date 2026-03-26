"""
Digital Twin Launch File (Updated for MJCF Humanoid)
Launches Gazebo world with humanoid robot, sensors, and ROS 2 bridge.
"""

from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    pkg_dir = get_package_share_directory('digital_twin')

    # World file
    world_file = os.path.join(pkg_dir, 'worlds', 'home_environment.sdf')

    # Gazebo server (gz sim)
    gz_sim = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world_file],
        output='screen',
    )

    # ROS 2 - Gazebo bridge (Week 4: sensors)
    # MJCF humanoid has cameras on head (egocentric) and torso (back, side)
    gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # Clock
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            # Head camera (egocentric - primary for object detection)
            '/world/home_environment/model/humanoid_robot/link/head/sensor/egocentric/camera/image@sensor_msgs/msg/Image[gz.msgs.Image',
            # Back camera
            '/world/home_environment/model/humanoid_robot/link/torso/sensor/back/camera/image@sensor_msgs/msg/Image[gz.msgs.Image',
            # Joint states
            '/world/home_environment/pose/info@gz.msgs.Pose_V',
        ],
        remappings=[
            # Remap to cleaner topic names
            ('/world/home_environment/model/humanoid_robot/link/head/sensor/egocentric/camera/image', '/camera/head/image'),
            ('/world/home_environment/model/humanoid_robot/link/torso/sensor/back/camera/image', '/camera/back/image'),
        ],
        output='screen',
    )

    # Week 4: Sensor logger
    sensor_logger = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='digital_twin',
                executable='sensor_logger',
                output='screen',
            )
        ],
    )

    # Week 5: Object detector (uncomment after training YOLOv8)
    # object_detector = TimerAction(
    #     period=6.0,
    #     actions=[
    #         Node(
    #             package='digital_twin',
    #             executable='detect_objects',
    #             output='screen',
    #         )
    #     ],
    # )

    return LaunchDescription([
        gz_sim,
        gz_bridge,
        sensor_logger,
    ])
