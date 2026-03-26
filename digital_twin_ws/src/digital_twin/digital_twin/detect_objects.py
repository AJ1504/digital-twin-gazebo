"""
Week 5: ROS 2 Object Detection Node (Updated for MJCF Humanoid)
Subscribes to head camera, runs YOLOv8 inference, publishes detections.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
import json
import os

try:
    from cv_bridge import CvBridge
    import cv2
    from ultralytics import YOLO
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install opencv-python-headless ultralytics")
    raise

# Object classes (must match training)
CLASSES = [
    'mug', 'book', 'phone', 'can', 'bowl',
    'pen', 'apple', 'screwdriver', 'cup', 'tape'
]


class ObjectDetector(Node):
    """Real-time object detection using YOLOv8."""

    def __init__(self):
        super().__init__('object_detector')

        # Load model
        model_path = os.path.expanduser(
            '~/digital-twin-gazebo/models_trained/household_objects/weights/best.pt'
        )
        if not os.path.exists(model_path):
            self.get_logger().warn(
                f'Model not found at {model_path}, using pretrained yolov8n'
            )
            model_path = 'yolov8n.pt'

        self.model = YOLO(model_path)
        self.bridge = CvBridge()

        self.conf_threshold = 0.5
        self.iou_threshold = 0.45

        # Publishers
        self.detection_pub = self.create_publisher(
            String, '/detections', 10
        )
        self.annotated_image_pub = self.create_publisher(
            Image, '/detections/image', 10
        )

        # Subscribe to head camera (egocentric view)
        self.create_subscription(
            Image, '/camera/head/image',
            self.image_callback, 10
        )

        self.frame_count = 0
        self.total_detections = 0

        self.get_logger().info('Object Detector ready (using head camera)')

    def image_callback(self, msg):
        """Process camera frame and detect objects."""
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception as e:
            self.get_logger().error(f'Image conversion error: {e}')
            return

        # Run inference
        results = self.model(
            cv_image,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            verbose=False
        )

        # Parse results
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue

            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                cls_name = CLASSES[cls_id] if cls_id < len(CLASSES) else f'class_{cls_id}'

                detection = {
                    'class': cls_name,
                    'confidence': round(conf, 3),
                    'bbox': [round(x1), round(y1), round(x2), round(y2)],
                    'center': [round((x1 + x2) / 2), round((y1 + y2) / 2)],
                }
                detections.append(detection)

        # Publish detections as JSON
        if detections:
            msg = String()
            msg.data = json.dumps({
                'frame': self.frame_count,
                'detections': detections
            })
            self.detection_pub.publish(msg)
            self.total_detections += len(detections)

        # Publish annotated image
        annotated = results[0].plot() if results else cv_image
        annotated_msg = self.bridge.cv2_to_imgmsg(annotated, 'bgr8')
        self.annotated_image_pub.publish(annotated_msg)

        self.frame_count += 1
        if self.frame_count % 30 == 0:
            self.get_logger().info(
                f'Processed {self.frame_count} frames, '
                f'{self.total_detections} detections'
            )


def main(args=None):
    rclpy.init(args=args)
    node = ObjectDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
