import { create } from 'zustand';
import { SettingsConfig, SettingsUpdatePayload, ModelStatusResponse, ModelPulseStatus } from '../types/settings';
import { settingsApi } from '../api/settings';

interface SettingsState {
  settings: SettingsConfig | null;
  modelStatus: ModelStatusResponse | null;
  isLoading: boolean;
  isSettingsModalOpen: boolean;
  isTestingConnection: boolean;
  
  openSettingsModal: () => void;
  closeSettingsModal: () => void;
  fetchSettings: () => Promise<void>;
  updateSettings: (payload: SettingsUpdatePayload) => Promise<void>;
  checkModelPulse: () => Promise<void>;
}

export const useSettingsStore = create<SettingsState>((set, get) => ({
  settings: null,
  modelStatus: null,
  isLoading: false,
  isSettingsModalOpen: false,
  isTestingConnection: false,

  openSettingsModal: () => set({ isSettingsModalOpen: true }),
  closeSettingsModal: () => set({ isSettingsModalOpen: false }),

  fetchSettings: async () => {
    try {
      set({ isLoading: true });
      const data = await settingsApi.getSettings();
      set({ settings: data, isLoading: false });
    } catch (err) {
      console.error('Failed to fetch settings:', err);
      set({ isLoading: false });
    }
  },

  updateSettings: async (payload) => {
    try {
      set({ isLoading: true });
      const updated = await settingsApi.updateSettings(payload);
      set({ settings: updated, isLoading: false });
      // Immediately refresh model pulse after settings change
      get().checkModelPulse();
    } catch (err) {
      console.error('Failed to update settings:', err);
      set({ isLoading: false });
      throw err;
    }
  },

  checkModelPulse: async () => {
    try {
      const status = await settingsApi.getModelStatus();
      set({ modelStatus: status });
    } catch (err) {
      console.error('Model pulse check failed:', err);
      set({
        modelStatus: {
          status: 'offline',
          provider: get().settings?.llm_provider || 'ollama_cloud',
          model_name: get().settings?.default_model || 'llama3.3:70b',
          last_ping: new Date().toISOString(),
          message: 'Connection check unreachable',
          capabilities: [],
        },
      });
    }
  },
}));
