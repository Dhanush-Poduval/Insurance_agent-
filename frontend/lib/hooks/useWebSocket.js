'use client';
import { useEffect, useCallback, useRef } from 'react';
import { wsClient } from '@/lib/api/webSocketClient';

export function useWebSocket(path = '', options = {}) {
  const { autoConnect = true, onMessage, onConnect, onDisconnect, onError } = options;
  const unsubscribers = useRef([]);

  useEffect(() => {
    if (!autoConnect) return;
    wsClient.connect(path);

    if (onConnect) unsubscribers.current.push(wsClient.subscribe('connect', onConnect));
    if (onDisconnect) unsubscribers.current.push(wsClient.subscribe('disconnect', onDisconnect));
    if (onMessage) unsubscribers.current.push(wsClient.subscribe('message', onMessage));
    if (onError) unsubscribers.current.push(wsClient.subscribe('error', onError));

    return () => {
      unsubscribers.current.forEach((unsub) => unsub());
      unsubscribers.current = [];
    };
  }, [path, autoConnect, onConnect, onDisconnect, onMessage, onError]);

  const subscribe = useCallback((event, callback) => {
    const unsub = wsClient.subscribe(event, callback);
    unsubscribers.current.push(unsub);
    return unsub;
  }, []);

  const send = useCallback((data) => wsClient.send(data), []);
  const disconnect = useCallback(() => wsClient.disconnect(), []);

  return { subscribe, send, disconnect, connected: wsClient.connected };
}
