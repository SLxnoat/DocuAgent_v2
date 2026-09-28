import { useEffect, useRef } from 'react';
import { useSessionStore } from '../store/sessionStore';
import { ActionTrace } from '../types/trace';

interface UseSessionEventsProps {
  sessionId?: string | null;
}

export const useSessionEvents = ({ sessionId }: UseSessionEventsProps) => {
  const addAction = useSessionStore((state) => state.addAction);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!sessionId) {
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
      return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/events/${sessionId}`;
    const ws = new WebSocket(wsUrl);
    socketRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === 'action_recorded' && payload.data) {
          addAction(payload.data as ActionTrace);
        }
      } catch (err) {
        console.error('Error handling session event:', err);
      }
    };

    return () => {
      ws.close();
    };
  }, [sessionId, addAction]);
};
