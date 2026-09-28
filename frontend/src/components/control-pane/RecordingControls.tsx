import React, { useState } from 'react';
import { Play, Square, Sparkles, Loader2, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';
import { useSessionStore } from '../../store/sessionStore';
import { useDocumentStore } from '../../store/documentStore';
import { useUIStore } from '../../store/uiStore';
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
  const { isGenerating, setIsGenerating, setCurrentDocument, currentDocument } = useDocumentStore();
  const { setViewMode } = useUIStore();
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const runSynthesisPipeline = async (sessionId: string) => {
    setIsGenerating(true);
    setErrorMsg(null);
    // Switch to split view so user sees live manual synthesis alongside browser traces
    setViewMode('split');

    try {
      const doc = await documentsApi.generateDocument(sessionId);
      setCurrentDocument(doc);
    } catch (err: any) {
      console.error('Failed to generate documentation:', err);
      setErrorMsg(err?.response?.data?.detail || err.message || 'Failed to synthesize document.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleStopRecording = async () => {
    if (!currentSession) return;
    setErrorMsg(null);
    try {
      const stopped = await sessionsApi.stopSession(currentSession.id);
      setCurrentSession(stopped);
      // Auto-trigger LangGraph multi-agent pipeline immediately on stop
      await runSynthesisPipeline(stopped.id);
    } catch (err: any) {
      console.error('Failed to stop recording:', err);
      setErrorMsg('Failed to finalize session.');
    }
  };

  const handleManualTrigger = async () => {
    if (!currentSession) return;
    await runSynthesisPipeline(currentSession.id);
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 shadow-sm space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">Session Controls</h3>
        <span className="text-[11px] font-semibold text-slate-400">
          Actions: <span className="text-blue-400 font-mono">{actions.length}</span>
        </span>
      </div>

      {!currentSession ? (
        <button
          onClick={onStartSession}
          disabled={!url || isLoading}
          className="w-full flex items-center justify-center space-x-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-medium py-2.5 px-4 rounded-xl text-xs transition shadow-lg shadow-blue-600/20 disabled:opacity-50 disabled:cursor-not-allowed"
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
        <div className="space-y-2.5">
          <button
            onClick={handleStopRecording}
            className="w-full flex items-center justify-center space-x-2 bg-red-600 hover:bg-red-500 text-white font-semibold py-2.5 px-4 rounded-xl text-xs transition shadow-lg shadow-red-600/20"
          >
            <Square className="w-4 h-4 fill-current" />
            <span>Stop & Run Pipeline</span>
          </button>
          <p className="text-[10px] text-slate-400 text-center flex items-center justify-center space-x-1">
            <span>🔴 Recording active · Click canvas to capture steps</span>
          </p>
        </div>
      ) : (
        <div className="space-y-2.5">
          {/* Synthesizing / Regenerate Button */}
          <button
            onClick={handleManualTrigger}
            disabled={isGenerating}
            className="w-full flex items-center justify-center space-x-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold py-2.5 px-4 rounded-xl text-xs transition shadow-lg shadow-emerald-600/20 disabled:opacity-50"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-white" />
                <span>Multi-Agent Synthesizing...</span>
              </>
            ) : currentDocument ? (
              <>
                <RefreshCw className="w-4 h-4" />
                <span>Re-Synthesize Manual</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Synthesize Manual (LangGraph)</span>
              </>
            )}
          </button>

          {isGenerating && (
            <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1.5 animate-pulse">
              <div className="flex items-center space-x-2 text-[11px] text-emerald-400 font-semibold">
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Multi-Agent Engine Executing...</span>
              </div>
              <p className="text-[10px] text-slate-400">
                Supervisor routing between Intent Parser, Technical Writer & Quality Reviewer.
              </p>
            </div>
          )}

          {errorMsg && (
            <div className="p-2 rounded-lg bg-rose-950/40 border border-rose-800 text-rose-300 text-[11px] flex items-start space-x-1.5">
              <AlertCircle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
              <span>{errorMsg}</span>
            </div>
          )}

          <button
            onClick={onStartSession}
            disabled={isGenerating}
            className="w-full flex items-center justify-center space-x-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 py-2 px-3 rounded-xl text-xs transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Record New Workflow</span>
          </button>
        </div>
      )}
    </div>
  );
};
