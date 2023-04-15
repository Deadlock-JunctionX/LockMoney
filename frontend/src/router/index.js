// Composables
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('@/layouts/default/Default.vue'),
    children: [
      {
        path: '',
        component: () => import(/* webpackChunkName: "home" */ '@/views/HomeView.vue'),
        meta: {
          requiresAuth: true
        }
      },
      {
        path: 'settings',
        component: () => import(/* webpackChunkName: "settings" */ '@/views/SettingsView.vue'),
        meta: {
          requiresAuth: true
        }
      },
      {
        path: 'transactions',
        component: () => import(/* webpackChunkName: "transactions" */ '@/views/TransactionsView.vue'),
        meta: {
          requiresAuth: true
        }
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
})

export default router
