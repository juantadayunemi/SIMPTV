/**
 * WebSocket Service para actualizaciones en tiempo real
 * Maneja conexiones WebSocket para análisis de tráfico
 */

export type WebSocketMessageType = 
  | 'progress_update'
  | 'vehicle_detected'
  | 'processing_complete'
  | 'processing_error'
  | 'log_message'
  | 'frame_processed';

export interface WebSocketMessage {
  type: WebSocketMessageType;
  data: any;
}

export interface ProgressUpdate {
  processed_frames: number;
  total_frames: number;
  vehicles_detected: number;
  percentage: number;
  status: string;
}

export interface VehicleDetected {
  track_id: string;
  vehicle_type: string;
  confidence: number;
  frame_number: number;
}

export interface ProcessingComplete {
  analysis_id: number;
  total_vehicles: number;
  processing_time: number;
  stats: Record<string, any>;
}

export interface LogMessage {
  level: 'info' | 'warning' | 'error';
  message: string;
  timestamp: string;
}

type MessageHandler = (data: any) => void;

export class TrafficWebSocketService {
  private ws: WebSocket | null = null;
  private handlers: Map<WebSocketMessageType, Set<MessageHandler>> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000;
  private analysisId: number | null = null;

  /**
   * Conectar al WebSocket de análisis de tráfico
   */
  connect(analysisId: number): Promise<void> {
    return new Promise((resolve, reject) => {
      this.analysisId = analysisId;
      
      // Construir URL del WebSocket
      const wsUrl = `${import.meta.env.VITE_WS_URL}/ws/traffic/analysis/${analysisId}/`;

      console.log(`🔌 Conectando a WebSocket: ${wsUrl}`);

      try {
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log('✅ WebSocket conectado');
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('❌ Error parseando mensaje WebSocket:', error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('❌ Error en WebSocket:', error);
          reject(error);
        };

        this.ws.onclose = (event) => {
          console.log(`🔌 WebSocket cerrado (code: ${event.code})`);
          
          // Intentar reconectar si no fue cierre intencional
          if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnect();
          }
        };
      } catch (error) {
        console.error('❌ Error creando WebSocket:', error);
        reject(error);
      }
    });
  }

  /**
   * Reconectar WebSocket automáticamente
   */
  private reconnect(): void {
    this.reconnectAttempts++;
    
    console.log(
      `🔄 Intentando reconectar (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`
    );

    setTimeout(() => {
      if (this.analysisId) {
        this.connect(this.analysisId).catch((error) => {
          console.error('❌ Error en reconexión:', error);
        });
      }
    }, this.reconnectDelay * this.reconnectAttempts);
  }

  /**
   * Manejar mensaje recibido del WebSocket
   */
  private handleMessage(message: WebSocketMessage): void {
    console.log(`📨 Mensaje recibido VVVVVVVVVV `, message)
    console.log(`📨 Mensaje recibido [${message.type}]:`, message.data);

    const handlers = this.handlers.get(message.type);
    if (handlers) {
      handlers.forEach((handler) => handler(message.data));
    }
  }

  /**
   * Suscribirse a un tipo de mensaje
   */
  on(messageType: WebSocketMessageType, handler: MessageHandler): () => void {
    if (!this.handlers.has(messageType)) {
      this.handlers.set(messageType, new Set());
    }

    this.handlers.get(messageType)!.add(handler);

    // Retornar función para desuscribirse
    return () => {
      this.handlers.get(messageType)?.delete(handler);
    };
  }

  /**
   * Enviar mensaje al servidor
   */
  send(message: WebSocketMessage): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('⚠️ WebSocket no conectado, no se puede enviar mensaje');
    }
  }

  /**
   * Desconectar WebSocket
   */
  disconnect(): void {
    if (this.ws) {
      console.log('🔌 Cerrando WebSocket...');
      this.ws.close(1000, 'Cierre intencional');
      this.ws = null;
    }
    
    this.handlers.clear();
    this.analysisId = null;
    this.reconnectAttempts = 0;
  }

  /**
   * Verificar si está conectado
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// Instancia singleton
let wsInstance: TrafficWebSocketService | null = null;

export const getWebSocketService = (): TrafficWebSocketService => {
  if (!wsInstance) {
    wsInstance = new TrafficWebSocketService();
  }
  return wsInstance;
};
