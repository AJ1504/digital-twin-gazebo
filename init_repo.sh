#!/bin/bash
# Quick setup: initialize git repo and push to GitHub
# Run this from inside the digital-twin-gazebo/ directory

set -e

echo "🔧 Initializing git repo..."
git init
git add -A
git commit -m "Weeks 1-5: Gazebo humanoid digital twin

- Week 1: ROS 2 Humble + Gazebo setup script
- Week 2: Home environment (table, 10 objects, bin, 3-light setup)
- Week 3: 18-joint humanoid robot model + joint controller
- Week 4: Sensor suite (camera, IMU, contacts) + 50Hz data logger
- Week 5: Object detection pipeline (synthetic data + YOLOv8 + ROS 2 node)"

echo ""
echo "📡 Creating GitHub repo and pushing..."
gh repo create digital-twin-gazebo --public --source=. --push

echo ""
echo "✅ Done! Your repo is live."
echo "Clone with: gh repo clone $USER/digital-twin-gazebo"
