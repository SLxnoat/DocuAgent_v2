import { apiClient } from './client';
import { SessionCreatePayload, SessionResponse } from '../types/session';
import { ActionTrace } from '../types/trace';

export const sessionsApi = {
  createSession: async (payload: SessionCreatePayload): Promise<SessionResponse> => {
    const { data } = await apiClient.post<SessionResponse>('/sessions/', payload);
    return data;
  },

  getSession: async (sessionId: string): Promise<SessionResponse> => {
    const { data } = await apiClient.get<SessionResponse>(`/sessions/${sessionId}`);
    return data;
  },

  getSessionActions: async (sessionId: string): Promise<ActionTrace[]> => {
    const { data } = await apiClient.get<ActionTrace[]>(`/sessions/${sessionId}/actions`);
    return data;
  },

  stopSession: async (sessionId: string): Promise<SessionResponse> => {
    const { data } = await apiClient.post<SessionResponse>(`/sessions/${sessionId}/stop`);
    return data;
  },
};
