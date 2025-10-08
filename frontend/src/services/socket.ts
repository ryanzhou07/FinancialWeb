import { io, Socket } from 'socket.io-client'
import type { PriceUpdatePayload } from '../types/stock'

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL ?? 'http://localhost:8000'

class SocketService {
  private socket: Socket | null = null

  connect() {
    if (!this.socket) {
      this.socket = io(SOCKET_URL, {
        transports: ['websocket'],
        autoConnect: true,
      })
    }
  }

  disconnect() {
    this.socket?.disconnect()
    this.socket = null
  }

  subscribe(symbol: string) {
    this.socket?.emit('subscribe', { symbol })
  }

  unsubscribe(symbol: string) {
    this.socket?.emit('unsubscribe', { symbol })
  }

  onPriceUpdate(callback: (payload: PriceUpdatePayload) => void) {
    this.socket?.on('price_update', callback)
  }

  offPriceUpdate(callback: (payload: PriceUpdatePayload) => void) {
    this.socket?.off('price_update', callback)
  }
}

export const socketService = new SocketService()
