const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';

export class WebSocketClient {
  constructor() {
    this.ws = null;
    this.subscribers = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 2000;
    this.connected = false;
  }

  connect(path = '') {
    if (typeof window === 'undefined') return;
    try {
      this.ws = new WebSocket(`${WS_URL}${path}`);
      this.ws.onopen = () => {
        this.connected = true;
        this.reconnectAttempts = 0;
        this._notify('connect', null);
      };
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this._notify(data.type, data.payload);
          this._notify('message', data);
        } catch {
          this._notify('message', event.data);
        }
      };
      this.ws.onclose = () => {
        this.connected = false;
        this._notify('disconnect', null);
        this._reconnect(path);
      };
      this.ws.onerror = (err) => {
        this._notify('error', err);
      };
    } catch {
      this._reconnect(path);
    }
  }

  disconnect() {
    this.maxReconnectAttempts = 0;
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.connected = false;
  }

  subscribe(event, callback) {
    if (!this.subscribers.has(event)) {
      this.subscribers.set(event, new Set());
    }
    this.subscribers.get(event).add(callback);
    return () => this.subscribers.get(event)?.delete(callback);
  }

  send(data) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  _notify(event, data) {
    this.subscribers.get(event)?.forEach((cb) => cb(data));
  }

  _reconnect(path) {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) return;
    this.reconnectAttempts++;
    setTimeout(() => this.connect(path), this.reconnectDelay * this.reconnectAttempts);
  }
}

export const wsClient = new WebSocketClient();
