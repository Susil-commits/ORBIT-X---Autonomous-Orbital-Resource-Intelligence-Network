import { useEffect, useRef } from 'react';
import { useSimulationStore } from './useSimulationStore';
import type { ConstellationTick } from '../types';

const WS_URL = 'ws://localhost:8000/ws/constellation';

export function useConstellationSocket() {
  const setTickData = useSimulationStore((s) => s.setTickData);
  const setIsConnected = useSimulationStore((s) => s.setIsConnected);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);

  useEffect(() => {
    let isMounted = true;

    function connect() {
      if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
        return;
      }

      try {
        const ws = new WebSocket(WS_URL);
        wsRef.current = ws;

        ws.onopen = () => {
          if (!isMounted) return;
          console.log('[ORBIT-X WS] Connected to constellation stream');
          setIsConnected(true);
        };

        ws.onmessage = (event) => {
          if (!isMounted) return;
          try {
            const data: ConstellationTick = JSON.parse(event.data);
            setTickData(data);
          } catch (err) {
            console.error('[ORBIT-X WS] Parse error', err);
          }
        };

        ws.onerror = (err) => {
          console.warn('[ORBIT-X WS] Connection error', err);
        };

        ws.onclose = () => {
          if (!isMounted) return;
          console.log('[ORBIT-X WS] Stream closed, reconnecting in 2s...');
          setIsConnected(false);
          reconnectTimeoutRef.current = window.setTimeout(() => {
            if (isMounted) connect();
          }, 2000);
        };
      } catch (e) {
        console.error('[ORBIT-X WS] Initialization error', e);
        reconnectTimeoutRef.current = window.setTimeout(() => {
          if (isMounted) connect();
        }, 2000);
      }
    }

    connect();

    return () => {
      isMounted = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [setTickData, setIsConnected]);
}
