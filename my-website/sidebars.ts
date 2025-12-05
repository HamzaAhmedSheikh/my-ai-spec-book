import type { SidebarsConfig } from "@docusaurus/plugin-content-docs";

const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    {
      type: "category",
      label: "Getting Started",
      collapsed: false,
      items: [
        "physical-ai/introduction/introduction-overview",
        // "physical-ai/introduction/why-physical-ai-matters",
        // "physical-ai/introduction/learning-outcomes",
        // "physical-ai/introduction/weekly-breakdown",
      ],
    },

    {
      type: "category",
      label: "Part 1: Foundational Robotics",
      collapsed: false,
      items: [
        {
          type: "category",
          label: "Module 1: The Robotic Nervous System (ROS 2)",
          collapsed: false,
          items: [
            "physical-ai/module-1-ros2/overview",
            "physical-ai/module-1-ros2/chapter-1-introduction",
            "physical-ai/module-1-ros2/chapter-2-architecture-dds",
            "physical-ai/module-1-ros2/chapter-3-building-first-app",
            "physical-ai/module-1-ros2/chapter-4-advanced-patterns",
            "physical-ai/module-1-ros2/chapter-5-physical-ai",
          ],
        },
        {
          type: "category",
          label: "Module 2: The Digital Twin (Gazebo & Unity)",
          collapsed: true,
          items: [
            "physical-ai/module-2-gazebo-unity/overview",
            "physical-ai/module-2-gazebo-unity/chapter-1-introduction",
            "physical-ai/module-2-gazebo-unity/chapter-2-robot-models",
            "physical-ai/module-2-gazebo-unity/chapter-3-sensors",
            "physical-ai/module-2-gazebo-unity/chapter-4-unity",
            "physical-ai/module-2-gazebo-unity/chapter-5-integration",
          ],
        },
      ],
    },

    {
      type: "category",
      label: "Part 2: Advanced AI for Robotics",
      collapsed: true,
      items: [
        {
          type: "category",
          label: "Module 3: The AI-Robot Brain (NVIDIA Isaac)",
          collapsed: true,
          items: [
            "physical-ai/module-3-nvidia-isaac/overview",
            "physical-ai/module-3-nvidia-isaac/chapter-1-introduction",
            "physical-ai/module-3-nvidia-isaac/chapter-2-isaac-sim",
            "physical-ai/module-3-nvidia-isaac/chapter-3-synthetic-data",
            "physical-ai/module-3-nvidia-isaac/chapter-4-isaac-ros",
            "physical-ai/module-3-nvidia-isaac/chapter-5-nav2-humanoids",
          ],
        },
        {
          type: "category",
          label: "Module 4: Vision-Language-Action (VLA)",
          collapsed: true,
          items: [
            "physical-ai/module-4-vla/overview",
            "physical-ai/module-4-vla/chapter-1-introduction",
            "physical-ai/module-4-vla/chapter-2-voice-to-action",
            "physical-ai/module-4-vla/chapter-3-cognitive-planning",
            "physical-ai/module-4-vla/chapter-4-nl-to-ros",
            "physical-ai/module-4-vla/chapter-5-capstone",
          ],
        },
      ],
    },

    // {
    //   type: "category",
    //   label: "⚙️ Hardware & Deployment",
    //   collapsed: true,
    //   items: [
    //     "physical-ai/hardware/hardware-requirements",
    //     "physical-ai/hardware/student-kits",
    //     "physical-ai/hardware/lab-setup",
    //     "physical-ai/hardware/cloud-lab-options",
    //   ],
    // },

    // {
    //   type: "category",
    //   label: "📊 Assessment & Resources",
    //   collapsed: true,
    //   items: ["physical-ai/assessments"],
    // },
  ],
};

export default sidebars;
