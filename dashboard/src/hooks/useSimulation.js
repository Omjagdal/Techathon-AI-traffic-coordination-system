import { useState, useEffect, useRef, useCallback } from 'react';

const WS_URL = 'ws://localhost:8000/ws';
const API_URL = 'http://localhost:8000';

export default function useSimulation() {
    const [state, setState] = useState(null);
    const [connected, setConnected] = useState(false);
    const wsRef = useRef(null);
    const reconnectTimer = useRef(null);

    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return;

        const ws = new WebSocket(WS_URL);
        wsRef.current = ws;

        ws.onopen = () => {
            setConnected(true);
            if (reconnectTimer.current) {
                clearTimeout(reconnectTimer.current);
                reconnectTimer.current = null;
            }
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                setState(data);
            } catch (e) {
                // ignore parse errors
            }
        };

        ws.onclose = () => {
            setConnected(false);
            wsRef.current = null;
            // Auto-reconnect after 2s
            reconnectTimer.current = setTimeout(connect, 2000);
        };

        ws.onerror = () => {
            ws.close();
        };
    }, []);

    useEffect(() => {
        connect();
        return () => {
            if (wsRef.current) wsRef.current.close();
            if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
        };
    }, [connect]);

    const spawnAmbulance = useCallback(async (direction) => {
        try {
            await fetch(`${API_URL}/api/spawn-ambulance`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ direction }),
            });
        } catch (e) {
            console.error('Failed to spawn ambulance:', e);
        }
    }, []);

    const resetSimulation = useCallback(async () => {
        try {
            await fetch(`${API_URL}/api/reset`, { method: 'POST' });
        } catch (e) {
            console.error('Failed to reset:', e);
        }
    }, []);

    return { state, connected, spawnAmbulance, resetSimulation };
}
