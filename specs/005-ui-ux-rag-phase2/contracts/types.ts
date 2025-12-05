/**
 * TypeScript Type Definitions for Physical AI Book RAG Chatbot API
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
 * Request model for global context chat (full-book search)
 * POST /chat
 */
export interface ChatRequest {
  /** User's question about the book (3-1000 characters) */
  query: string;
  /** Optional session identifier for multi-turn conversations */
  conversation_id?: string;
}

/**
 * Request model for grounded context chat (selected text mode)
 * POST /chat/grounded
 */
export interface GroundedChatRequest {
  /** User's question about the selected text (3-1000 characters) */
  query: string;
  /** Text highlighted by user from book page (10-10000 characters) */
  selected_text: string;
  /** Chapter slug where text was selected (optional metadata) */
  source_chapter?: string;
  /** Optional session identifier */
  conversation_id?: string;
}

// ============================================================================
// API Response Types
// ============================================================================

/**
 * Response model for both /chat and /chat/grounded endpoints
 */
export interface ChatResponse {
  /** LLM-generated response */
  answer: string;
  /** Chapter citations (global mode only) */
  sources?: SourceCitation[];
  /** Confirmation of selected text (grounded mode only) */
  grounded_in?: string;
  /** Session identifier */
  conversation_id: string;
  /** Whether response used selected text (true) or full-book search (false) */
  grounded: boolean;
}

/**
 * Reference to book chapter where information was retrieved
 */
export interface SourceCitation {
  /** Chapter slug (e.g., 'module-1/ros2-architecture') */
  chapter: string;
  /** Human-readable chapter title */
  title: string;
  /** Cosine similarity score (0.0-1.0, higher = more relevant) */
  relevance_score?: number;
}

/**
 * Health check response
 * GET /health
 */
export interface HealthResponse {
  /** API health status */
  status: 'healthy' | 'degraded';
  /** API version (semver) */
  version: string;
  /** Current server time (ISO 8601) */
  timestamp?: string;
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
  sender: 'user' | 'assistant';
  /** When message was created */
  timestamp: Date;
  /** Chapter citations (assistant messages only) */
  sources?: SourceCitation[];
  /** Whether response was grounded in selected text */
  grounded?: boolean;
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
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 30000, // 30 seconds (includes vector search + LLM inference)
  headers: {
    'Content-Type': 'application/json',
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
export type ChatMode = 'global' | 'grounded';

/**
 * Theme mode (light vs dark)
 */
export type ThemeMode = 'light' | 'dark';

// ============================================================================
// Type Guards (Runtime Type Checking)
// ============================================================================

/**
 * Type guard for ChatResponse
 */
export function isChatResponse(obj: unknown): obj is ChatResponse {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'answer' in obj &&
    'conversation_id' in obj &&
    'grounded' in obj
  );
}

/**
 * Type guard for ErrorResponse
 */
export function isErrorResponse(obj: unknown): obj is ErrorResponse {
  return typeof obj === 'object' && obj !== null && 'detail' in obj;
}

/**
 * Type guard for HealthResponse
 */
export function isHealthResponse(obj: unknown): obj is HealthResponse {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'status' in obj &&
    'version' in obj
  );
}

// ============================================================================
// Constants
// ============================================================================

/**
 * API endpoint paths
 */
export const API_ENDPOINTS = {
  HEALTH: '/health',
  CHAT_GLOBAL: '/chat',
  CHAT_GROUNDED: '/chat/grounded',
} as const;

/**
 * Validation constraints
 */
export const VALIDATION_RULES = {
  QUERY_MIN_LENGTH: 3,
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
  THEME: 'light' as ThemeMode,
  CHAT_MODE: 'global' as ChatMode,
} as const;

// ============================================================================
// Example Usage (Documentation)
// ============================================================================

/**
 * Example: Calling global context chat
 *
 * ```typescript
 * import { ChatRequest, ChatResponse, APIResult } from './types';
 * import { apiClient } from './api';
 *
 * async function askGlobalQuestion(query: string): Promise<APIResult<ChatResponse>> {
 *   try {
 *     const request: ChatRequest = { query };
 *     const response = await apiClient.post<ChatResponse>('/chat', request);
 *     return { success: true, data: response.data };
 *   } catch (error) {
 *     return { success: false, error: error.message };
 *   }
 * }
 * ```
 */

/**
 * Example: Calling grounded context chat
 *
 * ```typescript
 * import { GroundedChatRequest, ChatResponse, APIResult } from './types';
 * import { apiClient } from './api';
 *
 * async function askGroundedQuestion(
 *   query: string,
 *   selectedText: string,
 *   sourceChapter?: string
 * ): Promise<APIResult<ChatResponse>> {
 *   try {
 *     const request: GroundedChatRequest = {
 *       query,
 *       selected_text: selectedText,
 *       source_chapter: sourceChapter,
 *     };
 *     const response = await apiClient.post<ChatResponse>('/chat/grounded', request);
 *     return { success: true, data: response.data };
 *   } catch (error) {
 *     return { success: false, error: error.message };
 *   }
 * }
 * ```
 */

/**
 * Example: Managing chat UI state
 *
 * ```typescript
 * import { useState } from 'react';
 * import { ChatUIState, ChatMessage } from './types';
 *
 * function useChatState() {
 *   const [state, setState] = useState<ChatUIState>({
 *     isOpen: false,
 *     messages: [],
 *     isLoading: false,
 *     error: null,
 *     conversationId: null,
 *   });
 *
 *   const addMessage = (message: ChatMessage) => {
 *     setState(prev => ({
 *       ...prev,
 *       messages: [...prev.messages, message],
 *     }));
 *   };
 *
 *   return { state, setState, addMessage };
 * }
 * ```
 */
