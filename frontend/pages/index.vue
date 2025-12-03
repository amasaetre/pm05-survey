<script setup lang="ts">
const surveysStore = useSurveysStore()
const auth = useAuthStore()

onMounted(() => {
  surveysStore.fetchPublicSurveys()
})
</script>

<template>
  <div class="space-y-8 md:space-y-12 animate-fade-in">
    <section class="text-center space-y-6 py-8 md:py-12">
      <div class="space-y-4">
        <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight">
          <span class="bg-gradient-to-r from-primary-600 via-primary-500 to-primary-600 bg-clip-text text-transparent">
            Создавайте и проходите
          </span>
          <br>
          <span class="text-slate-900">онлайн-опросы</span>
        </h1>
        <p class="text-lg md:text-xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
          Платформа для быстрых опросов с аналитикой в реальном времени. Публикуйте опросы, собирайте ответы и
          анализируйте результаты.
        </p>
      </div>
      <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
        <NuxtLink 
          v-if="auth.isAuthenticated"
          to="/surveys/create" 
          class="btn-primary text-base px-6 py-3"
        >
          <svg class="w-5 h-5 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Создать опрос
        </NuxtLink>
        <NuxtLink 
          v-else
          to="/register" 
          class="btn-primary text-base px-6 py-3"
        >
          Начать бесплатно
        </NuxtLink>
        <NuxtLink 
          to="/surveys" 
          class="btn-secondary text-base px-6 py-3"
        >
          Посмотреть опросы
        </NuxtLink>
      </div>
    </section>

    <section class="grid md:grid-cols-3 gap-6 py-8">
      <div class="card text-center space-y-3">
        <div class="w-12 h-12 mx-auto rounded-xl bg-primary-100 flex items-center justify-center">
          <svg class="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 class="font-semibold text-lg">Разные типы вопросов</h3>
        <p class="text-sm text-slate-600">Одиночный выбор, множественный выбор, шкала оценок и текстовые ответы</p>
      </div>
      <div class="card text-center space-y-3">
        <div class="w-12 h-12 mx-auto rounded-xl bg-green-100 flex items-center justify-center">
          <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <h3 class="font-semibold text-lg">Аналитика в реальном времени</h3>
        <p class="text-sm text-slate-600">Графики, диаграммы и статистика по каждому вопросу</p>
      </div>
      <div class="card text-center space-y-3">
        <div class="w-12 h-12 mx-auto rounded-xl bg-purple-100 flex items-center justify-center">
          <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <h3 class="font-semibold text-lg">Безопасность</h3>
        <p class="text-sm text-slate-600">Защита от повторных прохождений и безопасное хранение данных</p>
      </div>
    </section>

    <section class="space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-2xl md:text-3xl font-bold text-slate-900">
            Публичные опросы
          </h2>
          <p class="text-slate-600 mt-1">
            Присоединяйтесь к опросам и делитесь своим мнением
          </p>
        </div>
      </div>
      
      <div v-if="surveysStore.loading" class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <div v-for="i in 6" :key="i" class="card animate-pulse">
          <div class="h-4 bg-slate-200 rounded w-3/4 mb-3"></div>
          <div class="h-3 bg-slate-200 rounded w-full mb-2"></div>
          <div class="h-3 bg-slate-200 rounded w-5/6"></div>
        </div>
      </div>
      
      <div v-else-if="surveysStore.items.length" class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="survey in surveysStore.items"
          :key="survey.id"
          class="card-hover flex flex-col justify-between group"
        >
          <div class="space-y-3">
            <h3 class="font-semibold text-lg text-slate-900 group-hover:text-primary-600 transition-colors">
              {{ survey.title }}
            </h3>
            <p class="text-sm text-slate-600 line-clamp-3 leading-relaxed">
              {{ survey.description }}
            </p>
          </div>
          <div class="mt-6 flex justify-between items-center pt-4 border-t border-slate-100">
            <div class="flex items-center gap-2 text-xs text-slate-500">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              <span>{{ survey.questions.length }} вопросов</span>
            </div>
            <NuxtLink
              class="btn-primary text-sm"
              :to="`/surveys/${survey.id}/take`"
            >
              Пройти
            </NuxtLink>
          </div>
        </div>
      </div>
      
      <div v-else class="card text-center py-12">
        <svg class="w-16 h-16 mx-auto text-slate-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="text-slate-500 text-lg">Пока нет опубликованных опросов</p>
        <p class="text-slate-400 text-sm mt-2">Будьте первым, кто создаст опрос!</p>
      </div>
    </section>
  </div>
</template>


