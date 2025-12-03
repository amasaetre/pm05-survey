import { useAuthStore } from '~/stores/auth'

export default defineNuxtRouteMiddleware((to) => {
  const auth = useAuthStore()
  if (process.client && !auth.accessToken) {
    auth.hydrate()
  }

  const isProtected = to.path.startsWith('/dashboard') || to.path.startsWith('/surveys/create') || to.path.includes('/edit') || to.path.startsWith('/profile')
  const isAuthPage = to.path === '/login' || to.path === '/register'

  if (isProtected && !auth.isAuthenticated) {
    return navigateTo('/login')
  }

  if (isAuthPage && auth.isAuthenticated) {
    return navigateTo('/dashboard')
  }
})


