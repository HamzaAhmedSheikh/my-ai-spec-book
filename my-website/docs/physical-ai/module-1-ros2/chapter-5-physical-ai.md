---
title: "Chapter 5: ROS 2 for Physical AI"
sidebar_label: "Chapter 5: Physical AI"
sidebar_position: 6
---

# Chapter 5: ROS 2 for Physical AI

## Integration with AI Frameworks

ROS 2 bridges the gap between AI models and physical robots:

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import torch
import torchvision.transforms as transforms

class VisionNode(Node):
    def __init__(self):
        super().__init__('vision_node')
        self.bridge = CvBridge()

        # Load AI model
        self.model = torch.load('model.pth')
        self.model.eval()

        # Subscribe to camera
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        # Publish detections
        self.publisher = self.create_publisher(
            DetectionArray,
            '/detections',
            10
        )

    def image_callback(self, msg):
        # Convert ROS image to OpenCV
        cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')

        # Preprocess for model
        tensor = self.preprocess(cv_image)

        # Run inference
        with torch.no_grad():
            detections = self.model(tensor)

        # Publish results
        self.publish_detections(detections)
```

## Real-Time Control with ROS 2 Control

```yaml
controller_manager:
  ros__parameters:
    update_rate: 100  # Hz

    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

    diff_drive_controller:
      type: diff_drive_controller/DiffDriveController

diff_drive_controller:
  ros__parameters:
    left_wheel_names: ["left_wheel_joint"]
    right_wheel_names: ["right_wheel_joint"]

    wheel_separation: 0.4
    wheel_radius: 0.1

    publish_rate: 50.0
    odom_frame_id: odom
    base_frame_id: base_link
```

## Navigation Stack (Nav2)

```python
from nav2_simple_commander.robot_navigator import BasicNavigator
from geometry_msgs.msg import PoseStamped

def create_pose(x, y, theta):
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.orientation.z = sin(theta / 2.0)
    pose.pose.orientation.w = cos(theta / 2.0)
    return pose

navigator = BasicNavigator()

# Set initial pose
initial_pose = create_pose(0.0, 0.0, 0.0)
navigator.setInitialPose(initial_pose)

# Wait for Nav2 to activate
navigator.waitUntilNav2Active()

# Send goal
goal_pose = create_pose(5.0, 3.0, 1.57)
navigator.goToPose(goal_pose)

# Monitor progress
while not navigator.isTaskComplete():
    feedback = navigator.getFeedback()
    print(f'Distance remaining: {feedback.distance_remaining}')
```

## Best Practices for Physical AI

1. **Modular Design**: Separate perception, planning, and control
2. **Lifecycle Management**: Use managed nodes for clean startup/shutdown
3. **Safety Monitors**: Implement watchdogs and emergency stops
4. **Logging and Diagnostics**: Use ROS 2 logging and diagnostic tools
5. **Testing**: Unit tests with pytest, integration tests with launch_testing

## Common Pitfalls

- **QoS mismatches**: Ensure publisher and subscriber QoS are compatible
- **Transform frame errors**: Always check frame_id and timestamps
- **Executor overload**: Don't block callbacks with long computations
- **Resource leaks**: Properly destroy nodes and shutdown rclpy
- **Clock synchronization**: Use ROS time, not system time

---

## Summary

In this module, you learned:

1. **Chapter 1**: ROS 2 fundamentals and key concepts
2. **Chapter 2**: Architecture, DDS middleware, and QoS
3. **Chapter 3**: Building publisher/subscriber nodes and launch files
4. **Chapter 4**: Advanced patterns (services, actions, parameters, tf2)
5. **Chapter 5**: Integration with AI frameworks and physical robots

### Next Steps

- Complete the hands-on exercises in the lab section
- Build a simple mobile robot controller
- Integrate a camera-based object detector
- Explore Nav2 for autonomous navigation

### Additional Resources

- [Official ROS 2 Documentation](https://docs.ros.org/)
- [ROS 2 Design](https://design.ros2.org/)
- [Nav2 Documentation](https://navigation.ros.org/)
- [ROS 2 Control](https://control.ros.org/)

