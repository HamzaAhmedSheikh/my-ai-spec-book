/**
 * Docusaurus Root Theme Wrapper
 * Provides global SelectionContext for text selection tracking
 *
 * This component wraps the entire Docusaurus site and provides:
 * - Global text selection listener using window.getSelection()
 * - React Context to share selected text with ChatWidget component
 * - Automatic cleanup on navigation
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import ChatWidget from '../components/ChatWidget/ChatWidget';

/**
 * Selection Context Type
 */
export interface SelectionContextType {
  selectedText: string;
  sourceChapter: string | null;
  selectionTime: Date | null;
  setSelectedText: (text: string, chapter?: string) => void;
  clearSelection: () => void;
}

/**
 * Create Selection Context
 */
export const SelectionContext = createContext<SelectionContextType>({
  selectedText: '',
  sourceChapter: null,
  selectionTime: null,
  setSelectedText: () => {},
  clearSelection: () => {},
});

/**
 * Hook to use Selection Context
 */
export function useSelection(): SelectionContextType {
  return useContext(SelectionContext);
}

/**
 * Root component wrapping entire Docusaurus site
 */
export default function Root({ children }: { children: ReactNode }): JSX.Element {
  const [selectedText, setSelectedTextState] = useState<string>('');
  const [sourceChapter, setSourceChapter] = useState<string | null>(null);
  const [selectionTime, setSelectionTime] = useState<Date | null>(null);

  /**
   * Handle text selection across the page
   */
  useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection();

      // Check if selection exists and meets minimum length (10 chars)
      if (selection && selection.toString().trim().length >= 10) {
        const text = selection.toString().trim();

        // Extract source chapter from current URL path
        const pathMatch = window.location.pathname.match(/\/docs\/([^/]+\/[^/]+)/);
        const chapter = pathMatch ? pathMatch[1] : null;

        setSelectedTextState(text);
        setSourceChapter(chapter);
        setSelectionTime(new Date());

        console.log(`[SelectionContext] Text selected: ${text.substring(0, 50)}... (${text.length} chars)`);
      }
    };

    // Attach listener to mouseup event (after text selection completes)
    document.addEventListener('mouseup', handleSelection);

    // Cleanup on unmount
    return () => {
      document.removeEventListener('mouseup', handleSelection);
    };
  }, []);

  /**
   * Clear selection programmatically
   */
  const clearSelection = () => {
    setSelectedTextState('');
    setSourceChapter(null);
    setSelectionTime(null);
    console.log('[SelectionContext] Selection cleared');
  };

  /**
   * Set selection programmatically
   */
  const setSelectedText = (text: string, chapter?: string) => {
    setSelectedTextState(text.trim());
    setSourceChapter(chapter || null);
    setSelectionTime(new Date());
  };

  const contextValue: SelectionContextType = {
    selectedText,
    sourceChapter,
    selectionTime,
    setSelectedText,
    clearSelection,
  };

  return (
    <SelectionContext.Provider value={contextValue}>
      {children}
      <ChatWidget />
    </SelectionContext.Provider>
  );
}
