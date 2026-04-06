import { ref, readonly } from 'vue'
import type { ServerStatus } from './types'

type MessageHandler = (data: ServerStatus) => void

class WebSocketService {
  private ws: WebSocket | null = null
  private url: string
  private reconnectInterval = 5000
  private reconnectTimer: number | null = null
  private handlers: Set<MessageHandler> = new Set()
  private subscribedServers: string[] = []

  public connected = ref(false)
  public readonly isConnected = readonly(this.connected)

  constructor(url?: string) {
    const wsUrl = url || import.meta.env.VITE_WS_URL || `ws://${window.location.host}/ws/status`
    this.url = wsUrl
  }

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return
    }

    this.ws = new WebSocket(this.url)

    this.ws.onopen = () => {
      this.connected.value = true
      this.subscribe(this.subscribedServers)
    }

    this.ws.onclose = () => {
      this.connected.value = false
      this.scheduleReconnect()
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket Error:', error)
    }

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        if (message.type === 'status_update') {
          const status: ServerStatus = message.data
          this.handlers.forEach(handler => handler(status))
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }
  }

  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.connected.value = false
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) return
    this.reconnectTimer = window.setTimeout(() => {
      this.reconnectTimer = null
      this.connect()
    }, this.reconnectInterval)
  }

  subscribe(serverIds: string[]) {
    this.subscribedServers = serverIds
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'subscribe',
        data: { server_ids: serverIds }
      }))
    }
  }

  onStatusUpdate(handler: MessageHandler) {
    this.handlers.add(handler)
    return () => this.handlers.delete(handler)
  }
}

export const wsService = new WebSocketService()

export default wsService
