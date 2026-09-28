import React from 'react';
import { Play, Square, Sparkles, Loader2, RefreshCw } from 'lucide-react';
import { useSessionStore } from '../../store/sessionStore';
import { useDocumentStore } from '../../store/documentStore';
import { sessionsApi } from '../../api/sessions';
import { documentsApi } from '../../api/documents';

interface RecordingControlsProps {
  url: string;
  title: string;
  onStartSession: () => void;
  isLoading: boolean;
}

export const RecordingControls: React.FC<RecordingControlsProps> = ({
  url,
  title,
  onStartSession,
  isLoading,
}) => {
  const { currentSession, isRecording, actions, setCurrentSession, setStatus } = useSessionStore();
  const { isGenerating, setIsGenerating, setCurrentDocument } = useDocumentStore();

  const handleStopRecording = async () => {
    if (!currentSession) return;
    try {
      const stopped = await sessionsApi.stopSession(currentSession.id);
      setCurrentSession(stopped);
    } catch (err) {
      console.error('Failed to stop recording:', err);
    }
  };

  const handleGenerateManual = async () => {
    if (!currentSession) return;
    setIsGenerating(true);
    try {
      const doc = await documentsApi.generateDocument(currentSession.id);
      setCurrentDocument(doc);
    } catch (err) {
      console.error('Failed to generate documentation:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 shadow-sm space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">Session Controls</h3>
        <span className="text-[11px] font-semibold text-slate-400">
          Actions: <span className="text-blue-400">{actions.length}</span>
        </span>
      </div>

      {!currentSession ? (
        <button
          onClick={onStartSession}
          disabled={!url || isLoading}
          className="w-full flex items-center justify-center space-x-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-medium py-2 px-4 rounded-lg text-xs transition shadow-lg shadow-blue-600/20 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <>
              <Play className="w-4 h-4 fill-current" />
              <span>Launch & Record Session</span>
            </>
          )}
        </button>
      ) : isRecording ? (
        <div className="space-y-2">
          <button
            onClick={handleStopRecording}
            className="w-full flex items-center justify-center space-x-2 bg-red-600 hover:bg-red-500 text-white font-medium py-2 px-4 rounded-lg text-xs transition shadow-lg shadow-red-600/20"
          >
            <Square className="w-4 h-4 fill-current" />
            <span>Stop & Finalize Recording</span>
          </button>
          <p className="text-[10px] text-slate-500 text-center">
            Click elements on the browser canvas to record steps.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          <button
            onClick={handleGenerateManual}
            disabled={isGenerating}
            className="w-full flex items-center justify-center space-x-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold py-2.5 px-4 rounded-lg text-xs transition shadow-lg shadow-emerald-600/20 disabled:opacity-50"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Multi-Agent Synthesizing...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Generate Manual (LangGraph)</span>
              </>
            )}
          </button>

          <button
            onClick={onStartSession}
            disabled={isGenerating}
            className="w-full flex items-center justify-center space-x-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 py-1.5 px-3 rounded-lg text-xs transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Record New Workflow</span>
          </button>
        </div>
      )}
    </div>
  );
};
