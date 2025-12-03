<script setup lang="ts">
const auth = useAuthStore()

const email = ref('')
const fullName = ref('')
const password = ref('')
const password2 = ref('')
const error = ref<string | null>(null)
const showPassword = ref(false)
const showPassword2 = ref(false)

const onSubmit = async () => {
  error.value = null
  if (!email.value || !password.value) {
    error.value = 'Заполните email и пароль'
    return
  }
  if (password.value.length < 6) {
    error.value = 'Пароль должен быть не менее 6 символов'
    return
  }
  if (password.value !== password2.value) {
    error.value = 'Пароли не совпадают'
    return
  }
  try {
    await auth.register(email.value, password.value, fullName.value || undefined)
    await navigateTo('/dashboard')
  } catch (e: any) {
    error.value = e?.data?.detail || 'Ошибка регистрации'
  }
}
</script>

<template>
  <div class="min-h-[calc(100vh-12rem)] flex items-center justify-center py-8 md:py-12">
    <div class="w-full max-w-md">
      <div class="card space-y-6 animate-slide-up">
        <div class="text-center space-y-2">
          <div class="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-primary-600 to-primary-500 flex items-center justify-center shadow-lg">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
          </div>
          <h1 class="text-2xl md:text-3xl font-bold text-slate-900">
            Создать аккаунт
          </h1>
          <p class="text-slate-600">
            Зарегистрируйтесь, чтобы начать создавать опросы
          </p>
        </div>

        <form class="space-y-5" @submit.prevent="onSubmit">
          <div class="space-y-2">
            <label class="label">Email</label>
              <input
                v-model="email"
                type="email"
                class="input"
                :class="{ 'input-error': error }"
                placeholder="you@example.com"
                autocomplete="email"
                required
              >
          </div>
          
          <div class="space-y-2">
            <label class="label">Имя (необязательно)</label>
              <input
                v-model="fullName"
                type="text"
                class="input"
                placeholder="Иван Иванов"
                autocomplete="name"
              >
          </div>
          
          <div class="space-y-2">
            <label class="label">Пароль</label>
            <div class="relative">
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                class="input pr-10"
                :class="{ 'input-error': error }"
                placeholder="Минимум 6 символов"
                autocomplete="new-password"
                required
              >
              <button
                type="button"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                @click="showPassword = !showPassword"
              >
                <svg v-if="showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </button>
            </div>
          </div>
          
          <div class="space-y-2">
            <label class="label">Повторите пароль</label>
            <div class="relative">
              <input
                v-model="password2"
                :type="showPassword2 ? 'text' : 'password'"
                class="input pr-10"
                :class="{ 'input-error': error }"
                placeholder="Повторите пароль"
                autocomplete="new-password"
                required
              >
              <button
                type="button"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                @click="showPassword2 = !showPassword2"
              >
                <svg v-if="showPassword2" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </button>
            </div>
          </div>

          <div v-if="error" class="p-3 rounded-lg bg-red-50 border border-red-200">
            <p class="text-sm text-red-600 flex items-center gap-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ error }}
            </p>
          </div>

          <button
            type="submit"
            class="btn-primary w-full"
            :disabled="auth.loading"
          >
            <span v-if="auth.loading" class="flex items-center justify-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Регистрация...
            </span>
            <span v-else>Зарегистрироваться</span>
          </button>
        </form>

        <div class="pt-4 border-t border-slate-200">
          <p class="text-center text-sm text-slate-600">
            Уже есть аккаунт?
            <NuxtLink to="/login" class="text-primary-600 hover:text-primary-700 font-medium hover:underline">
              Войти
            </NuxtLink>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>


