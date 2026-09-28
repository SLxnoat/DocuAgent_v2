import { useEffect, useRef, useState, useCallback } from 'react';

interface UseBrowserStreamProps {
  sessionId?: string | null;
}

export const useBrowserStream = ({ sessionId }: UseBrowserStreamProps) => {
  const [currentFrame, setCurrentFrame] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!sessionId) {
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
      setCurrentFrame(null);
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
    (event: 'click' | 'mousePressed' | 'mouseReleased' | 'mouseMoved', x: number, y: number, button = 'left') => {
      if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        socketRef.current.send(
          JSON.stringify({
            type: 'mouse',
            event,
            x,
            y,
            button,
            clickCount: 1,
          })
        );
      }
    },
    []
  );

  const sendKeyboardEvent = useCallback((event: 'keyDown' | 'keyUp' | 'type', key: string, text?: string) => {
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
  }, []);

  return {
    currentFrame,
    isConnected,
    sendMouseEvent,
    sendKeyboardEvent,
  };
};
