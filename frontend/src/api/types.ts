export interface Server {
  id: string
  name: string
  ip: string
  port: number
  user: string
  password?: string
  private_key?: string
  created_at?: string
  updated_at?: string
}

export interface ServerCreate {
  name: string
  ip: string
  user: string
  port?: number
  password?: string
  private_key?: string
}

export interface ServerUpdate {
  name?: string
  ip?: string
  user?: string
  port?: number
  password?: string
  private_key?: string
}

export interface GPUInfo {
  gpu_name: string
  gpu_usage: string
  memory_total: string
  memory_used: string
  temperature: string
}

export interface ContainerInfo {
  name: string
  image: string
  status: string
}

export interface ServerStatus {
  server_id: string
  gpu_info: GPUInfo[]
  container_info: ContainerInfo[]
  checked_at?: string
}

export interface ServiceConfig {
  id: string
  name: string
  description?: string
  image_depend: string[]
  if_gpu: boolean
  allow_server: string[]
  start_command: string
  stop_command: string
  created_at?: string
  updated_at?: string
}

export interface ServiceConfigCreate {
  name: string
  start_command: string
  stop_command: string
  description?: string
  image_depend?: string[]
  if_gpu?: boolean
  allow_server?: string[]
}

export interface ServiceConfigUpdate {
  name?: string
  start_command?: string
  stop_command?: string
  description?: string
  image_depend?: string[]
  if_gpu?: boolean
  allow_server?: string[]
}

export interface ServiceOperationResult {
  success: boolean
  output?: string
  error?: string
}

export interface ServiceStatusResult {
  running: boolean
  output: string
}

export interface APIResponse<T = any> {
  code: number
  message: string
  data: T
}

export interface ListResponse<T> {
  items: T[]
  total: number
}

export interface ServerTestResult {
  success: boolean
  message: string
}
