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
 * Request model for chat endpoint (both global and grounded modes)
 * POST /api/chat
 */
export interface ChatRequest {
  /** User's question (min 1 character) */
  query: string;
  /** Optional selected text for context mode */
  selection_context?: string;
  /** Query mode: 'global' or 'context' */
  mode: 'global' | 'context';
  /** Number of chunks to retrieve (default 5, range 1-20) */
  top_k?: number;
  /** Optional session identifier for multi-turn conversations */
  conversation_id?: string;
}

// ============================================================================
// API Response Types
// ============================================================================

/**
 * Response model for the /api/chat endpoint
 */
export interface ChatResponse {
  /** LLM-generated answer */
  answer: string;
  /** Chapter citations */
  sources: SourceCitation[];
  /** Query mode used for the response */
  mode: 'global' | 'context';
  /** Session identifier */
  conversation_id?: string; // Made optional as per backend for consistency, though often present
}

/**
 * Reference to book chapter where information was retrieved
 */
export interface SourceCitation {
  /** Chapter slug (e.g., 'physical-ai/module-1-ros2/chapter-1-introduction') */
  book: string; // Renamed from 'chapter' to 'book' to match backend
  /** Relevance score of the source */
  score: number;
  /** Index of the chunk within the source */
  chunk_index: number;
}


/**
 * Health check response
 * GET /api/health
 */
export interface HealthResponse {
  /** API health status */
  status: 'healthy' | 'degraded';
  /** Qdrant connection status */
  qdrant: string;
  /** Number of collections in Qdrant */
  collections: number;
  /** Embedding model used */
  embedding_model: string;
  /** LLM model used */
  llm_model: string;
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
  baseURL: 'http://localhost:8000', // Default FastAPI server URL
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
export type ChatMode = 'global' | 'context'; // Changed from 'global' | 'grounded' to match backend

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
    'mode' in obj &&
    'sources' in obj
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
    'qdrant' in obj
  );
}

// ============================================================================
// Constants
// ============================================================================

/**
 * API endpoint paths
 */
export const API_ENDPOINTS = {
  HEALTH: '/api/health',
  CHAT: '/api/chat', // Unified chat endpoint
  INDEX: '/api/index', // For indexing book content (admin endpoint)
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
  THEME: 'light' as ThemeMode,
  CHAT_MODE: 'global' as ChatMode,
} as const;


 */
