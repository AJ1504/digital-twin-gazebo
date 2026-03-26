"""
Digital Twin Bringup Launch File
Launches Gazebo world with humanoid robot, sensors, and basic nodes.
"""

from launch import LaunchDescription
from launch.actions import (
    ExecuteProcess,
    RegisterEventHandler,
    TimerAction,
    IncludeLaunchDescription,
)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    pkg_dir = get_package_share_directory('digital_twin')

    # World file
    world_file = os.path.join(pkg_dir, 'worlds', 'home_environment.sdf')

    # Robot model
    robot_model = os.path.join(pkg_dir, 'models', 'humanoid_robot', 'model.sdf')

    # Gazebo server (gz sim)
    gz_sim = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world_file],
        output='screen',
    )

    # Spawn robot in the world (after Gazebo starts)
    spawn_robot = TimerAction(
        period=3.0,
        actions=[
            ExecuteProcess(
                cmd=[
                    'gz', 'service', '-s', '/world/home_environment/create',
                    '--reqtype', 'gz.msgs.EntityFactory',
                    '--reptype', 'gz.msgs.Boolean',
                    '--timeout', '1000',
                    '--req', f'sdf_filename: "{robot_model}" pose {{ position {{ x: 0 y: 0 z: 0.1 }} }} name: "humanoid_robot"',
                ],
                output='screen',
            )
        ],
    )

    # ROS 2 - Gazebo bridge (joint states, sensors, etc.)
    gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # Joint states
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            # Clock
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            # Camera
            '/camera/image@sensor_msgs/msg/Image[gz.msgs.Image',
            # IMU
            '/model/humanoid_robot/link/torso/sensor/imu_sensor/imu'
            '@sensor_msgs/msg/Imu[gz.msgs.IMU',
        ],
        output='screen',
    )

    # Sensor logger (Week 4)
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

    # Joint controller (Week 3)
    joint_controller = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='digital_twin',
                executable='joint_controller',
                output='screen',
            )
        ],
    )

    # Object detector (Week 5 - only if model is trained)
    object_detector = TimerAction(
        period=6.0,
        actions=[
            Node(
                package='digital_twin',
                executable='detect_objects',
                output='screen',
            )
        ],
    )

    return LaunchDescription([
        gz_sim,
        spawn_robot,
        gz_bridge,
        sensor_logger,
        joint_controller,
        # object_detector,  # Uncomment after Week 5 training
    ])
