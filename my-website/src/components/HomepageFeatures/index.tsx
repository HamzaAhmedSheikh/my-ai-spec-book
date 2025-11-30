import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';

type PartItem = {
  title: string;
  icon: string;
  description: ReactNode;
  link: string;
  chapters: number;
};

const BookParts: PartItem[] = [
  {
    title: 'Getting Started',
    icon: '🚀',
    description: (
      <>
        Begin your journey into Physical AI. Learn the fundamentals, course structure, 
        and what makes this field revolutionary for robotics and automation.
      </>
    ),
    link: '/docs/physical-ai/introduction',
    chapters: 5,
  },
  {
    title: 'Core Technologies',
    icon: '🛠️',
    description: (
      <>
        Master ROS 2, Gazebo simulation, and NVIDIA Isaac platform. Build the technical 
        foundation for developing intelligent physical systems.
      </>
    ),
    link: '/docs/physical-ai',
    chapters: 0, // Placeholder - will be populated as chapters are added
  },
  {
    title: 'AI Integration',
    icon: '🤖',
    description: (
      <>
        Explore vision-language-action models and LLM-based robotics. Learn how AI 
        transforms robots from programmed machines to adaptive agents.
      </>
    ),
    link: '/docs/physical-ai',
    chapters: 0, // Placeholder
  },
  {
    title: 'Hardware & Deployment',
    icon: '⚙️',
    description: (
      <>
        Understand hardware requirements, student kits, lab setup, and cloud environments. 
        Bridge the gap from simulation to real-world deployment.
      </>
    ),
    link: '/docs/physical-ai/hardware-requirements',
    chapters: 4,
  },
  {
    title: 'Assessment & Resources',
    icon: '📊',
    description: (
      <>
        Evaluate your learning through projects, quizzes, and capstone challenges. 
        Access supplementary materials and community resources.
      </>
    ),
    link: '/docs/physical-ai/assessments',
    chapters: 1,
  },
];

function Part({title, icon, description, link, chapters}: PartItem) {
  return (
    <div className={clsx('col col--4', styles.part)}>
      <Link to={link} className={styles.partCard}>
        <div className={styles.partIcon}>{icon}</div>
        <Heading as="h3" className={styles.partTitle}>
          {title}
        </Heading>
        <p className={styles.partDescription}>{description}</p>
        {chapters > 0 && (
          <div className={styles.partMeta}>
            {chapters} {chapters === 1 ? 'chapter' : 'chapters'}
          </div>
        )}
      </Link>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className={styles.sectionHeader}>
          <Heading as="h2">Explore the Curriculum</Heading>
          <p className={styles.sectionSubtitle}>
            Navigate through five thematic parts, from foundational concepts to advanced AI integration
          </p>
        </div>
        <div className="row">
          {BookParts.map((props, idx) => (
            <Part key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
