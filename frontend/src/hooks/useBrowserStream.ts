import { useEffect, useRef, useState, useCallback } from 'react';

interface UseBrowserStreamProps {
  sessionId?: string | null;
}

export const useBrowserStream = ({ sessionId }: UseBrowserStreamProps) => {
  const [currentFrame, setCurrentFrame] = useState<string | null>(null);
  const [currentUrl, setCurrentUrl] = useState<string>('');
  const [pageTitle, setPageTitle] = useState<string>('');
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!sessionId) {
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
      setCurrentFrame(null);
      setCurrentUrl('');
      setPageTitle('');
      setIsConnected(false);
      return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/screencast/${sessionId}`;
    const ws = new WebSocket(wsUrl);
    socketRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === 'screencast_frame' && payload.data) {
          setCurrentFrame(`data:image/jpeg;base64,${payload.data}`);
          if (payload.metadata?.url) {
            setCurrentUrl(payload.metadata.url);
          }
          if (payload.metadata?.title) {
            setPageTitle(payload.metadata.title);
          }
        }
      } catch (err) {
        console.error('Failed to parse screencast packet:', err);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, [sessionId]);

  const sendMouseEvent = useCallback(
    (
      event: 'click' | 'dblclick' | 'mousePressed' | 'mouseReleased' | 'mouseMoved' | 'wheel',
      x: number,
      y: number,
      button = 'left',
      deltaX = 0,
      deltaY = 0
    ) => {
      if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        socketRef.current.send(
          JSON.stringify({
            type: 'mouse',
            event,
            x,
            y,
            button,
            clickCount: event === 'dblclick' ? 2 : 1,
            deltaX,
            deltaY,
          })
        );
      }
    },
    []
  );

  const sendKeyboardEvent = useCallback(
    (event: 'keyDown' | 'keyUp' | 'type' | 'press', key: string, text?: string) => {
      if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        socketRef.current.send(
          JSON.stringify({
            type: 'keyboard',
            event,
            key,
            text,
          })
        );
      }
    },
    []
  );

  const sendNavigation = useCallback((url: string) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(
        JSON.stringify({
          type: 'navigate',
          url,
        })
      );
    }
  }, []);

  const sendReload = useCallback(() => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ type: 'reload' }));
    }
  }, []);

  const sendGoBack = useCallback(() => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ type: 'goBack' }));
    }
  }, []);

  const sendGoForward = useCallback(() => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ type: 'goForward' }));
    }
  }, []);

  return {
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
  };
};

