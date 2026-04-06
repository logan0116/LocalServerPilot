<template>
  <el-container class="app-container">
    <el-aside width="200px">
      <div class="logo">LocalServerPilot</div>
      <el-menu
        :default-active="$route.path"
        router
        class="app-menu"
        :class="{ 'dark-menu': themeStore.isDark }"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataBoard /></el-icon>
          <span>{{ $t('app.dashboard') }}</span>
        </el-menu-item>
        <el-menu-item index="/servers">
          <el-icon><Box /></el-icon>
          <span>{{ $t('app.servers') }}</span>
        </el-menu-item>
        <el-menu-item index="/configs">
          <el-icon><Document /></el-icon>
          <span>{{ $t('app.configs') }}</span>
        </el-menu-item>
        <el-menu-item index="/services">
          <el-icon><Operation /></el-icon>
          <span>{{ $t('app.services') }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header>
        <div class="header-content">
          <h2>{{ pageTitle }}</h2>
          <div class="header-actions">
            <el-button-group>
              <el-button 
                :type="themeStore.isDark ? 'primary' : 'default'" 
                size="small"
                @click="themeStore.toggleTheme()"
                :icon="themeStore.isDark ? 'Sunny' : 'Moon'"
              >
                {{ themeStore.isDark ? 'Light' : 'Dark' }}
              </el-button>
              <el-button 
                :type="locale === 'zh' ? 'primary' : 'default'" 
                size="small"
                @click="toggleLocale"
              >
                {{ locale === 'zh' ? 'EN' : '中文' }}
              </el-button>
            </el-button-group>
            <el-tag :type="wsConnected ? 'success' : 'danger'" size="small">
              {{ wsConnected ? $t('app.connected') : $t('app.disconnected') }}
            </el-tag>
          </div>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useServerStore, useThemeStore } from '@/stores'
import wsService from '@/api/websocket'
import { DataBoard, Server, Document, Operation, Sunny, Moon } from '@element-plus/icons-vue'

const route = useRoute()
const { locale } = useI18n()
const serverStore = useServerStore()
const themeStore = useThemeStore()

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    '/dashboard': 'app.dashboard',
    '/servers': 'app.servers',
    '/configs': 'app.configs',
    '/services': 'app.services'
  }
  return titles[route.path] ? route.path : 'app.title'
})

const wsConnected = computed(() => wsService.isConnected.value)

const toggleLocale = () => {
  locale.value = locale.value === 'zh' ? 'en' : 'zh'
  localStorage.setItem('locale', locale.value)
}

onMounted(() => {
  serverStore.fetchServers()
  wsService.connect()
})

onUnmounted(() => {
  serverStore.stopPolling()
})
</script>

<style>
html.dark, body.dark {
  background-color: #1a1a1a;
  color: #e0e0e0;
}

html.dark .el-container {
  background-color: #1a1a1a;
}

html.dark .el-aside {
  background-color: #2a2a2a !important;
}

html.dark .el-menu {
  background-color: #2a2a2a !important;
  border-right: none;
}

html.dark .el-menu-item {
  color: #e0e0e0 !important;
}

html.dark .el-menu-item:hover {
  background-color: #3a3a3a !important;
}

html.dark .el-menu-item.is-active {
  background-color: #409eff !important;
  color: #fff !important;
}

html.dark .logo {
  background-color: #2a2a2a !important;
  color: #409eff;
}

html.dark .el-header {
  background-color: #2a2a2a !important;
  border-bottom-color: #3a3a3a !important;
}

html.dark .el-header h2 {
  color: #e0e0e0 !important;
}

html.dark .el-main {
  background-color: #1a1a1a !important;
}

html.dark .el-card {
  background-color: #2a2a2a !important;
  border-color: #3a3a3a !important;
}

html.dark .el-table {
  background-color: #2a2a2a !important;
  color: #e0e0e0 !important;
}

html.dark .el-table tr {
  background-color: #2a2a2a !important;
}

html.dark .el-table th {
  background-color: #3a3a3a !important;
  color: #e0e0e0 !important;
}

html.dark .el-table td {
  border-color: #3a3a3a !important;
}

html.dark .el-input__wrapper {
  background-color: #2a2a2a !important;
}

html.dark .el-input__inner {
  color: #e0e0e0 !important;
}

html.dark .el-select-dropdown {
  background-color: #2a2a2a !important;
}

html.dark .el-select-dropdown__item {
  color: #e0e0e0 !important;
}

html.dark .el-select-dropdown__item:hover {
  background-color: #3a3a3a !important;
}

html.dark .el-form-item__label {
  color: #e0e0e0 !important;
}

html.dark .el-dialog {
  background-color: #2a2a2a !important;
}

html.dark .el-dialog__title {
  color: #e0e0e0 !important;
}

html.dark .el-button--default {
  background-color: #3a3a3a !important;
  color: #e0e0e0 !important;
  border-color: #4a4a4a !important;
}

html.dark .el-tag {
  color: #e0e0e0 !important;
}

html.dark .dark-menu {
  background-color: #2a2a2a !important;
}
</style>

<style scoped>
.app-container {
  height: 100vh;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  font-size: 18px;
  font-weight: bold;
  color: #409eff;
  background: #f5f5f5;
}

.app-menu {
  border-right: none;
}

.el-header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h2 {
  margin: 0;
  font-size: 18px;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.el-main {
  background: #f5f5f5;
  padding: 20px;
}
</style>
