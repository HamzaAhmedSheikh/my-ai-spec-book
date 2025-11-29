---
title: "Hardware Requirements"
sidebar_label: "Hardware"
sidebar_position: 7
---

## **Hardware Requirements**

This course is technically demanding. It sits at the intersection of three heavy computational loads: **Physics Simulation** (Isaac Sim/Gazebo), **Visual Perception** (SLAM/Computer Vision), and **Generative AI** (LLMs/VLA).

Because the capstone involves a "Simulated Humanoid," the primary investment must be in **High-Performance Workstations**. However, to fulfill the "Physical AI" promise, you also need **Edge Computing Kits** (brains without bodies) or specific robot hardware.

### **1\. The "Digital Twin" Workstation (Required per Student)**

This is the most critical component. NVIDIA Isaac Sim is an Omniverse application that requires "RTX" (Ray Tracing) capabilities. Standard laptops (MacBooks or non-RTX Windows machines) **will not work**.

* **GPU (The Bottleneck):** NVIDIA **RTX 4070 Ti (12GB VRAM)** or higher.
  * *Why:* You need high VRAM to load the USD (Universal Scene Description) assets for the robot and environment, plus run the VLA (Vision-Language-Action) models simultaneously.
  * *Ideal:* RTX 3090 or 4090 (24GB VRAM) allows for smoother "Sim-to-Real" training.
* **CPU:** Intel Core i7 (13th Gen+) or AMD Ryzen 9\.
  * *Why:* Physics calculations (Rigid Body Dynamics) in Gazebo/Isaac are CPU-intensive.
* **RAM:** **64 GB DDR5** (32 GB is the absolute minimum, but will crash during complex scene rendering).
* **OS:** **Ubuntu 22.04 LTS**.
  * *Note:* While Isaac Sim runs on Windows, ROS 2 (Humble/Iron) is native to Linux. Dual-booting or dedicated Linux machines are mandatory for a friction-free experience.

###

###
