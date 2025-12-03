<script setup lang="ts">
const auth = useAuthStore()

const onLogout = () => {
  auth.clear()
  navigateTo('/login')
}
</script>

<template>
  <div class="max-w-2xl space-y-6 animate-fade-in">
    <header class="space-y-2">
      <h1 class="text-3xl md:text-4xl font-bold text-slate-900">
        Профиль
      </h1>
      <p class="text-slate-600">
        Управление настройками аккаунта
      </p>
    </header>

    <div class="card space-y-6">
      <div class="flex items-center gap-4 pb-6 border-b border-slate-200">
        <div class="w-16 h-16 rounded-full bg-gradient-to-br from-primary-600 to-primary-500 flex items-center justify-center text-white text-2xl font-bold shadow-lg">
          {{ auth.user?.full_name ? auth.user.full_name.charAt(0).toUpperCase() : auth.user?.email?.charAt(0).toUpperCase() }}
        </div>
        <div>
          <h2 class="text-xl font-semibold text-slate-900">
            {{ auth.user?.full_name || 'Пользователь' }}
          </h2>
          <p class="text-slate-600">{{ auth.user?.email }}</p>
        </div>
      </div>

      <div class="space-y-4">
        <div class="space-y-1">
          <label class="text-xs font-medium text-slate-500 uppercase tracking-wide">Email</label>
          <div class="flex items-center gap-2 p-3 rounded-lg bg-slate-50 border border-slate-200">
            <svg class="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
            </svg>
            <span class="text-slate-900 font-medium">{{ auth.user?.email }}</span>
          </div>
        </div>

        <div class="space-y-1">
          <label class="text-xs font-medium text-slate-500 uppercase tracking-wide">Имя</label>
          <div class="flex items-center gap-2 p-3 rounded-lg bg-slate-50 border border-slate-200">
            <svg class="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span class="text-slate-900 font-medium">{{ auth.user?.full_name || 'Не указано' }}</span>
          </div>
        </div>

        <div class="space-y-1">
          <label class="text-xs font-medium text-slate-500 uppercase tracking-wide">Роль</label>
          <div class="flex items-center gap-2 p-3 rounded-lg bg-slate-50 border border-slate-200">
            <svg class="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            <span 
              class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium"
              :class="auth.user?.role === 'admin' 
                ? 'bg-purple-100 text-purple-700' 
                : 'bg-blue-100 text-blue-700'"
            >
              {{ auth.user?.role === 'admin' ? 'Администратор' : 'Пользователь' }}
            </span>
          </div>
        </div>
      </div>

      <div class="pt-6 border-t border-slate-200 space-y-3">
        <NuxtLink to="/dashboard" class="btn-secondary w-full text-center">
          <svg class="w-5 h-5 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          Вернуться в дашборд
        </NuxtLink>
        <button class="btn-primary w-full bg-red-600 hover:bg-red-700 from-red-600 to-red-500 hover:from-red-700 hover:to-red-600" @click="onLogout">
          <svg class="w-5 h-5 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          Выйти из аккаунта
        </button>
      </div>
    </div>
  </div>
</template>


