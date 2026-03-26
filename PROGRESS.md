# Digital Twin Project - Progress Tracker

## Week 1: Environment Setup ✅
- [x] Setup script created (`scripts/setup.sh`)
- [x] ROS 2 Humble installation steps
- [x] Gazebo (gz-sim7) installation
- [x] Project workspace structure
- [ ] **USER ACTION:** Run `./scripts/setup.sh` on Ubuntu 22.04

## Week 2: Build Realistic Scene ✅
- [x] World file with 3-point lighting (`worlds/home_environment.sdf`)
- [x] Wooden table model with PBR materials
- [x] 10 household objects (mug, book, phone, can, bowl, pen, apple, screwdriver, cup, tape)
- [x] Bin/basket model
- [x] Room walls
- [x] Physics configuration
- [ ] **USER ACTION:** Test with `gz sim worlds/home_environment.sdf`

## Week 3: Robot Model ✅
- [x] Simplified humanoid model (`models/humanoid_robot/model.sdf`)
- [x] Articulated arms (shoulder, elbow, wrist)
- [x] Articulated legs (hip, knee, ankle)
- [x] Head with neck joints
- [x] Joint state publisher plugin
- [x] Joint controller plugin
- [x] Python joint control script (`joint_controller.py`)
- [ ] **USER ACTION:** Spawn robot in world, test joint movements

## Week 4: Add Sensors ✅
- [x] RGB-D camera (via Gazebo camera plugin)
- [x] IMU sensor (torso-mounted)
- [x] Contact sensors (feet)
- [x] Sensor data logger at 50Hz (`sensor_logger.py`)
- [x] CSV logging for joints, IMU, contacts
- [x] Image logging (10Hz to disk)
- [ ] **USER ACTION:** Verify all sensor topics publishing

## Week 5: Object Detection ✅
- [x] Synthetic data generator (`scripts/generate_synthetic.py`)
- [x] YOLOv8 training script with CPU + Colab options (`scripts/train_yolo.py`)
- [x] ROS 2 detection node (`detect_objects.py`)
- [x] Dataset configuration (10 classes, YOLO format)
- [ ] **USER ACTION:** Generate 1000+ synthetic images
- [ ] **USER ACTION:** Train YOLOv8 (use Colab for free GPU!)
- [ ] **USER ACTION:** Test detection node

## Week 6-16: Coming Next
- [ ] Week 6: MoveIt 2 motion planning
- [ ] Week 7: First grasp
- [ ] Week 8: Place in bin
- [ ] Week 9: Multi-object task
- [ ] Week 10: Data collection campaign
- [ ] Week 11: Actuator specifications
- [ ] Week 12: Reliability improvements
- [ ] Week 13-16: Demo video + documentation

---

## Free Resources
| Resource | GPU | Limit | Link |
|----------|-----|-------|------|
| Google Colab | T4 (16GB) | 12hrs/day | colab.research.google.com |
| Kaggle | P100 (16GB) | 30hrs/week | kaggle.com/code |
| Lightning.ai | T4 | Some free hours | lightning.ai |
| HuggingFace Spaces | CPU | Free | huggingface.co |

**Best bet for YOLOv8 training:** Google Colab free tier.
50 epochs on 1000 images = ~15-30 min on T4 (vs 2-4 hours on CPU).
