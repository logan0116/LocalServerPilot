import axios from 'axios'
import type {
  APIResponse,
  Server,
  ServerCreate,
  ServerUpdate,
  ServerTestResult,
  ServiceConfig,
  ServiceConfigCreate,
  ServiceConfigUpdate,
  ServiceOperationResult,
  ServiceStatusResult,
  ServerStatus,
  GPUInfo,
  ContainerInfo,
  ListResponse
} from './types'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000
})

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const serverApi = {
  list: () => api.get<APIResponse<ListResponse<Server>>>('/servers'),

  get: (id: string) => api.get<APIResponse<Server>>(`/servers/${id}`),

  create: (data: ServerCreate) => api.post<APIResponse<Server>>('/servers', data),

  update: (id: string, data: ServerUpdate) =>
    api.put<APIResponse<Server>>(`/servers/${id}`, data),

  delete: (id: string) => api.delete(`/servers/${id}`),

  test: (id: string) => api.post<APIResponse<ServerTestResult>>(`/servers/${id}/test`),

  getStatus: (id: string) => api.get<APIResponse<ServerStatus>>(`/servers/${id}/status`),

  getGPU: (id: string) => api.get<APIResponse<GPUInfo[]>>(`/servers/${id}/gpu`),

  getContainers: (id: string) => api.get<APIResponse<ContainerInfo[]>>(`/servers/${id}/containers`)
}

export const configApi = {
  list: () => api.get<APIResponse<ListResponse<ServiceConfig>>>('/configs'),

  get: (id: string) => api.get<APIResponse<ServiceConfig>>(`/configs/${id}`),

  create: (data: ServiceConfigCreate) => api.post<APIResponse<ServiceConfig>>('/configs', data),

  update: (id: string, data: ServiceConfigUpdate) =>
    api.put<APIResponse<ServiceConfig>>(`/configs/${id}`, data),

  delete: (id: string) => api.delete(`/configs/${id}`)
}

export const serviceApi = {
  start: (serverId: string, configId: string) =>
    api.post<APIResponse<ServiceOperationResult>>(`/services/${serverId}/${configId}/start`),

  stop: (serverId: string, configId: string) =>
    api.post<APIResponse<ServiceOperationResult>>(`/services/${serverId}/${configId}/stop`),

  status: (serverId: string, configId: string) =>
    api.get<APIResponse<ServiceStatusResult>>(`/services/${serverId}/${configId}/status`)
}

export const statusApi = {
  pollAll: () => api.get<APIResponse<{ servers: ServerStatus[]; polled_at: string }>>('/status/poll')
}

export default api
