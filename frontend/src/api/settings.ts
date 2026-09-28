import { apiClient } from './client';
import {
  SettingsConfig,
  SettingsUpdatePayload,
  ModelStatusResponse,
  ModelTestRequest,
  ModelTestResponse,
} from '../types/settings';

export const settingsApi = {
  getSettings: async (): Promise<SettingsConfig> => {
    const { data } = await apiClient.get<SettingsConfig>('/settings/');
    return data;
  },

  updateSettings: async (payload: SettingsUpdatePayload): Promise<SettingsConfig> => {
    const { data } = await apiClient.put<SettingsConfig>('/settings/', payload);
    return data;
  },

  getModelStatus: async (): Promise<ModelStatusResponse> => {
    const { data } = await apiClient.get<ModelStatusResponse>('/settings/model-status');
    return data;
  },

  testModelConnection: async (payload: ModelTestRequest): Promise<ModelTestResponse> => {
    const { data } = await apiClient.post<ModelTestResponse>('/settings/test-model', payload);
    return data;
  },

  getAvailableModels: async (): Promise<{ success: boolean; models: string[]; error?: string }> => {
    const { data } = await apiClient.get<{ success: boolean; models: string[]; error?: string }>('/settings/models');
    return data;
  },
};
