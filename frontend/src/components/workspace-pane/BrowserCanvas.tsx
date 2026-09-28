import React, { useRef, useState, useEffect, useCallback } from 'react';
import {
  MonitorPlay,
  Radio,
  ArrowLeft,
  ArrowRight,
  RotateCw,
  Search,
  Globe,
  Keyboard,
  MousePointer,
  Sparkles,
} from 'lucide-react';
import { useBrowserStream } from '../../hooks/useBrowserStream';
import { useSessionStore } from '../../store/sessionStore';
import { useSettingsStore } from '../../store/settingsStore';

export const BrowserCanvas: React.FC = () => {
  const { currentSession } = useSessionStore();
  const { settings } = useSettingsStore();

  const viewportWidth = settings?.viewport_width || 1440;
  const viewportHeight = settings?.viewport_height || 900;

  const {
    currentFrame,
    currentUrl,
    pageTitle,
    isConnected,
    sendMouseEvent,
    sendKeyboardEvent,
    sendNavigation,
    sendReload,
    sendGoBack,
    sendGoForward,
  } = useBrowserStream({
    sessionId: currentSession?.id,
  });

  const [addressBarUrl, setAddressBarUrl] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);

  // Sync address bar when session or navigation changes
  useEffect(() => {
    const url = currentUrl || currentSession?.active_url || currentSession?.target_url || '';
    if (url) {
      setAddressBarUrl(url);
    }
  }, [currentUrl, currentSession]);

  // Calculate exact Playwright viewport coordinates (handling object-contain letterboxing)
  const getCoordinates = useCallback(
    (e: React.MouseEvent<HTMLElement> | React.WheelEvent<HTMLElement>) => {
      const img = imgRef.current;
      if (!img) return null;

      const rect = img.getBoundingClientRect();
      const clickX = e.clientX - rect.left;
      const clickY = e.clientY - rect.top;

      // Image natural dimensions or viewport fallback
      const naturalW = img.naturalWidth || viewportWidth;
      const naturalH = img.naturalHeight || viewportHeight;

      // When using object-contain, calculate scale and offset
      const containerRatio = rect.width / rect.height;
      const imageRatio = naturalW / naturalH;

      let renderedWidth = rect.width;
      let renderedHeight = rect.height;
      let offsetX = 0;
      let offsetY = 0;

      if (containerRatio > imageRatio) {
        // Letterboxed on left/right
        renderedWidth = rect.height * imageRatio;
        offsetX = (rect.width - renderedWidth) / 2;
      } else {
        // Letterboxed on top/bottom
        renderedHeight = rect.width / imageRatio;
        offsetY = (rect.height - renderedHeight) / 2;
      }

      // Check if click is inside actual image
      const relativeX = clickX - offsetX;
      const relativeY = clickY - offsetY;

      if (relativeX < 0 || relativeX > renderedWidth || relativeY < 0 || relativeY > renderedHeight) {
        return null;
      }

      const scaleX = viewportWidth / renderedWidth;
      const scaleY = viewportHeight / renderedHeight;

      const x = Math.max(0, Math.min(viewportWidth, Math.round(relativeX * scaleX)));
      const y = Math.max(0, Math.min(viewportHeight, Math.round(relativeY * scaleY)));

      return { x, y };
    },
    [viewportWidth, viewportHeight]
  );

  const handleMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!currentSession) return;
    const coords = getCoordinates(e);
    if (!coords) return;
    const button = e.button === 2 ? 'right' : e.button === 1 ? 'middle' : 'left';
    sendMouseEvent('mousePressed', coords.x, coords.y, button);
    setIsFocused(true);
  };

  const handleMouseUp = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!currentSession) return;
    const coords = getCoordinates(e);
    if (!coords) return;
    const button = e.button === 2 ? 'right' : e.button === 1 ? 'middle' : 'left';
    sendMouseEvent('mouseReleased', coords.x, coords.y, button);
  };

  const handleDoubleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!currentSession) return;
    const coords = getCoordinates(e);
    if (!coords) return;
    sendMouseEvent('dblclick', coords.x, coords.y, 'left');
  };

  const handleWheel = (e: React.WheelEvent<HTMLDivElement>) => {
    if (!currentSession) return;
    e.preventDefault();
    const coords = getCoordinates(e) || { x: viewportWidth / 2, y: viewportHeight / 2 };
    sendMouseEvent('wheel', coords.x, coords.y, 'left', e.deltaX, e.deltaY);
  };

  const handleContextMenu = (e: React.MouseEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (!currentSession || !isFocused) return;

    // Do not intercept if user is typing in address bar input
    if ((e.target as HTMLElement).tagName === 'INPUT') return;

    // Prevent default browser actions (like scrolling or back navigation) when typing in canvas
    if (['Tab', 'Backspace', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' '].includes(e.key)) {
      e.preventDefault();
    }

    // Modifier keys (Shift, Control, Alt, Meta) use down/up tracking
    if (['Shift', 'Control', 'Alt', 'Meta'].includes(e.key)) {
      sendKeyboardEvent('keyDown', e.key);
      return;
    }

    // Single character typing, shortcuts, and special keys: send single 'press' event
    if (e.ctrlKey || e.metaKey) {
      const prefix = e.ctrlKey ? 'Control+' : 'Meta+';
      sendKeyboardEvent('press', `${prefix}${e.key}`);
    } else {
      sendKeyboardEvent('press', e.key);
    }
  };

  const handleKeyUp = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (!currentSession || !isFocused) return;
    if ((e.target as HTMLElement).tagName === 'INPUT') return;

    // Only send keyUp for modifier keys
    if (['Shift', 'Control', 'Alt', 'Meta'].includes(e.key)) {
      sendKeyboardEvent('keyUp', e.key);
    }
  };

  const handleAddressSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!addressBarUrl.trim()) return;
    sendNavigation(addressBarUrl.trim());
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-slate-950 border border-slate-800/80 rounded-xl overflow-hidden shadow-2xl relative">
      {/* Top Browser Toolbar */}
      <div className="h-10 bg-slate-900 border-b border-slate-800 px-3 flex items-center justify-between gap-2 select-none">
        {/* Window controls & Navigation buttons */}
        <div className="flex items-center space-x-1.5">
          <div className="flex items-center space-x-1 mr-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-red-500/80" />
            <div className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
          </div>

          <button
            type="button"
            onClick={sendGoBack}
            disabled={!currentSession || !isConnected}
            title="Back"
            className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800 disabled:opacity-40 transition"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
          </button>
          <button
            type="button"
            onClick={sendGoForward}
            disabled={!currentSession || !isConnected}
            title="Forward"
            className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800 disabled:opacity-40 transition"
          >
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
          <button
            type="button"
            onClick={sendReload}
            disabled={!currentSession || !isConnected}
            title="Reload Page"
            className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800 disabled:opacity-40 transition"
          >
            <RotateCw className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Interactive URL Address Bar */}
        <form onSubmit={handleAddressSubmit} className="flex-1 max-w-xl mx-2">
          <div className="relative flex items-center">
            <Globe className="w-3.5 h-3.5 absolute left-2.5 text-slate-500" />
            <input
              type="text"
              value={addressBarUrl}
              onChange={(e) => setAddressBarUrl(e.target.value)}
              disabled={!currentSession || !isConnected}
              placeholder="Enter URL to navigate (e.g. https://example.com)..."
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-8 pr-8 py-1 text-xs text-slate-200 font-mono focus:outline-none focus:border-blue-500 transition disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!currentSession || !isConnected}
              title="Navigate"
              className="absolute right-1.5 p-1 text-slate-400 hover:text-blue-400 disabled:opacity-30"
            >
              <Search className="w-3 h-3" />
            </button>
          </div>
        </form>

        {/* Live Status & Dimension Badges */}
        <div className="flex items-center space-x-2 text-[10px] font-medium shrink-0">
          <span className="hidden sm:inline-block font-mono text-slate-500 px-1.5 py-0.5 rounded bg-slate-950 border border-slate-800">
            {viewportWidth}×{viewportHeight}
          </span>
          {isConnected ? (
            <span className="flex items-center space-x-1 text-emerald-400 px-2 py-0.5 rounded-full bg-emerald-950/60 border border-emerald-800/80">
              <Radio className="w-3 h-3 animate-pulse" />
              <span>LIVE INTERACTION</span>
            </span>
          ) : (
            <span className="text-slate-500 px-2 py-0.5 rounded bg-slate-950 border border-slate-800">
              OFFLINE
            </span>
          )}
        </div>
      </div>

      {/* Interactive Browser Canvas Display */}
      <div
        ref={containerRef}
        tabIndex={0}
        onKeyDown={handleKeyDown}
        onKeyUp={handleKeyUp}
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onDoubleClick={handleDoubleClick}
        onWheel={handleWheel}
        onContextMenu={handleContextMenu}
        className={`flex-1 flex items-center justify-center bg-slate-950 overflow-hidden relative focus:outline-none ${
          isFocused ? 'ring-1 ring-blue-500/40' : ''
        }`}
      >
        {currentFrame ? (
          <div className="relative w-full h-full flex items-center justify-center">
            <img
              ref={imgRef}
              src={currentFrame}
              alt={pageTitle || 'Live Browser Canvas'}
              draggable={false}
              className="w-full h-full object-contain cursor-crosshair select-none"
            />

            {/* Bottom Interactive Hints Pill */}
            <div className="absolute bottom-3 left-1/2 -translate-x-1/2 bg-slate-900/90 backdrop-blur-md border border-slate-700/80 text-slate-300 text-[11px] px-3.5 py-1.5 rounded-full shadow-lg flex items-center space-x-2.5 pointer-events-none transition-opacity">
              <span className="flex items-center space-x-1 text-blue-400 font-semibold">
                <MousePointer className="w-3 h-3" />
                <span>Click / Scroll to interact</span>
              </span>
              <span className="text-slate-600">•</span>
              <span className="flex items-center space-x-1 text-emerald-400 font-semibold">
                <Keyboard className="w-3 h-3" />
                <span>Type to input text</span>
              </span>
              <span className="text-slate-600">•</span>
              <span className="text-slate-400">Actions recorded automatically</span>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center text-center p-8 space-y-4">
            <div className="w-14 h-14 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-500 shadow-inner">
              <MonitorPlay className="w-7 h-7 text-slate-400" />
            </div>
            <div className="space-y-1">
              <p className="text-sm font-bold text-slate-200">No Active Browser Stream</p>
              <p className="text-xs text-slate-400 max-w-sm">
                Enter a target URL and click <strong className="text-blue-400">"Launch & Record Session"</strong> in the left panel to begin.
              </p>
            </div>
            <div className="flex items-center space-x-2 text-[11px] text-slate-500 bg-slate-900/60 border border-slate-800/80 px-3 py-1.5 rounded-xl">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span>Full real-time browser canvas with click, type, and live CDP capture</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
