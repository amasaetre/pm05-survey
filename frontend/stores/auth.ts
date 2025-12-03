import { defineStore } from 'pinia'

interface User {
  id: string
  email: string
  full_name?: string | null
  role: 'user' | 'admin'
}

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  loading: boolean
}

const STORAGE_KEY = 'online-surveys-auth'

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    accessToken: null,
    refreshToken: null,
    loading: false,
  }),
  getters: {
    isAuthenticated: (state) => !!state.accessToken,
  },
  actions: {
    hydrate() {
      if (process.client) {
        const raw = window.localStorage.getItem(STORAGE_KEY)
        if (raw) {
          try {
            const parsed = JSON.parse(raw)
            this.user = parsed.user
            this.accessToken = parsed.accessToken
            this.refreshToken = parsed.refreshToken
          } catch {
          }
        }
      }
    },
    persist() {
      if (process.client) {
        window.localStorage.setItem(
          STORAGE_KEY,
          JSON.stringify({
            user: this.user,
            accessToken: this.accessToken,
            refreshToken: this.refreshToken,
          }),
        )
      }
    },
    clear() {
      this.user = null
      this.accessToken = null
      this.refreshToken = null
      if (process.client) {
        window.localStorage.removeItem(STORAGE_KEY)
      }
    },
    async login(email: string, password: string) {
      const config = useRuntimeConfig()
      this.loading = true
      try {
        const form = new URLSearchParams()
        form.append('username', email)
        form.append('password', password)
        const tokenRes = await $fetch<{
          access_token: string
          refresh_token: string
          token_type: string
        }>(`${config.public.apiBase}/api/v1/auth/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: form.toString(),
        })
        this.accessToken = tokenRes.access_token
        this.refreshToken = tokenRes.refresh_token

        const me = await $fetch<User>(`${config.public.apiBase}/api/v1/auth/me`, {
          headers: {
            Authorization: `Bearer ${this.accessToken}`,
          },
        })
        this.user = me
        this.persist()
      } finally {
        this.loading = false
      }
    },
    async register(email: string, password: string, fullName?: string) {
      const config = useRuntimeConfig()
      this.loading = true
      try {
        await $fetch<User>(`${config.public.apiBase}/api/v1/auth/register`, {
          method: 'POST',
          body: {
            email,
            password,
            full_name: fullName,
          },
        })
        await this.login(email, password)
      } catch (e: any) {
        throw e
      } finally {
        this.loading = false
      }
    },
    async refresh() {
      if (!this.refreshToken) {
        throw new Error('No refresh token available')
      }
      const config = useRuntimeConfig()
      try {
        console.log('Refreshing token...')
        const tokenRes = await $fetch<{
          access_token: string
          refresh_token: string
          token_type: string
        }>(`${config.public.apiBase}/api/v1/auth/refresh`, {
          method: 'POST',
          body: {
            refresh_token: this.refreshToken,
          },
        })
        console.log('Token refresh successful')
        this.accessToken = tokenRes.access_token
        this.refreshToken = tokenRes.refresh_token
        this.persist()
      } catch (e: any) {
        console.error('Token refresh failed:', e)
        this.clear()
        throw e
      }
    },
  },
})


