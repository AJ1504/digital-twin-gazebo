"""
Week 5: YOLOv8 Training Script
Train on synthetic data from Gazebo.
Optimized for CPU-only training with YOLOv8n (nano).

FREE GPU OPTIONS:
  - Google Colab: https://colab.research.google.com (free T4 GPU, 12hrs/day)
  - Kaggle: https://www.kaggle.com/code (free P100 GPU, 30hrs/week)
  - Lightning.ai: https://lightning.ai (free GPU hours)

To use Colab:
  1. Upload this script and data/synthetic/ to Google Drive
  2. Open in Colab, mount Drive
  3. Run: !pip install ultralytics && python train_yolo.py
"""

import os
import sys
import time
from pathlib import Path

try:
    from ultralytics import YOLO
except ImportError:
    print("Installing ultralytics...")
    os.system(f'{sys.executable} -m pip install ultralytics')
    from ultralytics import YOLO


# Object classes
CLASSES = [
    'mug', 'book', 'phone', 'can', 'bowl',
    'pen', 'apple', 'screwdriver', 'cup', 'tape'
]


def create_dataset_yaml(data_dir: str) -> str:
    """Create dataset.yaml for YOLOv8 training."""
    data_path = Path(data_dir).absolute()

    yaml_content = f"""# Digital Twin Object Detection Dataset
# 10 household objects, synthetic from Gazebo

path: {data_path}
train: images/train
val: images/val

nc: {len(CLASSES)}
names: {CLASSES}
"""
    yaml_path = data_path / 'dataset.yaml'
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)

    return str(yaml_path)


def train_cpu(data_dir: str = 'data/synthetic', epochs: int = 50):
    """
    Train on CPU with YOLOv8n (nano model - fastest).
    Expected time: ~2-4 hours for 50 epochs on 1000 images.
    """
    print("=" * 50)
    print("YOLOv8 Training (CPU Mode)")
    print("=" * 50)

    yaml_path = create_dataset_yaml(data_dir)

    # Load nano model (smallest, fastest for CPU)
    model = YOLO('yolov8n.pt')

    print(f"Dataset: {yaml_path}")
    print(f"Epochs: {epochs}")
    print(f"Device: CPU")
    print(f"Estimated time: {epochs * 2:.0f}-{epochs * 4:.0f} minutes")
    print()

    start_time = time.time()

    # Train
    results = model.train(
        data=yaml_path,
        epochs=epochs,
        imgsz=640,
        batch=16,
        device='cpu',
        workers=4,
        project='models_trained',
        name='household_objects',
        exist_ok=True,
        patience=10,          # Early stopping after 10 epochs without improvement
        save_period=10,       # Save checkpoint every 10 epochs
        plots=True,           # Generate training plots
        verbose=True,
    )

    elapsed = time.time() - start_time
    print(f"\nTraining complete in {elapsed / 60:.1f} minutes")
    print(f"Best model: models_trained/household_objects/weights/best.pt")

    # Validate
    print("\nRunning validation...")
    metrics = model.val()
    print(f"mAP50: {metrics.box.map50:.3f}")
    print(f"mAP50-95: {metrics.box.map:.3f}")

    return results


def train_gpu_colab(data_dir: str = 'data/synthetic', epochs: int = 50):
    """
    Training instructions for Google Colab (free T4 GPU).
    Copy-paste this into a Colab cell.
    """
    colab_code = f'''
# === Google Colab Cell 1: Setup ===
!pip install ultralytics
from google.colab import drive
drive.mount('/content/drive')

# === Colab Cell 2: Train ===
from ultralytics import YOLO

model = YOLO('yolov8n.pt')

results = model.train(
    data='/content/drive/MyDrive/digital-twin/data/synthetic/dataset.yaml',
    epochs={epochs},
    imgsz=640,
    batch=32,      # T4 has 16GB VRAM, can use larger batch
    device=0,      # GPU
    workers=2,
    project='/content/drive/MyDrive/digital-twin/models_trained',
    name='household_objects',
    exist_ok=True,
    patience=10,
    save_period=10,
    plots=True,
)

# Expected time on T4: ~15-30 minutes for 50 epochs (10x faster than CPU)

# === Colab Cell 3: Download results ===
# Model is saved to Drive automatically
print(f"Best model saved to Drive!")
'''
    print("=" * 50)
    print("Google Colab Training Code (FREE GPU)")
    print("=" * 50)
    print(colab_code)

    # Save to file
    with open('scripts/colab_train.py', 'w') as f:
        f.write(colab_code)
    print("\nSaved to scripts/colab_train.py")
    print("Copy-paste this into Google Colab for 10x faster training!")


def quick_test(model_path: str = 'models_trained/household_objects/weights/best.pt'):
    """Quick test of trained model on sample images."""
    if not os.path.exists(model_path):
        print(f"Model not found: {model_path}")
        print("Train first with: python3 scripts/train_yolo.py")
        return

    model = YOLO(model_path)

    # Test on validation images
    val_dir = Path('data/synthetic/images/val')
    if val_dir.exists():
        images = list(val_dir.glob('*.png'))[:5]
        for img in images:
            results = model(str(img))
            results[0].show()  # Display results


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Train YOLOv8 for object detection')
    parser.add_argument('--mode', choices=['cpu', 'colab', 'test'], default='cpu',
                        help='Training mode')
    parser.add_argument('--data', default='data/synthetic', help='Dataset directory')
    parser.add_argument('--epochs', type=int, default=50, help='Number of epochs')
    parser.add_argument('--model', default='models_trained/household_objects/weights/best.pt',
                        help='Model path for testing')

    args = parser.parse_args()

    if args.mode == 'cpu':
        train_cpu(args.data, args.epochs)
    elif args.mode == 'colab':
        train_gpu_colab(args.data, args.epochs)
    elif args.mode == 'test':
        quick_test(args.model)
