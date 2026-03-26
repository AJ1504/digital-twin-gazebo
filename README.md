# Humanoid Robot Digital Twin - Gazebo Simulation

4-month plan for building a realistic humanoid robot digital twin in Gazebo.

## Quick Start

```bash
# 1. Run setup (Week 1)
chmod +x scripts/setup.sh
./scripts/setup.sh

# 2. Launch the world (Week 2)
source /opt/ros/humble/setup.bash
cd digital_twin_ws
colcon build
source install/setup.bash
ros2 launch digital_twin bringup.launch.py

# 3. Run object detection (Week 5)
python3 src/digital_twin/digital_twin/perception/detect_objects.py
```

## Timeline

| Month | Weeks | Focus |
|-------|-------|-------|
| 1     | 1-4   | Setup, Scene, Robot, Sensors |
| 2     | 5-8   | Perception, Motion Planning, First Grasp |
| 3     | 9-12  | Full Task, Data Collection, Actuator Specs |
| 4     | 13-16 | Polish, Demo Video, Documentation |

## Requirements

- Ubuntu 22.04 (native or WSL2)
- 16GB RAM minimum
- ~20GB disk space
- No GPU required (CPU training with YOLOv8n)

## Project Structure

```
digital-twin-gazebo/
├── scripts/
│   ├── setup.sh              # Week 1: Full environment setup
│   ├── generate_synthetic.py  # Week 5: Synthetic data generation
│   └── train_yolo.py          # Week 5: YOLOv8 training (use Colab for free GPU)
├── digital_twin_ws/
│   └── src/
│       └── digital_twin/
│           ├── worlds/         # Gazebo world files
│           ├── models/         # SDF/URDF models
│           ├── launch/         # ROS 2 launch files
│           └── digital_twin/   # Python nodes
├── data/                      # Synthetic training images
├── models_trained/            # Trained YOLO weights
└── docs/                      # Documentation
```
