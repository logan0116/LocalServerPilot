<template>
  <div class="configs-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ $t('configs.title') }}</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon> {{ $t('configs.add') }}
          </el-button>
        </div>
      </template>

      <el-table :data="configList" stripe v-loading="configStore.loading">
        <el-table-column prop="name" :label="$t('configs.name')" width="200" />
        <el-table-column prop="description" :label="$t('configs.description')" min-width="200" />
        <el-table-column :label="$t('configs.gpu')" width="120">
          <template #default="{ row }">
            <el-tag :type="row.if_gpu ? 'warning' : 'info'" size="small">
              {{ row.if_gpu ? 'Yes' : 'No' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('configs.allowServers')" min-width="200">
          <template #default="{ row }">
            <el-tag
              v-for="server in row.allow_server"
              :key="server"
              size="small"
              style="margin-right: 4px"
            >
              {{ server }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('configs.actions')" width="200">
          <template #default="{ row }">
            <el-button type="warning" size="small" @click="editConfig(row)">
              {{ $t('configs.edit') }}
            </el-button>
            <el-button type="danger" size="small" @click="deleteConfig(row)">
              {{ $t('configs.delete') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="form" label-width="120px">
        <el-form-item :label="$t('configs.name')">
          <el-input v-model="form.name" :placeholder="$t('configs.name')" />
        </el-form-item>
        <el-form-item :label="$t('configs.description')">
          <el-input v-model="form.description" type="textarea" rows="2" />
        </el-form-item>
        <el-form-item :label="$t('configs.gpu')">
          <el-switch v-model="form.if_gpu" />
        </el-form-item>
        <el-form-item :label="$t('configs.allowServers')">
          <el-select v-model="form.allow_server" multiple placeholder="Select servers" style="width: 100%">
            <el-option
              v-for="server in serverList"
              :key="server.id"
              :label="server.name"
              :value="server.name"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('configs.imageDepend')">
          <el-select v-model="form.image_depend" multiple placeholder="Select images" style="width: 100%">
            <el-option label="python:3.10" value="python:3.10" />
            <el-option label="python:3.11" value="python:3.11" />
            <el-option label="cuda:11.8" value="cuda:11.8" />
            <el-option label="cuda:12.1" value="cuda:12.1" />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('configs.startCommand')">
          <el-input v-model="form.start_command" placeholder="python start.py" />
        </el-form-item>
        <el-form-item :label="$t('configs.stopCommand')">
          <el-input v-model="form.stop_command" placeholder="python stop.py" />
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
import { ref, computed, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useConfigStore, useServerStore } from '@/stores'
import type { ServiceConfig, ServiceConfigCreate, ServiceConfigUpdate } from '@/api/types'

const configStore = useConfigStore()
const serverStore = useServerStore()

const dialogVisible = ref(false)
const dialogTitle = ref('Add Config')
const editingId = ref<string | null>(null)

const form = reactive<ServiceConfigCreate>({
  name: '',
  description: '',
  if_gpu: false,
  allow_server: [],
  image_depend: [],
  start_command: '',
  stop_command: ''
})

const configList = computed(() => configStore.configList)
const serverList = computed(() => serverStore.serverList)

function showAddDialog() {
  dialogTitle.value = 'Add Config'
  editingId.value = null
  Object.assign(form, {
    name: '',
    description: '',
    if_gpu: false,
    allow_server: [],
    image_depend: [],
    start_command: '',
    stop_command: ''
  })
  dialogVisible.value = true
}

function editConfig(config: ServiceConfig) {
  dialogTitle.value = 'Edit Config'
  editingId.value = config.id
  Object.assign(form, {
    name: config.name,
    description: config.description || '',
    if_gpu: config.if_gpu,
    allow_server: [...config.allow_server],
    image_depend: [...config.image_depend],
    start_command: config.start_command,
    stop_command: config.stop_command
  })
  dialogVisible.value = true
}

async function submitForm() {
  try {
    if (editingId.value) {
      const updateData: ServiceConfigUpdate = { ...form }
      await configStore.updateConfig(editingId.value, updateData)
      ElMessage.success('Config updated')
    } else {
      await configStore.createConfig(form)
      ElMessage.success('Config created')
    }
    dialogVisible.value = false
  } catch (error: any) {
    ElMessage.error(error.message || 'Operation failed')
  }
}

async function deleteConfig(config: ServiceConfig) {
  try {
    await ElMessageBox.confirm(
      `Delete config "${config.name}"?`,
      'Warning',
      { type: 'warning' }
    )
    await configStore.deleteConfig(config.id)
    ElMessage.success('Config deleted')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('Delete failed')
    }
  }
}

onMounted(() => {
  configStore.fetchConfigs()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
