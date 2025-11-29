---
title: "Cloud & Remote Lab Options"
sidebar_label: "Cloud Labs"
sidebar_position: 10
---

Building a "Physical AI" lab is a significant investment. You will have to choose between building a physical **On-Premise Lab at Home** (High CapEx) versus running a **Cloud-Native Lab** (High OpEx).

### **Option 2 High OpEx: The "Ether" Lab (Cloud-Native)**

*Best for: Rapid deployment, or students with weak laptops.*

**1\. Cloud Workstations (AWS/Azure)** Instead of buying PCs, you rent instances.

* **Instance Type:** AWS **g5.2xlarge** (A10G GPU, 24GB VRAM) or **g6e.xlarge**.
* **Software:** NVIDIA Isaac Sim on Omniverse Cloud (requires specific AMI).
* **Cost Calculation:**
  * Instance cost: \~$1.50/hour (spot/on-demand mix).
  * Usage: 10 hours/week × 12 weeks \= 120 hours.
  * Storage (EBS volumes for saving environments): \~$25/quarter.
  * **Total Cloud Bill:** **\~$205 per quarter**.

**2\. Local "Bridge" Hardware** You cannot eliminate hardware entirely for "Physical AI." You still need the edge devices to deploy the code physically.

* **Edge AI Kits:** You still need the Jetson Kit for the physical deployment phase.
  * **Cost:** **$700** (One-time purchase).
* **Robot:** You still need one physical robot for the final demo.
  * **Cost:** **$3,000** (Unitree Go2 Standard).

### **The Economy Jetson Student Kit**

*Best for: Learning ROS 2, Basic Computer Vision, and Sim-to-Real control.*

| Component | Model | Price (Approx.) | Notes |
| :---- | :---- | :---- | :---- |
| **The Brain** | **NVIDIA Jetson Orin Nano Super Dev Kit (8GB)** | **$249** | New official MSRP (Price dropped from \~$499). Capable of 40 TOPS. |
| **The Eyes** | **Intel RealSense D435i** | **$349** | Includes IMU (essential for SLAM). Do not buy the D435 (non-i). |
| **The Ears** | **ReSpeaker USB Mic Array v2.0** | **$69** | Far-field microphone for voice commands (Module 4). |
| **Wi-Fi** | (Included in Dev Kit) | $0 | The new "Super" kit includes the Wi-Fi module pre-installed. |
| **Power/Misc** | SD Card (128GB) \+ Jumper Wires | $30 | High-endurance microSD card required for the OS. |
| **TOTAL** |  | **\~$700 per kit** |  |

**3\. The Latency Trap (Hidden Cost)**

* Simulating in the cloud works well, but *controlling* a real robot from a cloud instance is dangerous due to latency.
* *Solution:* Students train in the Cloud, download the model (weights), and flash it to the local Jetson kit.
