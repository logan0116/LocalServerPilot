import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/dashboard'
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('@/views/Dashboard.vue')
    },
    {
      path: '/servers',
      name: 'Servers',
      component: () => import('@/views/Servers.vue')
    },
    {
      path: '/configs',
      name: 'Configs',
      component: () => import('@/views/Configs.vue')
    },
    {
      path: '/services',
      name: 'Services',
      component: () => import('@/views/Services.vue')
    }
  ]
})

export default router
