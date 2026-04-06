<template>
  <div class="services-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ $t('services.title') }}</span>
        </div>
      </template>

      <el-form :inline="true">
        <el-form-item :label="$t('services.selectServer')">
          <el-select v-model="selectedServer" :placeholder="$t('services.selectServer')" @change="onServerChange">
            <el-option
              v-for="server in serverList"
              :key="server.id"
              :label="server.name"
              :value="server.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('services.selectConfig')">
          <el-select v-model="selectedConfig" :placeholder="$t('services.selectConfig')">
            <el-option
              v-for="config in availableConfigs"
              :key="config.id"
              :label="config.name"
              :value="config.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="startService" :loading="actionLoading">
            <el-icon><VideoPlay /></el-icon> {{ $t('services.start') }}
          </el-button>
          <el-button type="danger" @click="stopService" :loading="actionLoading">
            <el-icon><VideoPause /></el-icon> {{ $t('services.stop') }}
          </el-button>
          <el-button type="info" @click="checkStatus" :loading="actionLoading">
            <el-icon><Search /></el-icon> {{ $t('services.status') }}
          </el-button>
        </el-form-item>
      </el-form>

      <el-divider />

      <div v-if="selectedServer && selectedConfig" class="server-info">
        <el-descriptions :column="2" border>
          <el-descriptions-item :label="$t('servers.name')">
            {{ selectedServerName }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('configs.name')">
            {{ selectedConfigName }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('configs.startCommand')">
            <code>{{ selectedConfigData?.start_command }}</code>
          </el-descriptions-item>
          <el-descriptions-item :label="$t('configs.stopCommand')">
            <code>{{ selectedConfigData?.stop_command }}</code>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <el-divider />

      <div v-if="actionResult" class="action-result">
        <el-alert :type="actionResult.success ? 'success' : 'error'" :title="actionResult.success ? 'Success' : 'Error'" show-icon>
          <pre>{{ actionResult.output || actionResult.error }}</pre>
        </el-alert>
      </div>

      <div v-if="serviceStatus" class="service-status">
        <el-alert :type="serviceStatus.running ? 'success' : 'warning'" :title="serviceStatus.running ? $t('services.running') : $t('services.stopped')" show-icon>
          <pre>{{ serviceStatus.output }}</pre>
        </el-alert>
      </div>
    </el-card>

    <el-card style="margin-top: 20px">
      <template #header>
        <span>{{ $t('services.title') }} Overview</span>
      </template>
      <el-table :data="serverList" stripe>
        <el-table-column prop="name" :label="$t('servers.name')" width="150" />
        <el-table-column :label="$t('app.configs')" min-width="300">
          <template #default="{ row }">
            <div v-for="config in getConfigsForServer(row.name)" :key="config.id" class="service-item">
              <el-tag size="small">{{ config.name }}</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column :label="$t('dashboard.containerInfo')" min-width="200">
          <template #default="{ row }">
            <div v-if="getStatus(row.id)">
              <div v-for="container in getStatus(row.id).container_info" :key="container.name" class="container-item">
                <el-tag size="small" :type="getContainerType(container.status)">
                  {{ container.name }} - {{ container.status }}
                </el-tag>
              </div>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useServerStore, useConfigStore } from '@/stores'
import { serviceApi } from '@/api'
import type { ServiceOperationResult, ServiceStatusResult } from '@/api/types'

const serverStore = useServerStore()
const configStore = useConfigStore()

const selectedServer = ref<string>('')
const selectedConfig = ref<string>('')
const actionLoading = ref(false)
const actionResult = ref<ServiceOperationResult | null>(null)
const serviceStatus = ref<ServiceStatusResult | null>(null)

const serverList = computed(() => serverStore.serverList)
const configList = computed(() => configStore.configList)

const selectedServerName = computed(() => {
  const server = serverList.value.find(s => s.id === selectedServer.value)
  return server?.name || ''
})

const selectedConfigName = computed(() => {
  const config = configList.value.find(c => c.id === selectedConfig.value)
  return config?.name || ''
})

const selectedConfigData = computed(() => {
  return configList.value.find(c => c.id === selectedConfig.value)
})

const availableConfigs = computed(() => {
  if (!selectedServer.value) return []
  const server = serverList.value.find(s => s.id === selectedServer.value)
  if (!server) return []
  return configList.value.filter(c => c.allow_server.includes(server.name))
})

function getConfigsForServer(serverName: string) {
  return configStore.getConfigByServer(serverName)
}

function getStatus(serverId: string) {
  return serverStore.getServerStatus(serverId)
}

function getContainerType(status: string): string {
  if (status.startsWith('Up')) return 'success'
  if (status.startsWith('Exited')) return 'info'
  return 'warning'
}

function onServerChange() {
  selectedConfig.value = ''
  actionResult.value = null
  serviceStatus.value = null
}

async function startService() {
  if (!selectedServer.value || !selectedConfig.value) {
    ElMessage.warning('Please select server and service')
    return
  }
  actionLoading.value = true
  actionResult.value = null
  serviceStatus.value = null
  try {
    const response = await serviceApi.start(selectedServer.value, selectedConfig.value)
    actionResult.value = response.data
    if (!response.data.success) {
      ElMessage.error('Failed to start service')
    } else {
      ElMessage.success('Service started')
      await serverStore.fetchServerStatus(selectedServer.value)
    }
  } catch (error: any) {
    actionResult.value = { success: false, error: error.message }
    ElMessage.error('Failed to start service')
  } finally {
    actionLoading.value = false
  }
}

async function stopService() {
  if (!selectedServer.value || !selectedConfig.value) {
    ElMessage.warning('Please select server and service')
    return
  }
  actionLoading.value = true
  actionResult.value = null
  serviceStatus.value = null
  try {
    const response = await serviceApi.stop(selectedServer.value, selectedConfig.value)
    actionResult.value = response.data
    if (!response.data.success) {
      ElMessage.error('Failed to stop service')
    } else {
      ElMessage.success('Service stopped')
      await serverStore.fetchServerStatus(selectedServer.value)
    }
  } catch (error: any) {
    actionResult.value = { success: false, error: error.message }
    ElMessage.error('Failed to stop service')
  } finally {
    actionLoading.value = false
  }
}

async function checkStatus() {
  if (!selectedServer.value || !selectedConfig.value) {
    ElMessage.warning('Please select server and service')
    return
  }
  actionLoading.value = true
  actionResult.value = null
  serviceStatus.value = null
  try {
    const response = await serviceApi.status(selectedServer.value, selectedConfig.value)
    serviceStatus.value = response.data
  } catch (error: any) {
    ElMessage.error('Failed to check service status')
  } finally {
    actionLoading.value = false
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-select {
  width: 200px;
}

.service-item,
.container-item {
  margin-bottom: 4px;
}

.action-result pre,
.service-status pre {
  margin: 10px 0 0 0;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
