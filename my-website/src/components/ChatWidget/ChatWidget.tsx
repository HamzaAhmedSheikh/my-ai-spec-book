/**
 * ChatWidget Component
 * Floating chatbot widget for RAG-based Q&A
 *
 * Features:
 * - Expands/collapses from bottom-right corner
 * - Integrates with SelectionContext for grounded mode
 * - Calls chatGlobal or chatGrounded API based on selected text
 * - Displays conversation history with sources
 */

import React, { useState } from "react";
import { useSelection } from "../../theme/Root";
import { chatGlobal, chatGrounded } from "../../utils/api";
import { ChatMessage as ChatMessageType, ChatUIState } from "../../utils/types";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import styles from "./styles.module.css";

export default function ChatWidget() {
  const { selectedText, sourceChapter, clearSelection } = useSelection();

  // Chat UI State
  const [state, setState] = useState<ChatUIState>({
    isOpen: false,
    messages: [],
    isLoading: false,
    error: null,
    conversationId: null,
  });

  /**
   * Toggle widget open/closed
   */
  const toggleWidget = () => {
    setState((prev) => ({ ...prev, isOpen: !prev.isOpen }));
  };

  /**
   * Handle user submitting a query
   */
  const handleSendMessage = async (query: string) => {
    // Clear any previous errors
    setState((prev) => ({ ...prev, error: null, isLoading: true }));

    // Add user message to conversation
    const userMessage: ChatMessageType = {
      id: crypto.randomUUID(),
      content: query,
      sender: "user",
      timestamp: new Date(),
    };

    setState((prev) => ({
      ...prev,
      messages: [...prev.messages, userMessage],
    }));

    try {
      // Determine mode: grounded (if text selected) or global
      const isGroundedMode = selectedText.length >= 10;

      let result;
      if (isGroundedMode) {
        // Call grounded endpoint
        result = await chatGrounded(query, selectedText);
      } else {
        // Call global endpoint
        result = await chatGlobal(query);
      }

      if (!result.success) {
        // API error
        setState((prev) => ({
          ...prev,
          isLoading: false,
          error: result.error,
        }));
        return;
      }

      // Add assistant message
      const assistantMessage: ChatMessageType = {
        id: crypto.randomUUID(),
        content: result.data.answer,
        sender: "assistant",
        timestamp: new Date(),
        sources: result.data.sources,
        grounded: isGroundedMode,
      };

      setState((prev) => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
        isLoading: false,
      }));

      // Clear selected text after successful grounded query
      if (isGroundedMode) {
        clearSelection();
      }
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: "An unexpected error occurred. Please try again.",
      }));
    }
  };

  /**
   * Clear conversation history
   */
  const handleClearChat = () => {
    setState((prev) => ({
      ...prev,
      messages: [],
      conversationId: null,
      error: null,
    }));
  };

  return (
    <>
      {/* Floating Button */}
      {!state.isOpen && (
        <button
          className={styles.chatButton}
          onClick={toggleWidget}
          aria-label="Open chat"
        >
          💬
        </button>
      )}

      {/* Expanded Widget */}
      {state.isOpen && (
        <div className={styles.chatWidget}>
          {/* Header */}
          <div className={styles.chatHeader}>
            <div className={styles.chatTitle}>
              <span>📚 Physical AI Assistant</span>
              {selectedText.length >= 10 && (
                <span
                  className={styles.groundedBadge}
                  title="Grounded in selected text"
                >
                  🎯 Grounded Mode
                </span>
              )}
            </div>
            <div className={styles.chatActions}>
              {state.messages.length > 0 && (
                <button
                  className={styles.clearButton}
                  onClick={handleClearChat}
                  title="Clear conversation"
                >
                  🗑️
                </button>
              )}
              <button
                className={styles.closeButton}
                onClick={toggleWidget}
                aria-label="Close chat"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Messages Container */}
          <div className={styles.messagesContainer}>
            {state.messages.length === 0 ? (
              <div className={styles.emptyState}>
                <p>👋 Hi! I'm your Physical AI textbook assistant.</p>
                {selectedText.length >= 10 ? (
                  <p className={styles.groundedHint}>
                    💡 You've selected text! Ask me a question about it, and
                    I'll answer based only on what you highlighted.
                  </p>
                ) : (
                  <p>
                    Ask me anything about the book, or highlight text to ask
                    specific questions.
                  </p>
                )}
              </div>
            ) : (
              state.messages.map((msg) => (
                <ChatMessage key={msg.id} message={msg} />
              ))
            )}

            {/* Error Display */}
            {state.error && (
              <div className={styles.errorMessage}>⚠️ {state.error}</div>
            )}

            {/* Loading Indicator */}
            {state.isLoading && (
              <div className={styles.loadingIndicator}>
                <span className={styles.typingDots}>
                  <span>.</span>
                  <span>.</span>
                  <span>.</span>
                </span>
              </div>
            )}
          </div>

          {/* Selected Text Preview (when text is selected) */}
          {selectedText.length >= 10 && (
            <div className={styles.selectedTextPreview}>
              <div className={styles.selectedTextHeader}>
                <span>🎯 Selected Text:</span>
                <button
                  className={styles.clearSelectionButton}
                  onClick={clearSelection}
                  title="Clear selection"
                >
                  ✕
                </button>
              </div>
              <div className={styles.selectedTextContent}>
                {selectedText.length > 150
                  ? `${selectedText.substring(0, 150)}...`
                  : selectedText}
              </div>
              <div className={styles.selectedTextFooter}>
                {selectedText.length} characters selected
              </div>
            </div>
          )}

          {/* Input */}
          <ChatInput
            onSendMessage={handleSendMessage}
            disabled={state.isLoading}
          />
        </div>
      )}
    </>
  );
}
