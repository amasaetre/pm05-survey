<script setup lang="ts">
const auth = useAuthStore()

const onLogout = () => {
  auth.clear()
  navigateTo('/')
}
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <header class="border-b border-slate-200 bg-white/80 backdrop-blur-sm sticky top-0 z-50 shadow-sm">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <NuxtLink to="/" class="flex items-center gap-2 group">
            <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-600 to-primary-500 flex items-center justify-center shadow-sm group-hover:shadow-md transition-shadow">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <span class="text-xl font-bold bg-gradient-to-r from-primary-600 to-primary-500 bg-clip-text text-transparent">
              SurveyHub
            </span>
          </NuxtLink>
          <nav class="hidden md:flex items-center gap-6 text-sm">
            <NuxtLink 
              to="/surveys" 
              class="text-slate-600 hover:text-primary-600 font-medium transition-colors"
              active-class="text-primary-600"
            >
              Опросы
            </NuxtLink>
            <ClientOnly>
              <NuxtLink 
                v-if="auth.isAuthenticated" 
                to="/dashboard" 
                class="text-slate-600 hover:text-primary-600 font-medium transition-colors"
                active-class="text-primary-600"
              >
                Дашборд
              </NuxtLink>
              <NuxtLink 
                v-if="auth.isAuthenticated" 
                to="/profile" 
                class="text-slate-600 hover:text-primary-600 font-medium transition-colors"
                active-class="text-primary-600"
              >
                Профиль
              </NuxtLink>
              <template #fallback>
                <span class="text-slate-600 font-medium opacity-0">Дашборд</span>
                <span class="text-slate-600 font-medium opacity-0">Профиль</span>
              </template>
            </ClientOnly>
          </nav>
          <div class="flex items-center gap-3">
            <ClientOnly>
              <template #default>
                <button
                  v-if="auth.isAuthenticated"
                  class="btn-secondary text-sm hidden sm:inline-flex"
                  @click="onLogout"
                >
                  Выйти
                </button>
              <NuxtLink 
                v-else 
                to="/login" 
                class="btn-primary text-sm"
              >
                Войти
                    </NuxtLink>
                    <button
                  v-if="auth.isAuthenticated"
                  class="md:hidden p-2 rounded-lg text-slate-600 hover:bg-slate-100"
                  @click="onLogout"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                </button>
              </template>
              <template #fallback>
                <button class="btn-primary text-sm" disabled>
                  Войти
                </button>
              </template>
            </ClientOnly>
          </div>
        </div>
      </div>
    </header>
    <main class="flex-1">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6 md:py-8">
        <NuxtPage />
      </div>
    </main>
    <footer class="border-t border-slate-200 bg-white/50 mt-auto">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6">
        <p class="text-center text-sm text-slate-500">
          © 2025 SurveyHub. Платформа для создания и проведения онлайн-опросов.
        </p>
      </div>
    </footer>
  </div>
</template>


