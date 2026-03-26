#!/bin/bash
# =============================================================================
# Week 1: Full Environment Setup Script
# Installs ROS 2 Humble, Gazebo (gz-sim7), and project dependencies
# For Ubuntu 22.04 (native or WSL2)
# =============================================================================

set -e

echo "=========================================="
echo "Digital Twin - Week 1 Environment Setup"
echo "=========================================="

# --- Pre-checks ---
echo "[1/8] Checking system..."
if ! grep -q "22.04" /etc/os-release 2>/dev/null; then
    echo "⚠️  Warning: This script is tested on Ubuntu 22.04"
    echo "   Detected: $(lsb_release -d 2>/dev/null || cat /etc/os-release | grep PRETTY_NAME)"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
fi

# --- System Update ---
echo "[2/8] Updating system packages..."
sudo apt update && sudo apt upgrade -y

# --- ROS 2 Humble ---
echo "[3/8] Installing ROS 2 Humble..."
if ! command -v ros2 &> /dev/null; then
    # Add ROS 2 apt repository
    sudo apt install -y software-properties-common curl
    sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

    sudo apt update
    sudo apt install -y ros-humble-desktop
    sudo apt install -y python3-colcon-common-extensions python3-rosdep python3-pip

    # Initialize rosdep
    sudo rosdep init 2>/dev/null || true
    rosdep update

    # Add to bashrc
    echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc
    echo 'source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash' >> ~/.bashrc

    echo "✅ ROS 2 Humble installed"
else
    echo "✅ ROS 2 Humble already installed"
fi

source /opt/ros/humble/setup.bash

# --- Gazebo (gz-sim7) ---
echo "[4/8] Installing Gazebo (gz-sim7)..."
if ! command -v gz &> /dev/null; then
    sudo apt install -y ros-humble-ros-gz
    echo "✅ Gazebo installed"
else
    echo "✅ Gazebo already installed"
fi

# --- MoveIt 2 (Week 6 prep) ---
echo "[5/8] Installing MoveIt 2..."
sudo apt install -y ros-humble-moveit
echo "✅ MoveIt 2 installed"

# --- Python Dependencies ---
echo "[6/8] Installing Python packages..."
pip3 install --user \
    ultralytics \
    opencv-python-headless \
    numpy \
    pandas \
    matplotlib \
    transforms3d \
    pyyaml

echo "✅ Python packages installed"

# --- Create Project Workspace ---
echo "[7/8] Creating project workspace..."
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WS_DIR="$PROJECT_DIR/digital_twin_ws"
SRC_DIR="$WS_DIR/src"

mkdir -p "$SRC_DIR"

# Create ROS 2 package if not exists
if [ ! -d "$SRC_DIR/digital_twin" ]; then
    cd "$SRC_DIR"
    ros2 pkg create digital_twin \
        --build-type ament_python \
        --dependencies rclpy std_msgs sensor_msgs geometry_msgs vision_msgs \
        moveit_ros_planning_interface
    echo "✅ ROS 2 package created"
fi

# Copy our source files into the package
echo "[8/8] Installing project files..."
cp -r "$PROJECT_DIR/src/"* "$SRC_DIR/digital_twin/digital_twin/" 2>/dev/null || true

# Build
cd "$WS_DIR"
colcon build --symlink-install
source "$WS_DIR/install/setup.bash"

# Add workspace sourcing to bashrc
echo "source $WS_DIR/install/setup.bash" >> ~/.bashrc

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. source ~/.bashrc"
echo "  2. ros2 launch digital_twin bringup.launch.py"
echo ""
echo "To test Gazebo:"
echo "  gz sim shapes.sdf"
echo ""
