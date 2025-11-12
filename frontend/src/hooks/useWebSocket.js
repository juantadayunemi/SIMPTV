/**
 * useWebSocket Hook
 * Custom hook for WebSocket connection to live camera streams
 */
import { useState, useEffect, useRef, useCallback } from 'react';

const WS_BASE_URL = 'ws://localhost:8000';

export const useWebSocket = (cameraId, enabled = true) => {
  const [frame, setFrame] = useState(null);
  const [detections, setDetections] = useState([]);
  const [stats, setStats] = useState({
    frameCount: 0,
    detectionCount: 0,
    recordingId: null,
  });
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState(null);

  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  const MAX_RECONNECT_ATTEMPTS = 5;

  const connect = useCallback(() => {
    if (!cameraId || !enabled) return;

    try {
      const wsUrl = `${WS_BASE_URL}/ws/live-stream/${cameraId}/`;
      console.log(`Connecting to WebSocket: ${wsUrl}`);

      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log(`WebSocket connected to camera: ${cameraId}`);
        setConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          switch (data.type) {
            case 'connection':
              console.log(`${data.message}`);
              break;

            case 'stream_frame':
              // Update frame (base64 encoded JPEG)
              setFrame(data.frame);
              
              // Update detections
              setDetections(data.detections || []);
              
              // Update stats
              setStats({
                frameCount: data.frame_count || 0,
                detectionCount: data.detection_count || 0,
                recordingId: data.recording_id,
              });
              break;

            case 'error':
              console.error(`WebSocket error: ${data.message}`);
              setError(data.message);
              break;

            default:
              console.debug(`Received message type: ${data.type}`);
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        setError('WebSocket connection error');
        setConnected(false);
      };

      ws.onclose = (event) => {
        console.log(`WebSocket closed: ${event.code} - ${event.reason}`);
        setConnected(false);

        // Attempt reconnection if enabled and not manually closed
        if (enabled && reconnectAttemptsRef.current < MAX_RECONNECT_ATTEMPTS) {
          reconnectAttemptsRef.current += 1;
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 10000);
          
          console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current}/${MAX_RECONNECT_ATTEMPTS})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        } else if (reconnectAttemptsRef.current >= MAX_RECONNECT_ATTEMPTS) {
          setError('Failed to reconnect after maximum attempts');
        }
      };

      wsRef.current = ws;

    } catch (err) {
      console.error('Error creating WebSocket:', err);
      setError(err.message);
      setConnected(false);
    }
  }, [cameraId, enabled]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      console.log(`🔌 Manually disconnecting WebSocket for camera: ${cameraId}`);
      wsRef.current.close(1000, 'Client disconnect');
      wsRef.current = null;
    }

    setConnected(false);
    setFrame(null);
    setDetections([]);
    reconnectAttemptsRef.current = 0;
  }, [cameraId]);

  const sendMessage = useCallback((message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  }, []);

  // Auto-connect when enabled changes or component mounts
  useEffect(() => {
    if (enabled && cameraId) {
      connect();
    } else {
      disconnect();
    }

    // Cleanup on unmount
    return () => {
      disconnect();
    };
  }, [cameraId, enabled, connect, disconnect]);

  return {
    frame,
    detections,
    stats,
    connected,
    error,
    sendMessage,
    reconnect: connect,
    disconnect,
  };
};

export default useWebSocket;
