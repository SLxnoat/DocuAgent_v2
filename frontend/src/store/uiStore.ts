import { create } from 'zustand';

export type WorkspaceViewMode = 'browser' | 'split' | 'preview';

interface UIState {
  viewMode: WorkspaceViewMode;
  isControlPaneCollapsed: boolean;
  isChatPaneCollapsed: boolean;
  setViewMode: (mode: WorkspaceViewMode) => void;
  toggleControlPane: () => void;
  toggleChatPane: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  viewMode: 'split',
  isControlPaneCollapsed: false,
  isChatPaneCollapsed: false,
  setViewMode: (mode) => set({ viewMode: mode }),
  toggleControlPane: () => set((state) => ({ isControlPaneCollapsed: !state.isControlPaneCollapsed })),
  toggleChatPane: () => set((state) => ({ isChatPaneCollapsed: !state.isChatPaneCollapsed })),
}));
