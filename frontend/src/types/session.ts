export type SessionStatus = 'idle' | 'starting' | 'recording' | 'paused' | 'processing' | 'completed' | 'failed';

export interface AuthCredentials {
  username?: string;
  password?: string;
  auth_type: string;
  login_url?: string;
}

export interface SessionCreatePayload {
  target_url: string;
  title?: string;
  description?: string;
  credentials?: AuthCredentials;
  viewport_width?: number;
  viewport_height?: number;
  highlight_color?: string;
}

export interface SessionResponse {
  id: string;
  target_url: string;
  title: string;
  description?: string;
  status: SessionStatus;
  action_count: number;
  created_at: string;
  updated_at: string;
  active_url?: string;
  metadata: Record<string, any>;
}
