import { DocumentationStep } from './document';

export type MessageRole = 'user' | 'assistant' | 'system';

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
  step_number?: number;
  applied_changes?: Record<string, any>;
}

export interface ChatRefineRequest {
  document_id: string;
  prompt: string;
  target_step_number?: number;
  history: ChatMessage[];
}

export interface ChatRefineResponse {
  document_id: string;
  reply_message: string;
  updated_steps: DocumentationStep[];
  updated_markdown: string;
  modified_step_numbers: number[];
}
