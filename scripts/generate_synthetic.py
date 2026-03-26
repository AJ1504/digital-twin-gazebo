"""
Week 5: Synthetic Training Data Generator
Uses Gazebo camera to generate 1000+ labeled images of household objects.
Automatically varies camera angle, lighting, and object positions.
"""

import os
import random
import math
import json
import cv2
import numpy as np
from pathlib import Path

# Object classes matching our 10 household objects
OBJECT_CLASSES = {
    0: 'mug',
    1: 'book',
    2: 'phone',
    3: 'can',
    4: 'bowl',
    5: 'pen',
    6: 'apple',
    7: 'screwdriver',
    8: 'cup',
    9: 'tape',
}

# Object sizes for bounding box estimation (approximate, in meters)
OBJECT_SIZES = {
    'mug': (0.08, 0.09),
    'book': (0.15, 0.22),
    'phone': (0.07, 0.15),
    'can': (0.066, 0.12),
    'bowl': (0.14, 0.05),
    'pen': (0.01, 0.15),
    'apple': (0.08, 0.08),
    'screwdriver': (0.02, 0.20),
    'cup': (0.07, 0.08),
    'tape': (0.08, 0.025),
}


class SyntheticDataGenerator:
    """Generate synthetic training data from Gazebo camera images."""

    def __init__(self, output_dir='data/synthetic', num_images=1000):
        self.output_dir = Path(output_dir)
        self.num_images = num_images
        self.image_dir = self.output_dir / 'images'
        self.label_dir = self.output_dir / 'labels'
        self.image_dir.mkdir(parents=True, exist_ok=True)
        self.label_dir.mkdir(parents=True, exist_ok=True)

        # Camera parameters (matching our RGB-D camera setup)
        self.img_width = 640
        self.img_height = 480
        self.fov_h = 1.047  # 60 degrees horizontal FOV

    def generate_camera_poses(self, num_poses):
        """Generate random camera poses looking at the table."""
        poses = []
        for _ in range(num_poses):
            # Camera looks down at table from varying heights and angles
            height = random.uniform(1.4, 1.8)  # Robot head height range
            lateral = random.uniform(-0.3, 0.3)
            forward = random.uniform(-0.2, 0.2)
            yaw = random.uniform(-0.5, 0.5)
            pitch = random.uniform(-0.3, 0.1)
            poses.append({
                'position': (lateral, forward, height),
                'orientation': (0, pitch, yaw)
            })
        return poses

    def project_3d_to_2d(self, point_3d, camera_pose):
        """
        Simple pinhole camera projection.
        Converts 3D world point to 2D image coordinates.
        """
        # Simple projection (simplified - real version would use full transform matrix)
        cx, cy, cz = camera_pose['position']
        dx = point_3d[0] - cx
        dy = point_3d[1] - cy
        dz = point_3d[2] - cz

        if dz <= 0:
            return None

        # Project to normalized coordinates
        fx = self.img_width / (2 * math.tan(self.fov_h / 2))
        fy = fx  # Square pixels

        px = int(fx * dx / dz + self.img_width / 2)
        py = int(fy * dy / dz + self.img_height / 2)

        if 0 <= px < self.img_width and 0 <= py < self.img_height:
            return (px, py)
        return None

    def generate_yolo_label(self, objects_in_view, camera_pose):
        """Generate YOLO format label for objects in view."""
        labels = []
        for obj in objects_in_view:
            name = obj['name']
            pos = obj['position']
            size = OBJECT_SIZES.get(name, (0.1, 0.1))

            # Project center point
            center = self.project_3d_to_2d(pos, camera_pose)
            if center is None:
                continue

            # Estimate bounding box (simplified)
            # In real scenario, project all 8 corners and take min/max
            depth = pos[2] - camera_pose['position'][2]
            if depth <= 0:
                continue

            scale = 1.0 / depth
            w_px = int(size[0] * scale * self.img_width / (2 * math.tan(self.fov_h / 2)))
            h_px = int(size[1] * scale * self.img_width / (2 * math.tan(self.fov_h / 2)))

            # YOLO format: class_id center_x center_y width height (normalized)
            cx_norm = center[0] / self.img_width
            cy_norm = center[1] / self.img_height
            w_norm = w_px / self.img_width
            h_norm = h_px / self.img_height

            # Clamp to image bounds
            cx_norm = max(0, min(1, cx_norm))
            cy_norm = max(0, min(1, cy_norm))
            w_norm = max(0, min(1, w_norm))
            h_norm = max(0, min(1, h_norm))

            class_id = [k for k, v in OBJECT_CLASSES.items() if v == name]
            if class_id:
                labels.append(f"{class_id[0]} {cx_norm:.6f} {cy_norm:.6f} {w_norm:.6f} {h_norm:.6f}")

        return labels

    def generate_dataset_config(self):
        """Generate YOLOv8 dataset.yaml config file."""
        config = {
            'path': str(self.output_dir.absolute()),
            'train': 'images/train',
            'val': 'images/val',
            'nc': len(OBJECT_CLASSES),
            'names': list(OBJECT_CLASSES.values())
        }

        config_path = self.output_dir / 'dataset.yaml'
        with open(config_path, 'w') as f:
            import yaml
            yaml.dump(config, f, default_flow_style=False)

        print(f"Dataset config saved to {config_path}")
        return config_path

    def create_split_dirs(self):
        """Create train/val split directories."""
        for split in ['train', 'val']:
            (self.output_dir / 'images' / split).mkdir(parents=True, exist_ok=True)
            (self.output_dir / 'labels' / split).mkdir(parents=True, exist_ok=True)

    def run(self):
        """Main generation loop.
        NOTE: This is a scaffold. In practice, you'd:
        1. Launch Gazebo with the world
        2. Move camera to each pose via ROS 2
        3. Capture actual rendered images
        4. Use Gazebo's ground truth for bounding boxes

        This version generates the directory structure and config
        for the actual Gazebo-based generation.
        """
        self.create_split_dirs()

        # Generate camera poses
        poses = self.generate_camera_poses(self.num_images)

        # Save poses for the Gazebo capture script
        poses_path = self.output_dir / 'camera_poses.json'
        with open(poses_path, 'w') as f:
            json.dump(poses, f, indent=2)

        # Generate dataset config
        config_path = self.generate_dataset_config()

        # Generate placeholder labels (for development without Gazebo)
        # In production, these come from Gazebo ground truth
        object_positions = [
            {'name': 'mug', 'position': (0.1, 0.1, 0.82)},
            {'name': 'book', 'position': (-0.15, 0.05, 0.79)},
            {'name': 'phone', 'position': (0.25, -0.1, 0.785)},
            {'name': 'can', 'position': (0.3, 0.15, 0.815)},
            {'name': 'bowl', 'position': (-0.25, -0.15, 0.81)},
            {'name': 'pen', 'position': (0.05, 0.25, 0.782)},
            {'name': 'apple', 'position': (-0.3, 0.2, 0.82)},
            {'name': 'screwdriver', 'position': (0.15, -0.25, 0.785)},
            {'name': 'cup', 'position': (-0.05, -0.2, 0.815)},
            {'name': 'tape', 'position': (0.35, 0.0, 0.80)},
        ]

        for i, pose in enumerate(poses):
            split = 'train' if i < int(self.num_images * 0.8) else 'val'

            # Generate labels for this pose
            labels = self.generate_yolo_label(object_positions, pose)

            # Save label file
            label_path = self.output_dir / 'labels' / split / f'frame_{i:06d}.txt'
            with open(label_path, 'w') as f:
                f.write('\n'.join(labels))

            if (i + 1) % 100 == 0:
                print(f"Generated {i + 1}/{self.num_images} samples")

        print(f"\nDataset structure ready at {self.output_dir}")
        print(f"Train: {int(self.num_images * 0.8)} images")
        print(f"Val: {self.num_images - int(self.num_images * 0.8)} images")
        print(f"\nNext steps:")
        print(f"1. Launch Gazebo: ros2 launch digital_twin bringup.launch.py")
        print(f"2. Run capture: python3 scripts/capture_images.py")
        print(f"3. Train: python3 scripts/train_yolo.py")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--num-images', type=int, default=1000)
    parser.add_argument('--output', default='data/synthetic')
    args = parser.parse_args()

    gen = SyntheticDataGenerator(args.output, args.num_images)
    gen.run()
