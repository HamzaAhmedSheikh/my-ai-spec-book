---
title: "Student Kit Options"
sidebar_label: "Student Kits"
sidebar_position: 9
---

### **3\. The Robot Lab**

For the "Physical" part of the course, you have three tiers of options depending on budget.

#### **Option A: The "Proxy" Approach (Recommended for Budget)**

Use a quadruped (dog) or a robotic arm as a proxy. The software principles (ROS 2, VSLAM, Isaac Sim) transfer 90% effectively to humanoids.

* **Robot:** **Unitree Go2 Edu** (\~$1,800 \- $3,000).
* **Pros:** Highly durable, excellent ROS 2 support, affordable enough to have multiple units.
* **Cons:** Not a biped (humanoid).

#### **Option B: The "Miniature Humanoid" Approach**

Small, table-top humanoids.

* **Robot:** **Unitree H1** is too expensive ($90k+), so look at **Unitree G1** (\~$16k) or **Robotis OP3** (older, but stable, \~$12k).
* **Budget Alternative:** **Hiwonder TonyPi Pro** (\~$600).
  * *Warning:* The cheap kits (Hiwonder) usually run on Raspberry Pi, which **cannot** run NVIDIA Isaac ROS efficiently. You would use these only for kinematics (walking) and use the Jetson kits for AI.

#### **Option C: The "Premium" Lab (Sim-to-Real specific)**

If the goal is to actually deploy the Capstone to a real humanoid:

* **Robot:** **Unitree G1 Humanoid**.
  * *Why:* It is one of the few commercially available humanoids that can actually walk dynamically and has an SDK open enough for students to inject their own ROS 2 controllers.

### **4\. Summary of Architecture**

To teach this successfully, your lab infrastructure should look like this:

| Component | Hardware | Function |
| :---- | :---- | :---- |
| **Sim Rig** | PC with RTX 4080 \+ Ubuntu 22.04 | Runs Isaac Sim, Gazebo, Unity, and trains LLM/VLA models. |
| **Edge Brain** | Jetson Orin Nano | Runs the "Inference" stack. Students deploy their code here. |
| **Sensors** | RealSense Camera \+ Lidar | Connected to the Jetson to feed real-world data to the AI. |
| **Actuator** | Unitree Go2 or G1 (Shared) | Receives motor commands from the Jetson. |

If you do not have access to RTX-enabled workstations, we must restructure the course to rely entirely on cloud-based instances (like AWS RoboMaker or NVIDIA's cloud delivery for Omniverse), though this introduces significant latency and cost complexity.
