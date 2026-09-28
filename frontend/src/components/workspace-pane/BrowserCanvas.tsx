import React, { useRef, useEffect } from 'react';
import { useBrowserStream } from '../../hooks/useBrowserStream';
import { useSessionStore } from '../../store/sessionStore';
import { MonitorPlay, Radio } from 'lucide-react';

export const BrowserCanvas: React.FC = () => {
  const { currentSession } = useSessionStore();
  const { currentFrame, isConnected, sendMouseEvent } = useBrowserStream({
    sessionId: currentSession?.id,
  });

  const canvasContainerRef = useRef<HTMLDivElement>(null);

  const handleCanvasClick = (e: React.MouseEvent<HTMLImageElement>) => {
    if (!currentSession) return;
    const img = e.currentTarget;
    const rect = img.getBoundingClientRect();
    
    // Calculate normalized coordinates based on native resolution (1440x900)
    const scaleX = 1440 / rect.width;
    const scaleY = 900 / rect.height;

    const x = Math.round((e.clientX - rect.left) * scaleX);
    const y = Math.round((e.clientY - rect.top) * scaleY);

    sendMouseEvent('click', x, y);
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-slate-950 border border-slate-800/80 rounded-xl overflow-hidden shadow-2xl relative">
      {/* Top Browser Chrome Bar */}
      <div className="h-9 bg-slate-900 border-b border-slate-800 px-3 flex items-center justify-between">
        <div className="flex items-center space-x-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-red-500/80" />
          <div className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
        </div>

        <div className="flex-1 max-w-lg mx-4 bg-slate-950/80 border border-slate-800/80 rounded-md px-3 py-1 text-[11px] text-slate-400 font-mono truncate text-center">
          {currentSession?.active_url || currentSession?.target_url || 'about:blank'}
        </div>

        <div className="flex items-center space-x-1.5 text-[10px] font-medium">
          {isConnected ? (
            <span className="flex items-center space-x-1 text-emerald-400">
              <Radio className="w-3 h-3 animate-pulse" />
              <span>LIVE CDP</span>
            </span>
          ) : (
            <span className="text-slate-500">OFFLINE</span>
          )}
        </div>
      </div>

      {/* Screen Frame Display */}
      <div
        ref={canvasContainerRef}
        className="flex-1 flex items-center justify-center bg-slate-950 overflow-hidden relative"
      >
        {currentFrame ? (
          <img
            src={currentFrame}
            alt="Live Browser Screencast"
            onClick={handleCanvasClick}
            className="w-full h-full object-contain cursor-crosshair select-none"
          />
        ) : (
          <div className="flex flex-col items-center justify-center text-center p-8 space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-500">
              <MonitorPlay className="w-6 h-6" />
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-300">No Active Browser Stream</p>
              <p className="text-[11px] text-slate-500 max-w-xs mt-0.5">
                Launch a session from the left control panel to begin recording browser interactions.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
