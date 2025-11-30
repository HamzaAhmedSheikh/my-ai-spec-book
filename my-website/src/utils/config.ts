// src/utils/config.ts
import { APIConfig } from "./types"; // Import the interface

/**
 * Default API configuration, sourcing environment variables securely.
 */
export const DEFAULT_API_CONFIG: APIConfig = {
  // Access variables using the method configured by your build tool (Solution 1)
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
};
