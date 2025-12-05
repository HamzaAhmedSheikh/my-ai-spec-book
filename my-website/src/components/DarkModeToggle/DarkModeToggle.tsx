/**
 * Dark Mode Toggle Component
 * Uses Docusaurus built-in color mode hook
 *
 * Features:
 * - Syncs with system preferences (if respectPrefersColorScheme: true)
 * - Persists to localStorage automatically
 * - Smooth icon transition
 */

import React from "react";
import { useColorMode } from "@docusaurus/theme-common";
import styles from "./styles.module.css";

export default function DarkModeToggle() {
  const { colorMode, setColorMode } = useColorMode();

  const handleToggle = () => {
    setColorMode(colorMode === "dark" ? "light" : "dark");
  };

  return (
    <button
      className={styles.toggle}
      onClick={handleToggle}
      aria-label={`Switch to ${colorMode === "dark" ? "light" : "dark"} mode`}
      title={`Currently in ${colorMode} mode. Click to switch.`}
    >
      <span className={styles.icon}>{colorMode === "dark" ? "☀️" : "🌙"}</span>
    </button>
  );
}
