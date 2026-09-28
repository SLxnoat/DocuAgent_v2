export type CalloutType = 'note' | 'tip' | 'warning' | 'important';

export interface Callout {
  type: CalloutType;
  content: string;
}

export interface DocumentationStep {
  step_number: number;
  title: string;
  instruction: string;
  detailed_description?: string;
  target_ui_element?: string;
  action_type?: string;
  input_value_used?: string;
  screenshot_url?: string;
  screenshot_path?: string;
  highlight_selector?: string;
  callouts: Callout[];
  raw_action_ids: string[];
}

export interface QualityReport {
  score: number;
  is_approved: boolean;
  completeness_score: number;
  clarity_score: number;
  structure_score: number;
  strengths: string[];
  suggestions: string[];
  missing_items: string[];
}

export interface DocumentSchema {
  id: string;
  session_id: string;
  title: string;
  executive_summary: string;
  prerequisites: string[];
  steps: DocumentationStep[];
  troubleshooting: Array<{ problem: string; solution: string }>;
  raw_markdown: string;
  quality_report?: QualityReport | null;
  created_at: string;
  updated_at: string;
  version: number;
}

export type ExportFormat = 'pdf' | 'html' | 'markdown' | 'json';
