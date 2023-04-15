// Composables
import { createRouter, createWebHistory } from 'vue-router'
import { useAppStore } from '@/store/app'
import Cookies from 'js-cookie'

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
      {
        path: 'login',
        component: () => import(/* webpackChunkName: "login" */ '@/views/LoginView.vue'),
        meta: {
          requiresAuth: false
        }
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth) {
    const accessToken = Cookies.get("access_token");
    if (!accessToken) {
      return {
        path: '/login',
        query: { redirect: to.path },
      }
    }

    const store = useAppStore()
    return store.fetchUser().catch(() => {
      // this route requires auth, check if logged in
      // if not, redirect to login page.
      return {
        path: '/login',
        query: { redirect: to.path },
      }
    })
  }
})

export default router
