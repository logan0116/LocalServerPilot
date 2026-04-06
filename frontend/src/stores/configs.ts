import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { configApi } from '@/api'
import type { ServiceConfig, ServiceConfigCreate, ServiceConfigUpdate } from '@/api/types'

export const useConfigStore = defineStore('configs', () => {
  const configs = ref<ServiceConfig[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const configList = computed(() => configs.value)
  const configCount = computed(() => configs.value.length)

  async function fetchConfigs(force = false) {
    if (!force && configs.value.length > 0) {
      return
    }
    loading.value = true
    error.value = null
    try {
      const response = await configApi.list()
      configs.value = response.data.items
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch configs'
    } finally {
      loading.value = false
    }
  }

  async function fetchConfig(id: string) {
    loading.value = true
    error.value = null
    try {
      const response = await configApi.get(id)
      const index = configs.value.findIndex(c => c.id === id)
      if (index >= 0) {
        configs.value[index] = response.data
      } else {
        configs.value.push(response.data)
      }
      return response.data
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch config'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createConfig(data: ServiceConfigCreate) {
    loading.value = true
    error.value = null
    try {
      const response = await configApi.create(data)
      configs.value.push(response.data)
      return response.data
    } catch (e: any) {
      error.value = e.message || 'Failed to create config'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateConfig(id: string, data: ServiceConfigUpdate) {
    loading.value = true
    error.value = null
    try {
      const response = await configApi.update(id, data)
      const index = configs.value.findIndex(c => c.id === id)
      if (index >= 0) {
        configs.value[index] = response.data
      }
      return response.data
    } catch (e: any) {
      error.value = e.message || 'Failed to update config'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteConfig(id: string) {
    loading.value = true
    error.value = null
    try {
      await configApi.delete(id)
      configs.value = configs.value.filter(c => c.id !== id)
    } catch (e: any) {
      error.value = e.message || 'Failed to delete config'
      throw e
    } finally {
      loading.value = false
    }
  }

  function getConfigByServer(serverName: string) {
    return configs.value.filter(c => c.allow_server.includes(serverName))
  }

  return {
    configs,
    loading,
    error,
    configList,
    configCount,
    fetchConfigs,
    fetchConfig,
    createConfig,
    updateConfig,
    deleteConfig,
    getConfigByServer
  }
})
