import React from 'react';
import { Eye, Sparkles, LayoutPanelLeft, MessageSquare, SplitSquareVertical, Globe, RefreshCw } from 'lucide-react';
import { useUIStore } from '../../store/uiStore';
import { useSessionStore } from '../../store/sessionStore';
import { useDocumentStore } from '../../store/documentStore';

export const Header: React.FC = () => {
  const { viewMode, setViewMode, toggleControlPane, toggleChatPane } = useUIStore();
  const { currentSession, isRecording } = useSessionStore();
  const { currentDocument } = useDocumentStore();

  return (
    <header className="h-14 border-b border-slate-800 bg-slate-900/80 backdrop-blur-md px-4 flex items-center justify-between z-20">
      {/* Brand & Status */}
      <div className="flex items-center space-x-3">
        <button
          onClick={toggleControlPane}
          title="Toggle Control Pane"
          className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition"
        >
          <LayoutPanelLeft className="w-5 h-5" />
        </button>
        <div className="flex items-center space-x-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Eye className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold text-base tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            DocuAgent<span className="text-blue-500 font-extrabold ml-0.5">AI</span>
          </span>
          <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700/60 font-medium">
            v2.0
          </span>
        </div>

        {/* Live Active URL indicator */}
        {currentSession && (
          <div className="hidden lg:flex items-center space-x-2 text-xs bg-slate-950/60 border border-slate-800 rounded-md px-2.5 py-1 text-slate-300 max-w-sm truncate">
            <Globe className="w-3.5 h-3.5 text-blue-400 shrink-0" />
            <span className="truncate">{currentSession.active_url || currentSession.target_url}</span>
          </div>
        )}
      </div>

      {/* Center View Controls */}
      <div className="flex items-center bg-slate-950 border border-slate-800 p-0.5 rounded-lg">
        <button
          onClick={() => setViewMode('browser')}
          className={`px-3 py-1 text-xs font-medium rounded-md transition ${
            viewMode === 'browser'
              ? 'bg-blue-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          Live Browser
        </button>
        <button
          onClick={() => setViewMode('split')}
          className={`px-3 py-1 text-xs font-medium rounded-md transition ${
            viewMode === 'split'
              ? 'bg-blue-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          Split Canvas
        </button>
        <button
          onClick={() => setViewMode('preview')}
          className={`px-3 py-1 text-xs font-medium rounded-md transition ${
            viewMode === 'preview'
              ? 'bg-blue-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          Manual Preview
        </button>
      </div>

      {/* Right Quick Actions */}
      <div className="flex items-center space-x-2">
        {isRecording && (
          <div className="flex items-center space-x-1.5 px-2.5 py-1 bg-red-950/40 border border-red-800/50 rounded-full text-xs font-semibold text-red-400 animate-pulse">
            <div className="w-2 h-2 rounded-full bg-red-500" />
            <span>RECORDING</span>
          </div>
        )}

        {currentDocument?.quality_report && (
          <div className="hidden sm:flex items-center space-x-1 px-2 py-0.5 rounded-md bg-emerald-950/60 border border-emerald-800 text-emerald-400 text-xs font-medium">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Score: {currentDocument.quality_report.score}%</span>
          </div>
        )}

        <button
          onClick={toggleChatPane}
          title="Toggle Human-in-the-loop Chat"
          className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition"
        >
          <MessageSquare className="w-5 h-5" />
        </button>
      </div>
    </header>
  );
};
