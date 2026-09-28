import React from 'react';
import { BrowserCanvas } from './BrowserCanvas';
import { MarkdownPreview } from './MarkdownPreview';
import { ActionTraceFeed } from './ActionTraceFeed';
import { useUIStore } from '../../store/uiStore';
import { useSessionStore } from '../../store/sessionStore';
import { useSessionEvents } from '../../hooks/useSessionEvents';

export const WorkspacePane: React.FC = () => {
  const { viewMode } = useUIStore();
  const { currentSession } = useSessionStore();

  // Connect live event stream
  useSessionEvents({ sessionId: currentSession?.id });

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden p-3 space-y-3">
      <div className="flex-1 flex overflow-hidden space-x-3">
        {/* Browser Canvas Pane */}
        {(viewMode === 'browser' || viewMode === 'split') && (
          <div className={`${viewMode === 'split' ? 'w-1/2' : 'w-full'} flex flex-col h-full overflow-hidden`}>
            <BrowserCanvas />
          </div>
        )}

        {/* Live Markdown Preview Pane */}
        {(viewMode === 'preview' || viewMode === 'split') && (
          <div className={`${viewMode === 'split' ? 'w-1/2' : 'w-full'} flex flex-col h-full overflow-hidden`}>
            <MarkdownPreview />
          </div>
        )}
      </div>

      {/* Real-time Action Trace Feed Bar */}
      <ActionTraceFeed />
    </div>
  );
};
