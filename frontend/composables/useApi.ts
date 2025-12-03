export const useApi = () => {
  const auth = useAuthStore()
  const config = useRuntimeConfig()

  const apiFetch = async <T>(url: string, options: any = {}): Promise<T> => {
    const headers = {
      ...options.headers,
      ...(auth.accessToken ? { Authorization: `Bearer ${auth.accessToken}` } : {}),
    }

    try {
      return await $fetch<T>(url, {
        ...options,
        headers,
      })
    } catch (error: any) {
      const statusCode = error?.status || error?.statusCode || error?.response?.status
      
      if (process.client && statusCode === 401) {
        console.log('401 error detected, refreshToken available:', !!auth.refreshToken, 'URL:', url)
      }
      
      if (statusCode === 401 && auth.refreshToken && !url.includes('/auth/refresh')) {
        console.log('Attempting to refresh token...')
        try {
          await auth.refresh()
          console.log('Token refreshed successfully, retrying request...')

          return await $fetch<T>(url, {
            ...options,
            headers: {
              ...options.headers,
              Authorization: `Bearer ${auth.accessToken}`,
            },
          })
        } catch (refreshError: any) {
          console.error('Token refresh failed:', refreshError)
          auth.clear()
          if (process.client) {
            await navigateTo('/login')
          }
          throw refreshError
        }
      }
      throw error
    }
  }

  return {
    apiFetch,
  }
}

