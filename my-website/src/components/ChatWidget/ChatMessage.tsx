/**
 * ChatMessage Component
 * Renders individual messages in the chat conversation
 *
 * Features:
 * - Different styling for user vs assistant messages
 * - Displays source citations for assistant responses
 * - Shows grounded badge when applicable
 */

import React from 'react';
import { ChatMessage as ChatMessageType } from '@site/utils/types';
import styles from './styles.module.css';

interface ChatMessageProps {
  message: ChatMessageType;
}

export default function ChatMessage({ message }: ChatMessageProps): JSX.Element {
  const isUser = message.sender === 'user';

  return (
    <div className={`${styles.message} ${isUser ? styles.messageUser : styles.messageAssistant}`}>
      {/* Message Content */}
      <div className={styles.messageContent}>
        <p>{message.content}</p>

        {/* Source Citations (Assistant only) */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className={styles.sources}>
            <strong>📖 Sources:</strong>
            <ul>
              {message.sources.map((source, idx) => (
                <li key={idx}>
                  <a href={`/docs/${source.chapter}`} target="_blank" rel="noopener noreferrer">
                    {source.title}
                  </a>
                  {source.relevance_score && (
                    <span className={styles.relevanceScore}>
                      ({Math.round(source.relevance_score * 100)}% relevant)
                    </span>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Grounded Badge (Assistant only) */}
        {!isUser && message.grounded && (
          <div className={styles.groundedIndicator}>🎯 Response grounded in your selected text</div>
        )}
      </div>

      {/* Timestamp */}
      <div className={styles.messageTime}>{formatTime(message.timestamp)}</div>
    </div>
  );
}

/**
 * Format timestamp for display
 */
function formatTime(date: Date): string {
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  return `${hours}:${minutes}`;
}
