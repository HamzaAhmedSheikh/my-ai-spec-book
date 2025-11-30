/**
 * API Client for Physical AI RAG Chatbot Backend
 *
 * Provides functions to call FastAPI endpoints:
 * - chatGlobal: Full-book search with citations
 * - chatGrounded: Selected text mode (Magna Carta feature)
 * - healthCheck: API health status
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  ChatRequest, // Updated to unified ChatRequest
  ChatResponse,
  HealthResponse,
  APIResult,
  DEFAULT_API_CONFIG,
  API_ENDPOINTS, // Import API_ENDPOINTS
} from './types';

/**
 * Create axios instance with default configuration
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: DEFAULT_API_CONFIG.baseURL,
  timeout: DEFAULT_API_CONFIG.timeout,
  headers: DEFAULT_API_CONFIG.headers,
});

/**
 * Error handler - converts axios errors to user-friendly messages
 */
function handleError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError;

    // Network error
    if (axiosError.code === 'ECONNABORTED') {
      return 'Request timed out. The chatbot is taking too long to respond.';
    }

    if (!axiosError.response) {
      return 'Cannot connect to chatbot API. Please check your internet connection.';
    }

    // Server error
    const status = axiosError.response.status;
    const detail = (axiosError.response.data as any)?.detail;

    if (status === 422) {
      return `Invalid request: ${detail || 'Please check your input'}`;
    }

    if (status === 500) {
      return 'Chatbot service error. Please try again later.';
    }

    return detail || `API error (${status})`;
  }

  return 'An unexpected error occurred';
}

/**
 * Call global context chat endpoint
 * POST /api/chat
 *
 * @param query - User's question about the book
 * @param conversationId - Optional session ID
 * @returns API result with ChatResponse or error message
 */
export async function chatGlobal(
  query: string,
  conversationId?: string
): Promise<APIResult<ChatResponse>> {
  try {
    const request: ChatRequest = {
      query,
      mode: 'global', // Set mode for global chat
      conversation_id: conversationId,
    };

    const response = await apiClient.post<ChatResponse>(API_ENDPOINTS.CHAT, request);

    return { success: true, data: response.data };
  } catch (error) {
    return { success: false, error: handleError(error) };
  }
}

/**
 * Call grounded context chat endpoint
 * POST /api/chat
 *
 * @param query - User's question about the selected text
 * @param selectedText - Highlighted text from book page
 * @param conversationId - Optional session ID
 * @returns API result with ChatResponse or error message
 */
export async function chatGrounded(
  query: string,
  selectedText: string,
  // sourceChapter?: string, // Removed as it's not part of backend ChatRequest
  conversationId?: string
): Promise<APIResult<ChatResponse>> {
  try {
    const request: ChatRequest = {
      query,
      selection_context: selectedText, // Pass selected text as selection_context
      mode: 'context', // Set mode for grounded chat
      conversation_id: conversationId,
    };

    const response = await apiClient.post<ChatResponse>(API_ENDPOINTS.CHAT, request);

    return { success: true, data: response.data };
  } catch (error) {
    return { success: false, error: handleError(error) };
  }
}

/**
 * Check API health status
 * GET /api/health
 *
 * @returns API result with HealthResponse or error message
 */
export async function healthCheck(): Promise<APIResult<HealthResponse>> {
  try {
    const response = await apiClient.get<HealthResponse>(API_ENDPOINTS.HEALTH);

    return { success: true, data: response.data };
  } catch (error) {
    return { success: false, error: handleError(error) };
  }
}

/**
 * Update API base URL (useful for switching between local dev and production)
 *
 * @param newBaseURL - New API base URL
 */
export function setAPIBaseURL(newBaseURL: string): void {
  apiClient.defaults.baseURL = newBaseURL;
}
