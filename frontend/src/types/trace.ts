export type ActionType = 'click' | 'dblclick' | 'input' | 'change' | 'select' | 'submit' | 'keypress' | 'navigation' | 'scroll' | 'hover';

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
  top?: number;
  left?: number;
  bottom?: number;
  right?: number;
}

export interface DOMElementInfo {
  tag_name: string;
  element_id?: string | null;
  class_names: string[];
  css_selector: string;
  xpath?: string | null;
  inner_text?: string | null;
  placeholder?: string | null;
  aria_label?: string | null;
  role?: string | null;
  input_type?: string | null;
  bounding_box?: BoundingBox | null;
  attributes?: Record<string, string>;
}

export interface ActionTrace {
  id: string;
  session_id: string;
  sequence_number: number;
  action_type: ActionType;
  timestamp: string;
  page_url: string;
  page_title: string;
  target_element?: DOMElementInfo | null;
  input_value?: string | null;
  key?: string | null;
  screenshot_path?: string | null;
  screenshot_url?: string | null;
  metadata?: Record<string, any>;
}
