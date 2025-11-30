import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <p className={styles.heroDescription}>
          A comprehensive guide to building intelligent robots using ROS 2, NVIDIA Isaac, 
          and cutting-edge AI models. From simulation to deployment.
        </p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/physical-ai/introduction">
            Start Learning →
          </Link>
          <Link
            className={clsx('button button--outline button--lg', styles.buttonOutline)}
            to="/docs/physical-ai/quarter-overview">
            View Course Overview
          </Link>
        </div>
        <div className={styles.stats}>
          <div className={styles.stat}>
            <div className={styles.statNumber}>10</div>
            <div className={styles.statLabel}>Weeks</div>
          </div>
          <div className={styles.stat}>
            <div className={styles.statNumber}>5</div>
            <div className={styles.statLabel}>Major Parts</div>
          </div>
          <div className={styles.stat}>
            <div className={styles.statNumber}>AI-Powered</div>
            <div className={styles.statLabel}>Chatbot Support</div>
          </div>
        </div>
      </div>
    </header>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title="Home"
      description="Physical AI & Humanoid Robotics - A comprehensive textbook for building intelligent physical systems with ROS 2, NVIDIA Isaac, and AI">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
