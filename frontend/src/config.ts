/**
 * Central API configuration for ORBIT-X frontend.
 * Override at build time with VITE_API_URL and VITE_WS_URL env vars,
 * or via a `.env.local` file in the frontend directory.
 *
 * Examples:
 *   VITE_API_URL=https://api.orbitx.example.com
 *   VITE_WS_URL=wss://api.orbitx.example.com
 */
export const API_BASE: string =
  (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:8000';

export const WS_BASE: string =
  (import.meta.env.VITE_WS_URL as string | undefined) ?? 'ws://localhost:8000';
