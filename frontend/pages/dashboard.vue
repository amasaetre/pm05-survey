<script setup lang="ts">
definePageMeta({
  ssr: false
})

const auth = useAuthStore()
const surveysStore = useSurveysStore()

const loading = computed(() => surveysStore.loading)
const publishing = ref<string | null>(null)
const isMounted = ref(false)

const loadSurveys = async () => {
  if (!auth.accessToken) {
    return
  }
  
  try {
    if (auth.user?.id) {
      await surveysStore.fetchMySurveys(auth.accessToken, auth.user.id)
    } else {
      await surveysStore.fetchMySurveys(auth.accessToken)
    }
  } catch (error) {
    console.error('Error loading surveys:', error)
  }
}

onMounted(async () => {
  isMounted.value = true
  
  await nextTick()
  
  if (!auth.user && auth.accessToken) {
    try {
      await auth.refresh()
    } catch {
    }
  }
  
  await loadSurveys()
})

watch([() => auth.accessToken, () => auth.user?.id], async ([newToken]) => {
  if (isMounted.value && newToken) {
    await loadSurveys()
  }
}, { immediate: false })

const togglePublish = async (surveyId: string) => {
  if (!auth.accessToken) return
  publishing.value = surveyId
  try {
    let currentToken = auth.accessToken
    
    try {
      await surveysStore.togglePublish(surveyId, currentToken)
      await loadSurveys()
    } catch (e: any) {
      const statusCode = e?.status || e?.statusCode || e?.response?.status
      if (statusCode === 401 && auth.refreshToken) {
        try {
          await auth.refresh()
          currentToken = auth.accessToken
          await surveysStore.togglePublish(surveyId, currentToken)
          await loadSurveys()
        } catch (refreshError: any) {
          auth.clear()
          await navigateTo('/login')
          throw refreshError
        }
      } else {
        throw e
      }
    }
  } catch (e: any) {
    const errorMessage = e?.data?.detail || e?.message || 'Ошибка при изменении статуса публикации'
    alert(errorMessage)
  } finally {
    publishing.value = null
  }
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

const totalSurveys = computed(() => isMounted.value ? surveysStore.items.length : 0)
const publishedCount = computed(() => isMounted.value ? surveysStore.items.filter(s => s.is_published).length : 0)
const draftsCount = computed(() => isMounted.value ? surveysStore.items.filter(s => !s.is_published).length : 0)
const surveysList = computed(() => isMounted.value ? surveysStore.items : [])
</script>

<template>
  <ClientOnly>
    <template #default>
      <div class="space-y-8">
        <header class="space-y-3">
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 class="text-3xl md:text-4xl font-bold text-slate-900">
                Дашборд
              </h1>
              <p class="text-slate-600 mt-2">
                Управляйте своими опросами и отслеживайте результаты
              </p>
            </div>
            <NuxtLink to="/surveys/create" class="btn-primary inline-flex items-center gap-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Создать опрос
            </NuxtLink>
          </div>
        </header>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div class="rounded-xl shadow-sm border border-primary-200 p-4 md:p-6 bg-gradient-to-br from-primary-50 to-primary-100">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-primary-700">Всего опросов</p>
                <p class="text-3xl font-bold text-primary-900 mt-1">
                  {{ totalSurveys }}
                </p>
              </div>
              <div class="w-12 h-12 rounded-xl bg-primary-200 flex items-center justify-center shrink-0">
                <svg class="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
          </div>
          
          <div class="rounded-xl shadow-sm border border-green-200 p-4 md:p-6 bg-gradient-to-br from-green-50 to-green-100">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-green-700">Опубликовано</p>
                <p class="text-3xl font-bold text-green-900 mt-1">
                  {{ publishedCount }}
                </p>
              </div>
              <div class="w-12 h-12 rounded-xl bg-green-200 flex items-center justify-center shrink-0">
                <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>
          
          <div class="rounded-xl shadow-sm border border-slate-200 p-4 md:p-6 bg-gradient-to-br from-slate-50 to-slate-100">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-slate-700">Черновики</p>
                <p class="text-3xl font-bold text-slate-900 mt-1">
                  {{ draftsCount }}
                </p>
              </div>
              <div class="w-12 h-12 rounded-xl bg-slate-200 flex items-center justify-center shrink-0">
                <svg class="w-6 h-6 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <div class="space-y-4">
          <h2 class="text-xl md:text-2xl font-bold text-slate-900">
            Мои опросы
          </h2>

          <div v-if="loading" class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <div v-for="i in 6" :key="i" class="card animate-pulse">
              <div class="h-5 bg-slate-200 rounded w-3/4 mb-3"></div>
              <div class="h-3 bg-slate-200 rounded w-full mb-2"></div>
              <div class="h-3 bg-slate-200 rounded w-5/6"></div>
            </div>
          </div>

          <template v-else-if="surveysList.length">
            <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              <div
                v-for="survey in surveysList"
                :key="survey.id"
                class="card-hover flex flex-col"
              >
                <div class="flex-1 space-y-3">
                  <div class="flex items-start justify-between gap-3">
                    <h3 class="font-semibold text-lg text-slate-900 line-clamp-2 flex-1">
                      {{ survey.title }}
                    </h3>
                    <span
                      class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium shrink-0"
                      :class="survey.is_published 
                        ? 'bg-green-100 text-green-700' 
                        : 'bg-slate-100 text-slate-600'"
                    >
                      <span 
                        class="w-1.5 h-1.5 rounded-full"
                        :class="survey.is_published ? 'bg-green-500' : 'bg-slate-400'"
                      ></span>
                      {{ survey.is_published ? 'Опубликован' : 'Черновик' }}
                    </span>
                  </div>
                  
                  <p class="text-sm text-slate-600 line-clamp-2 leading-relaxed">
                    {{ survey.description }}
                  </p>
                  
                  <div class="flex items-center gap-4 text-xs text-slate-500 pt-2 border-t border-slate-100">
                    <div class="flex items-center gap-1">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      {{ formatDate(survey.created_at) }}
                    </div>
                    <div class="flex items-center gap-1">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                      </svg>
                      {{ survey.questions.length }} вопросов
                    </div>
                  </div>
                </div>
                
                <div class="mt-4 pt-4 border-t border-slate-100 space-y-3">
                  <button
                    :disabled="publishing === survey.id"
                    class="w-full text-sm px-4 py-2 rounded-lg font-medium transition-all duration-200"
                    :class="survey.is_published
                      ? 'bg-red-50 text-red-600 hover:bg-red-100 border border-red-200'
                      : 'bg-green-50 text-green-600 hover:bg-green-100 border border-green-200'"
                    @click="togglePublish(survey.id)"
                  >
                    <span v-if="publishing === survey.id" class="flex items-center justify-center gap-2">
                      <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Обработка...
                    </span>
                    <span v-else>
                      {{ survey.is_published ? 'Снять с публикации' : 'Опубликовать' }}
                    </span>
                  </button>
                  
                  <div class="flex gap-2">
                    <NuxtLink 
                      :to="`/surveys/${survey.id}/edit`" 
                      class="flex-1 btn-secondary text-sm text-center"
                    >
                      Редактировать
                    </NuxtLink>
                    <NuxtLink 
                      :to="`/surveys/${survey.id}/results`" 
                      class="flex-1 btn-primary text-sm text-center"
                    >
                      Результаты
                    </NuxtLink>
                  </div>
                </div>
              </div>
            </div>
          </template>
          
          <div v-else class="card text-center py-12">
            <div class="w-16 h-16 mx-auto rounded-2xl bg-slate-100 flex items-center justify-center mb-4">
              <svg class="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-slate-900 mb-2">У вас пока нет опросов</h3>
            <p class="text-slate-600 mb-6">Создайте свой первый опрос и начните собирать ответы</p>
            <NuxtLink to="/surveys/create" class="btn-primary inline-flex items-center gap-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Создать опрос
            </NuxtLink>
          </div>
        </div>
      </div>
    </template>
    <template #fallback>
      <div class="min-h-[calc(100vh-12rem)] flex items-center justify-center py-8 md:py-12">
        <div class="text-center">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mb-4"></div>
          <p class="text-slate-600">Загрузка дашборда...</p>
        </div>
      </div>
    </template>
  </ClientOnly>
</template>
