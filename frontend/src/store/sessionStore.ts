import { create } from 'zustand';
import { SessionResponse, SessionStatus } from '../types/session';
import { ActionTrace } from '../types/trace';

interface SessionState {
  currentSession: SessionResponse | null;
  actions: ActionTrace[];
  isRecording: boolean;
  status: SessionStatus;
  setCurrentSession: (session: SessionResponse | null) => void;
  addAction: (action: ActionTrace) => void;
  setActions: (actions: ActionTrace[]) => void;
  setStatus: (status: SessionStatus) => void;
  resetSession: () => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  currentSession: null,
  actions: [],
  isRecording: false,
  status: 'idle',
  setCurrentSession: (session) =>
    set({
      currentSession: session,
      status: session ? session.status : 'idle',
      isRecording: session?.status === 'recording',
    }),
  addAction: (action) =>
    set((state) => ({
      actions: [...state.actions, action],
    })),
  setActions: (actions) => set({ actions }),
  setStatus: (status) =>
    set({
      status,
      isRecording: status === 'recording',
    }),
  resetSession: () =>
    set({
      currentSession: null,
      actions: [],
      isRecording: false,
      status: 'idle',
    }),
}));
