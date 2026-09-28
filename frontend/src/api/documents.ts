import { apiClient } from './client';
import { DocumentSchema, ExportFormat } from '../types/document';
import { ChatRefineRequest, ChatRefineResponse } from '../types/chat';

export const documentsApi = {
  generateDocument: async (sessionId: string): Promise<DocumentSchema> => {
    const { data } = await apiClient.post<DocumentSchema>(`/documents/generate/${sessionId}`);
    return data;
  },

  getDocument: async (documentId: string): Promise<DocumentSchema> => {
    const { data } = await apiClient.get<DocumentSchema>(`/documents/${documentId}`);
    return data;
  },

  refineDocument: async (payload: ChatRefineRequest): Promise<ChatRefineResponse> => {
    const { data } = await apiClient.post<ChatRefineResponse>('/chat/refine', payload);
    return data;
  },

  exportDocument: async (
    documentId: string,
    format: ExportFormat = 'pdf',
    includeScreenshots: boolean = true
  ): Promise<Blob> => {
    const response = await apiClient.post(
      '/documents/export',
      {
        document_id: documentId,
        format,
        include_screenshots: includeScreenshots,
      },
      {
        responseType: format === 'pdf' ? 'blob' : 'json',
      }
    );
    return response.data;
  },
};
