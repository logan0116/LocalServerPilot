import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { serverApi, statusApi } from '@/api'
import type { Server, ServerCreate, ServerUpdate, ServerStatus } from '@/api/types'
import wsService from '@/api/websocket'

export const useServerStore = defineStore('servers', () => {
  const servers = ref<Server[]>([])
  const serverStatuses = ref<Map<string, ServerStatus>>(new Map())
  const loading = ref(false)
  const error = ref<string | null>(null)
  const pollInterval = ref<number>(15000)
  let pollTimer: number | null = null

  const serverList = computed(() => servers.value)
  const serverCount = computed(() => servers.value.length)

  async function fetchServers(force = false) {
    if (!force && servers.value.length > 0) {
      return
    }
    loading.value = true
    error.value = null
    try {
      const response = await serverApi.list()
      servers.value = response.data.items
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch servers'
    } finally {
      loading.value = false
    }
  }

  async function fetchServer(id: string) {
    loading.value = true
    error.value = null
    try {
      const response = await serverApi.get(id)
      const index = servers.value.findIndex(s => s.id === id)
      if (index >= 0) {
        servers.value[index] = response.data
      } else {
        servers.value.push(response.data)
      }
      return response.data
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch server'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createServer(data: ServerCreate) {
    loading.value = true
    error.value = null
    try {
      const response = await serverApi.create(data)
      servers.value.push(response.data)
      return response.data
    } catch (e: any) {
      error.value = e.message || 'Failed to create server'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateServer(id: string, data: ServerUpdate) {
    loading.value = true
    error.value = null
    try {
      const response = await serverApi.update(id, data)
      const index = servers.value.findIndex(s => s.id === id)
      if (index >= 0) {
        servers.value[index] = response.data
      }
      return response.data
    } catch (e: any) {
      error.value = e.message || 'Failed to update server'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteServer(id: string) {
    loading.value = true
    error.value = null
    try {
      await serverApi.delete(id)
      servers.value = servers.value.filter(s => s.id !== id)
      serverStatuses.value.delete(id)
    } catch (e: any) {
      error.value = e.message || 'Failed to delete server'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function testServer(id: string) {
    try {
      const response = await serverApi.test(id)
      return response.data
    } catch (e: any) {
      return { success: false, message: e.message }
    }
  }

  async function fetchServerStatus(id: string) {
    try {
      const response = await serverApi.getStatus(id)
      serverStatuses.value.set(id, response.data)
      return response.data
    } catch (e: any) {
      console.error('Failed to fetch server status:', e)
      return null
    }
  }

  async function fetchAllStatuses() {
    try {
      const response = await statusApi.pollAll()
      response.data.servers.forEach(status => {
        serverStatuses.value.set(status.server_id, status)
      })
    } catch (e: any) {
      console.error('Failed to poll all statuses:', e)
    }
  }

  function getServerStatus(id: string) {
    return serverStatuses.value.get(id)
  }

  function startPolling(interval?: number) {
    if (interval) {
      pollInterval.value = interval
    }
    stopPolling()
    fetchAllStatuses()
    pollTimer = window.setInterval(fetchAllStatuses, pollInterval.value)
    wsService.connect()
    wsService.onStatusUpdate((status) => {
      serverStatuses.value.set(status.server_id, status)
    })
  }

  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
    wsService.disconnect()
  }

  return {
    servers,
    serverStatuses,
    loading,
    error,
    serverList,
    serverCount,
    fetchServers,
    fetchServer,
    createServer,
    updateServer,
    deleteServer,
    testServer,
    fetchServerStatus,
    fetchAllStatuses,
    getServerStatus,
    startPolling,
    stopPolling
  }
})
