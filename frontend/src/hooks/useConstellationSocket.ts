import { useEffect, useRef } from 'react';
import { useSimulationStore } from './useSimulationStore';
import { WS_BASE } from '../config';
import type { ConstellationTick } from '../types';

const WS_URL = `${WS_BASE}/ws/constellation`;
const MAX_RECONNECT_DELAY_MS = 30_000;

export function useConstellationSocket() {
  const setTickData = useSimulationStore((s) => s.setTickData);
  const setIsConnected = useSimulationStore((s) => s.setIsConnected);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const retryCountRef = useRef<number>(0);

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
          retryCountRef.current = 0; // reset backoff on successful connect
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
          const delay = Math.min(MAX_RECONNECT_DELAY_MS, 1000 * Math.pow(2, retryCountRef.current));
          retryCountRef.current += 1;
          console.log(`[ORBIT-X WS] Stream closed, reconnecting in ${delay}ms (attempt ${retryCountRef.current})...`);
          setIsConnected(false);
          reconnectTimeoutRef.current = window.setTimeout(() => {
            if (isMounted) connect();
          }, delay);
        };
      } catch (e) {
        console.error('[ORBIT-X WS] Initialization error', e);
        const delay = Math.min(MAX_RECONNECT_DELAY_MS, 1000 * Math.pow(2, retryCountRef.current));
        retryCountRef.current += 1;
        reconnectTimeoutRef.current = window.setTimeout(() => {
          if (isMounted) connect();
        }, delay);
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
