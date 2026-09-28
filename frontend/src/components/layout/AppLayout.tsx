import React from 'react';
import { Header } from './Header';
import { ControlPane } from '../control-pane/ControlPane';
import { WorkspacePane } from '../workspace-pane/WorkspacePane';
import { ChatPane } from '../chat-pane/ChatPane';
import { useUIStore } from '../../store/uiStore';

export const AppLayout: React.FC = () => {
  const { isControlPaneCollapsed, isChatPaneCollapsed } = useUIStore();

  return (
    <div className="flex flex-col h-screen w-screen bg-slate-950 text-slate-100 overflow-hidden">
      <Header />
      <div className="flex-1 flex overflow-hidden">
        {/* Left Control Pane */}
        {!isControlPaneCollapsed && (
          <aside className="w-80 border-r border-slate-800 bg-slate-900/50 flex flex-col shrink-0 overflow-y-auto">
            <ControlPane />
          </aside>
        )}

        {/* Center Workspace Pane */}
        <main className="flex-1 flex flex-col min-w-0 bg-slate-950 overflow-hidden relative">
          <WorkspacePane />
        </main>

        {/* Right HITL Chat Pane */}
        {!isChatPaneCollapsed && (
          <aside className="w-88 lg:w-96 border-l border-slate-800 bg-slate-900/50 flex flex-col shrink-0 overflow-hidden">
            <ChatPane />
          </aside>
        )}
      </div>
    </div>
  );
};
