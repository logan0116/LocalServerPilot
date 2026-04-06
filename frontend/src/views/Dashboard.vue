<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#409eff"><Server /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ serverStore.serverCount }}</div>
              <div class="stat-label">{{ $t('app.servers') }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#67c23a"><Document /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ configStore.configCount }}</div>
              <div class="stat-label">{{ $t('app.configs') }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#f56c6c"><Cpu /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ totalGPUs }}</div>
              <div class="stat-label">Total GPUs</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#e6a23c"><Monitor /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ runningContainers }}</div>
              <div class="stat-label">Running Containers</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-alert type="warning" :closable="false" show-icon>
          <template #title>
            <span style="font-size: 18px; font-weight: bold;">
              注意: 使用前请务必在<a href="https://docs.qq.com/sheet/DTWdIVkp5aWhGS1F2?tab=BB08J2" target="_blank" style="color: #409eff;">服务器使用登记</a>中登记使用情况
            </span>
          </template>
        </el-alert>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>{{ $t('dashboard.serverStatus') }}</span>
              <el-button type="primary" size="small" @click="refresh">
                <el-icon><Refresh /></el-icon> {{ $t('common.refresh') || 'Refresh' }}
              </el-button>
            </div>
          </template>
          <el-table :data="serverList" stripe style="width: 100%">
            <el-table-column prop="name" :label="$t('servers.name')" width="150" />
            <el-table-column prop="ip" label="IP" width="150" />
            <el-table-column prop="user" :label="$t('servers.user')" width="120" />
            <el-table-column :label="$t('dashboard.gpuInfo')" min-width="200">
              <template #default="{ row }">
                <div v-if="getServerStatus(row.id)">
                  <div v-for="(gpu, idx) in getServerStatus(row.id).gpu_info" :key="idx" class="gpu-item">
                    <el-tag size="small">{{ gpu.gpu_name }}</el-tag>
                    <el-tag size="small" :type="getGPUType(gpu.gpu_usage)">{{ gpu.gpu_usage }}</el-tag>
                    <span class="gpu-temp">{{ gpu.temperature }}</span>
                  </div>
                </div>
                <el-tag v-else type="info">{{ $t('common.loading') }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="$t('dashboard.containerInfo')" min-width="150">
              <template #default="{ row }">
                <div v-if="getServerStatus(row.id)">
                  {{ getServerStatus(row.id).container_info.length }} containers
                </div>
                <el-tag v-else type="info">{{ $t('common.loading') }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="$t('servers.actions')" width="150">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="viewDetails(row)">
                  Details
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useServerStore, useConfigStore } from '@/stores'
import type { Server } from '@/api/types'

const router = useRouter()
const serverStore = useServerStore()
const configStore = useConfigStore()

const serverList = computed(() => serverStore.serverList)

const totalGPUs = computed(() => {
  let count = 0
  serverStore.serverStatuses.forEach(status => {
    count += status.gpu_info.length
  })
  return count
})

const runningContainers = computed(() => {
  let count = 0
  serverStore.serverStatuses.forEach(status => {
    count += status.container_info.filter(c => c.status.startsWith('Up')).length
  })
  return count
})

function getServerStatus(id: string) {
  return serverStore.getServerStatus(id)
}

function getGPUType(usage: string): string {
  const value = parseInt(usage)
  if (value < 50) return 'success'
  if (value < 80) return 'warning'
  return 'danger'
}

function refresh() {
  serverStore.fetchAllStatuses()
}

function viewDetails(server: Server) {
  router.push({ name: 'Servers' })
}

onMounted(() => {
  configStore.fetchConfigs()
  serverStore.startPolling()
})

onUnmounted(() => {
  serverStore.stopPolling()
})
</script>

<style scoped>
.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  font-size: 48px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.gpu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.gpu-temp {
  font-size: 12px;
  color: #909399;
}
</style>
