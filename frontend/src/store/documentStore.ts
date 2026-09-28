import { create } from 'zustand';
import { DocumentSchema, DocumentationStep } from '../types/document';
import { ChatMessage } from '../types/chat';

interface DocumentState {
  currentDocument: DocumentSchema | null;
  isGenerating: boolean;
  chatMessages: ChatMessage[];
  selectedStepNumber: number | null;
  setCurrentDocument: (doc: DocumentSchema | null) => void;
  setIsGenerating: (generating: boolean) => void;
  addChatMessage: (msg: ChatMessage) => void;
  setChatMessages: (msgs: ChatMessage[]) => void;
  setSelectedStepNumber: (step: number | null) => void;
  updateSteps: (steps: DocumentationStep[], markdown: string) => void;
  resetDocument: () => void;
}

export const useDocumentStore = create<DocumentState>((set) => ({
  currentDocument: null,
  isGenerating: false,
  chatMessages: [],
  selectedStepNumber: null,
  setCurrentDocument: (doc) => set({ currentDocument: doc }),
  setIsGenerating: (generating) => set({ isGenerating: generating }),
  addChatMessage: (msg) =>
    set((state) => ({
      chatMessages: [...state.chatMessages, msg],
    })),
  setChatMessages: (msgs) => set({ chatMessages: msgs }),
  setSelectedStepNumber: (step) => set({ selectedStepNumber: step }),
  updateSteps: (steps, markdown) =>
    set((state) => ({
      currentDocument: state.currentDocument
        ? {
            ...state.currentDocument,
            steps,
            raw_markdown: markdown,
            version: state.currentDocument.version + 1,
          }
        : null,
    })),
  resetDocument: () =>
    set({
      currentDocument: null,
      isGenerating: false,
      chatMessages: [],
      selectedStepNumber: null,
    }),
}));
