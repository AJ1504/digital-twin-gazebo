"""Setup for digital_twin ROS 2 package."""
from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'digital_twin'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Install launch files
        ('share/' + package_name + '/launch',
         glob('launch/*.launch.py')),
        # Install world files
        ('share/' + package_name + '/worlds',
         glob('worlds/*.sdf')),
        # Install model files (recursively)
        *[
            (os.path.join('share', package_name, os.path.dirname(f)), [f])
            for f in glob('models/**/*', recursive=True)
            if os.path.isfile(f)
        ],
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='digital-twin',
    maintainer_email='dev@digital-twin.local',
    description='Humanoid robot digital twin simulation in Gazebo',
    license='MIT',
    entry_points={
        'console_scripts': [
            'joint_controller = digital_twin.joint_controller:main',
            'sensor_logger = digital_twin.sensor_logger:main',
            'detect_objects = digital_twin.detect_objects:main',
        ],
    },
)
