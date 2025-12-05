/**
 * TypeScript Type Definitions for Physical AI RAG Chatbot Backend API
 *
 * Generated from: openapi.yaml
 * Version: 1.0.0
 *
 * Usage: Import these types in frontend React components
 * Example: import { ChatRequest, ChatResponse } from '@site/utils/types';
 */

// ============================================================================
// API Request Types
// ============================================================================

/**
 * Request model for global chat endpoint
 * POST /api/chat
 */
export interface ChatRequest {
  /** User's question (min 1 character, max 1000) */
  question: string;
}

/**
 * Request model for grounded chat endpoint
 * POST /api/chat/grounded
 */
export interface GroundedChatRequest {
  /** User's question (min 1 character, max 1000) */
  question: string;
  /** Selected text for grounded context (min 1, max 10000 characters) */
  selected_text: string;
}

// ============================================================================
// API Response Types
// ============================================================================

/**
 * Response model for both /api/chat and /api/chat/grounded endpoints
 */
export interface ChatResponse {
  /** LLM-generated answer */
  answer: string;
  /** Chapter citations */
  sources: Source[];
  /** Response latency in seconds */
  latency?: number;
  /** Context used for the response (optional) */
  context?: string;
}

/**
 * Reference to book chapter where information was retrieved
 */
export interface Source {
  /** Chapter number */
  chapter: number;
  /** Section name */
  section: string;
  /** Page reference (optional) */
  page?: string;
  /** Relevance score of the source (optional) */
  relevance_score?: number;
}

/**
 * Health check response
 * GET /api/health
 */
export interface HealthResponse {
  /** API health status */
  status: string;
  /** Qdrant connection status */
  qdrant_connected: boolean;
}

/**
 * Generic error response
 */
export interface ErrorResponse {
  /** Error message */
  detail: string;
}

/**
 * Validation error response (HTTP 422)
 */
export interface ValidationError {
  detail: Array<{
    /** Location of the validation error */
    loc: string[];
    /** Error message */
    msg: string;
    /** Error type */
    type: string;
  }>;
}

// ============================================================================
// Frontend-Specific Types (React Component State)
// ============================================================================

/**
 * Chat message in conversation thread
 */
export interface ChatMessage {
  /** Unique message ID (UUID) */
  id: string;
  /** Message text */
  content: string;
  /** Who sent the message */
  sender: "user" | "assistant";
  /** When message was created */
  timestamp: Date;
  /** Chapter citations (assistant messages only) */
  sources?: Source[];
  /** Whether response was grounded in selected text */
  grounded?: boolean; // Keep for UI logic if needed
}

/**
 * Chat widget UI state
 */
export interface ChatUIState {
  /** Whether chat widget is expanded */
  isOpen: boolean;
  /** Conversation history */
  messages: ChatMessage[];
  /** Whether API request is in flight */
  isLoading: boolean;
  /** Error message (if API call failed) */
  error: string | null;
  /** Session identifier (future: multi-turn) */
  conversationId: string | null;
}

/**
 * Selected text context for grounded queries
 */
export interface SelectionContext {
  /** The highlighted text content */
  text: string;
  /** Chapter slug where text was selected */
  sourceChapter: string | null;
  /** When selection occurred */
  selectionTime: Date | null;
}

// ============================================================================
// API Client Configuration
// ============================================================================

/**
 * API client configuration
 */
export interface APIConfig {
  /** Base URL for FastAPI backend */
  baseURL: string;
  /** Request timeout in milliseconds */
  timeout: number;
  /** Headers to include in all requests */
  headers: Record<string, string>;
}

/**
 * Default API configuration
 */
export const DEFAULT_API_CONFIG: APIConfig = {
  baseURL: "http://localhost:8000", // Default FastAPI server URL
  timeout: 30000, // 30 seconds (includes vector search + LLM inference)
  headers: {
    "Content-Type": "application/json",
  },
};

// ============================================================================
// Utility Types
// ============================================================================

/**
 * API response wrapper for error handling
 */
export type APIResult<T> =
  | { success: true; data: T }
  | { success: false; error: string };

/**
 * Chat mode (global vs grounded)
 */
export type ChatMode = "global" | "grounded";

/**
 * Theme mode (light vs dark)
 */
export type ThemeMode = "light" | "dark";

// ============================================================================
// Type Guards (Runtime Type Checking)
// ============================================================================

/**
 * Type guard for ChatResponse
 */
export function isChatResponse(obj: unknown): obj is ChatResponse {
  return (
    typeof obj === "object" &&
    obj !== null &&
    "answer" in obj &&
    "sources" in obj
  );
}

/**
 * Type guard for ErrorResponse
 */
export function isErrorResponse(obj: unknown): obj is ErrorResponse {
  return typeof obj === "object" && obj !== null && "detail" in obj;
}

/**
 * Type guard for HealthResponse
 */
export function isHealthResponse(obj: unknown): obj is HealthResponse {
  return (
    typeof obj === "object" &&
    obj !== null &&
    "status" in obj &&
    "qdrant_connected" in obj
  );
}

// ============================================================================
// Constants
// ============================================================================

/**
 * API endpoint paths
 */
export const API_ENDPOINTS = {
  HEALTH: "/health",
  CHAT: "/chat",
  CHAT_GROUNDED: "/chat/grounded",
  INDEX: "/index",
} as const;

/**
 * Validation constraints
 */
export const VALIDATION_RULES = {
  QUERY_MIN_LENGTH: 1, // Changed to 1 from 3 to allow shorter queries
  QUERY_MAX_LENGTH: 1000,
  SELECTED_TEXT_MIN_LENGTH: 10,
  SELECTED_TEXT_MAX_LENGTH: 10000,
  SELECTED_TEXT_TOKEN_WARNING: 6000, // Warn if selection > 6000 tokens
  MAX_MESSAGE_HISTORY: 100, // Prevent memory bloat
} as const;

/**
 * Default values
 */
export const DEFAULTS = {
  CONVERSATION_ID: null,
  THEME: "light" as ThemeMode,
  CHAT_MODE: "global" as ChatMode,
} as const;
