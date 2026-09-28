import React, { useState } from 'react';
import { FileDown, FileText, Code2, Loader2, Check } from 'lucide-react';
import { useDocumentStore } from '../../store/documentStore';
import { documentsApi } from '../../api/documents';
import { ExportFormat } from '../../types/document';

export const ExportActionCard: React.FC = () => {
  const { currentDocument } = useDocumentStore();
  const [isExporting, setIsExporting] = useState(false);
  const [downloadedFormat, setDownloadedFormat] = useState<string | null>(null);

  const handleExport = async (format: ExportFormat) => {
    if (!currentDocument) return;
    setIsExporting(true);
    try {
      const data = await documentsApi.exportDocument(currentDocument.id, format, true);
      
      if (format === 'pdf' && data instanceof Blob) {
        const downloadUrl = window.URL.createObjectURL(data);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `${currentDocument.title.replace(/\\s+/g, '_')}.pdf`;
        document.body.appendChild(link);
        link.click();
        link.remove();
      }

      setDownloadedFormat(format);
      setTimeout(() => setDownloadedFormat(null), 3000);
    } catch (err) {
      console.error('Export failed:', err);
    } finally {
      setIsExporting(false);
    }
  };

  if (!currentDocument) return null;

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 shadow-sm space-y-3">
      <div className="flex items-center space-x-2">
        <FileDown className="w-4 h-4 text-emerald-400" />
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">Export & Publish</h3>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <button
          onClick={() => handleExport('pdf')}
          disabled={isExporting}
          className="flex items-center justify-center space-x-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700/80 text-white py-2 px-3 rounded-lg text-xs font-medium transition disabled:opacity-50"
        >
          {isExporting ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : downloadedFormat === 'pdf' ? (
            <Check className="w-3.5 h-3.5 text-emerald-400" />
          ) : (
            <FileText className="w-3.5 h-3.5 text-red-400" />
          )}
          <span>One-Click PDF</span>
        </button>

        <button
          onClick={() => handleExport('html')}
          disabled={isExporting}
          className="flex items-center justify-center space-x-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700/80 text-white py-2 px-3 rounded-lg text-xs font-medium transition disabled:opacity-50"
        >
          <Code2 className="w-3.5 h-3.5 text-blue-400" />
          <span>HTML Export</span>
        </button>
      </div>
    </div>
  );
};
