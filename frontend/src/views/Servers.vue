<template>
  <div class="servers-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ $t('servers.title') }}</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon> {{ $t('servers.add') }}
          </el-button>
        </div>
      </template>

      <el-table :data="serverList" stripe v-loading="serverStore.loading">
        <el-table-column prop="name" :label="$t('servers.name')" width="150" />
        <el-table-column prop="ip" label="IP" width="150" />
        <el-table-column prop="port" :label="$t('servers.port')" width="100" />
        <el-table-column prop="user" :label="$t('servers.user')" width="120" />
        <el-table-column :label="$t('dashboard.serverStatus')" width="120">
          <template #default="{ row }">
            <el-tag v-if="getStatus(row.id)" type="success" size="small">Online</el-tag>
            <el-tag v-else type="info" size="small">Unknown</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('servers.actions')">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="testServer(row)">
              {{ $t('servers.test') }}
            </el-button>
            <el-button type="warning" size="small" @click="editServer(row)">
              {{ $t('servers.edit') }}
            </el-button>
            <el-button type="danger" size="small" @click="deleteServer(row)">
              {{ $t('servers.delete') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item :label="$t('servers.name')">
          <el-input v-model="form.name" :placeholder="$t('servers.name')" />
        </el-form-item>
        <el-form-item label="IP">
          <el-input v-model="form.ip" placeholder="192.168.1.100" />
        </el-form-item>
        <el-form-item :label="$t('servers.port')">
          <el-input-number v-model="form.port" :min="1" :max="65535" />
        </el-form-item>
        <el-form-item :label="$t('servers.user')">
          <el-input v-model="form.user" placeholder="root" />
        </el-form-item>
        <el-form-item :label="$t('servers.password')">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-form-item :label="$t('servers.privateKey')">
          <el-input v-model="form.private_key" placeholder="/path/to/key" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="submitForm">{{ $t('common.confirm') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useServerStore } from '@/stores'
import type { Server, ServerCreate, ServerUpdate } from '@/api/types'

const serverStore = useServerStore()

const dialogVisible = ref(false)
const dialogTitle = ref('')
const editingId = ref<string | null>(null)

const form = reactive<ServerCreate>({
  name: '',
  ip: '',
  user: '',
  port: 22,
  password: '',
  private_key: ''
})

const serverList = computed(() => serverStore.serverList)

function getStatus(id: string) {
  return serverStore.getServerStatus(id)
}

function showAddDialog() {
  dialogTitle.value = 'Add Server'
  editingId.value = null
  Object.assign(form, {
    name: '',
    ip: '',
    user: '',
    port: 22,
    password: '',
    private_key: ''
  })
  dialogVisible.value = true
}

function editServer(server: Server) {
  dialogTitle.value = 'Edit Server'
  editingId.value = server.id
  Object.assign(form, {
    name: server.name,
    ip: server.ip,
    user: server.user,
    port: server.port,
    password: server.password || '',
    private_key: server.private_key || ''
  })
  dialogVisible.value = true
}

async function submitForm() {
  try {
    if (editingId.value) {
      const updateData: ServerUpdate = { ...form }
      await serverStore.updateServer(editingId.value, updateData)
      ElMessage.success('Server updated')
    } else {
      await serverStore.createServer(form)
      ElMessage.success('Server created')
    }
    dialogVisible.value = false
  } catch (error: any) {
    ElMessage.error(error.message || 'Operation failed')
  }
}

async function testServer(server: Server) {
  try {
    const result = await serverStore.testServer(server.id)
    if (result.success) {
      ElMessage.success('Connection successful')
    } else {
      ElMessage.error(result.message || 'Connection failed')
    }
  } catch (error: any) {
    ElMessage.error('Connection test failed')
  }
}

async function deleteServer(server: Server) {
  try {
    await ElMessageBox.confirm(
      `Delete server "${server.name}"?`,
      'Warning',
      { type: 'warning' }
    )
    await serverStore.deleteServer(server.id)
    ElMessage.success('Server deleted')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('Delete failed')
    }
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
