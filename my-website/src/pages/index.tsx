import type { ReactNode } from "react";
import clsx from "clsx";
import Link from "@docusaurus/Link";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import Layout from "@theme/Layout";
import Heading from "@theme/Heading";
import { useHistory } from "@docusaurus/router"; // Import useHistory

import styles from "./index.module.css";

const courses = [
  {
    title: "Getting Started",
    description:
      "Begin your journey into Physical AI and Humanoid Robotics with this essential introduction.",
    link: "docs/physical-ai/introduction/introduction-overview",
  },
  {
    title: "Module 1: The Robotic Nervous System (ROS 2)",
    description:
      "Learn the fundamentals of ROS 2 for building robust robotic applications.",
    link: "docs/physical-ai/module-1-ros2/overview",
  },
  {
    title: "Module 2: The Digital Twin (Gazebo & Unity)",
    description:
      "Explore simulation environments for robotics with Gazebo and Unity.",
    link: "docs/physical-ai/module-2-gazebo-unity/overview",
  },
  {
    title: "Module 3: The AI-Robot Brain (NVIDIA Isaac)",
    description:
      "Integrate advanced AI capabilities into your robots using NVIDIA Isaac.",
    link: "docs/physical-ai/module-3-nvidia-isaac/overview",
  },
  {
    title: "Module 4: Vision-Language-Action (VLA)",
    description:
      "Delve into Vision-Language-Action models for intelligent robot control.",
    link: "docs/physical-ai/module-4-vla/overview",
  },
];

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();

  return (
    <header className={clsx("hero hero--primary", styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <div>
          <p className="hero__subtitle">{siteConfig.tagline}</p>
          <p className={styles.heroDescription}>
            A comprehensive guide to building intelligent robots using ROS 2,
            NVIDIA Isaac, and cutting-edge AI models. From simulation to
            deployment.
          </p>
        </div>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to={`${siteConfig.baseUrl}docs/physical-ai/introduction/introduction-overview`}
          >
            Start Learning →
          </Link>
        </div>
      </div>
    </header>
  );
}

function CourseSection() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <section className={styles.courseSection}>
      <div className="container">
        <Heading as="h2" className={styles.courseSectionTitle}>
          Our Curriculum
        </Heading>
        <div className={styles.courseGrid}>
          {courses.map((course) => (
            <Link
              to={`${siteConfig.baseUrl}${course.link}`}
              className={styles.courseCard}
              key={course.title}
            >
              <Heading as="h3" className={styles.courseCardTitle}>
                {course.title}
              </Heading>
              <p className={styles.courseCardDescription}>
                {course.description}
              </p>
              <span className={styles.courseCardLink}>Learn More →</span>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}

export default function Home(): ReactNode {
  return (
    <Layout
      title="Home"
      description="Physical AI & Humanoid Robotics - A comprehensive textbook for building intelligent physical systems with ROS 2, NVIDIA Isaac, and AI"
    >
      <HomepageHeader />
      <main>
        <CourseSection />
      </main>
    </Layout>
  );
}
