---
title: "Chapter 2: ROS 2 Architecture & DDS"
sidebar_label: "Chapter 2: Architecture & DDS"
sidebar_position: 3
---

# Chapter 2: ROS 2 Architecture & DDS

## The Data Distribution Service (DDS)

ROS 2 uses DDS as its middleware layer, providing:

- **Quality of Service (QoS)**: Reliability, durability, and latency control
- **Discovery**: Automatic node detection without a central master
- **Scalability**: Support for large-scale distributed systems

## QoS Profiles

```python
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

# Best effort for sensor data (speed over reliability)
sensor_qos = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,
    durability=DurabilityPolicy.VOLATILE,
    depth=10
)

# Reliable for critical commands
command_qos = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.TRANSIENT_LOCAL,
    depth=10
)
```

## Node Architecture

```
┌─────────────────────────────────────┐
│         ROS 2 Application           │
├─────────────────────────────────────┤
│  Node 1   │  Node 2   │  Node 3     │
├───────────┴───────────┴─────────────┤
│         ROS Client Library          │
│         (rclcpp / rclpy)            │
├─────────────────────────────────────┤
│              DDS Layer              │
│   (FastDDS / CycloneDDS / RTI)     │
├─────────────────────────────────────┤
│         Operating System            │
└─────────────────────────────────────┘
```

## Executors and Callbacks

ROS 2 uses executors to manage callback execution:

- **Single-threaded executor**: Simple, sequential processing
- **Multi-threaded executor**: Parallel callback execution
- **Static single-threaded executor**: Optimized for real-time systems

