/**
 * ChatInput Component
 * Text input with submit button for user queries
 *
 * Features:
 * - Auto-resize textarea
 * - Submit on Enter (Shift+Enter for newline)
 * - Character counter
 * - Disabled state during loading
 */

import React, { useState, KeyboardEvent, useRef, useEffect } from 'react';
import styles from './styles.module.css';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

export default function ChatInput({ onSendMessage, disabled = false }: ChatInputProps): JSX.Element {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const MAX_LENGTH = 1000;

  /**
   * Auto-resize textarea based on content
   */
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  /**
   * Handle send message
   */
  const handleSend = () => {
    const trimmed = input.trim();
    if (trimmed.length >= 3 && trimmed.length <= MAX_LENGTH && !disabled) {
      onSendMessage(trimmed);
      setInput('');
    }
  };

  /**
   * Handle Enter key (submit) vs Shift+Enter (newline)
   */
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const isValid = input.trim().length >= 3 && input.trim().length <= MAX_LENGTH;

  return (
    <div className={styles.inputContainer}>
      <textarea
        ref={textareaRef}
        className={styles.inputTextarea}
        placeholder="Ask a question about the book..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        maxLength={MAX_LENGTH}
        rows={1}
      />
      <div className={styles.inputFooter}>
        <span className={styles.charCounter}>
          {input.length}/{MAX_LENGTH}
        </span>
        <button className={styles.sendButton} onClick={handleSend} disabled={!isValid || disabled}>
          {disabled ? '⏳' : '➤'}
        </button>
      </div>
    </div>
  );
}
