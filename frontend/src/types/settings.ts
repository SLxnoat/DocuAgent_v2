export type LLMProvider = 'ollama_cloud' | 'ollama_local' | 'openai' | 'litellm' | 'anthropic';

export type ModelPulseStatus = 'online' | 'degraded' | 'offline' | 'checking';

export interface SettingsConfig {
  llm_provider: LLMProvider;
  ollama_base_url: string;
  ollama_api_key_masked?: string | null;
  default_model: string;
  fast_model: string;
  openai_api_key_masked?: string | null;

  highlight_color: string;
  highlight_outline_width: string;
  viewport_width: number;
  viewport_height: number;
  screencast_fps: number;
  screencast_quality: number;

  default_export_format: string;
  environment: string;
  backend_port: number;
}

export interface SettingsUpdatePayload {
  llm_provider?: LLMProvider;
  ollama_base_url?: string;
  ollama_api_key?: string;
  default_model?: string;
  fast_model?: string;
  openai_api_key?: string;

  highlight_color?: string;
  highlight_outline_width?: string;
  viewport_width?: number;
  viewport_height?: number;
  screencast_fps?: number;
  screencast_quality?: number;
}

export interface ModelStatusResponse {
  status: ModelPulseStatus;
  provider: string;
  model_name: string;
  latency_ms?: number | null;
  last_ping: string;
  message: string;
  capabilities: string[];
}

export interface ModelTestRequest {
  provider?: string;
  base_url?: string;
  api_key?: string;
  model_name?: string;
}

export interface ModelTestResponse {
  success: boolean;
  latency_ms: number;
  provider: string;
  model_name: string;
  sample_response?: string | null;
  error_message?: string | null;
}
