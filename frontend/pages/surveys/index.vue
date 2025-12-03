<script setup lang="ts">
const surveysStore = useSurveysStore()

onMounted(() => {
  surveysStore.fetchPublicSurveys()
})
</script>

<template>
  <div class="space-y-6">
    <header class="space-y-1">
      <h1 class="text-2xl font-semibold">
        Публичные опросы
      </h1>
      <p class="text-slate-600 text-sm">
        Список доступных для прохождения опросов.
      </p>
    </header>

    <div class="grid gap-4 md:grid-cols-2">
      <div
        v-for="survey in surveysStore.items"
        :key="survey.id"
        class="card flex flex-col justify-between"
      >
        <div class="space-y-1">
          <h2 class="font-medium">
            {{ survey.title }}
          </h2>
          <p class="text-sm text-slate-600 line-clamp-3">
            {{ survey.description }}
          </p>
        </div>
        <div class="mt-4 flex justify-between items-center text-sm">
          <span class="text-slate-500">
            Вопросов: {{ survey.questions.length }}
          </span>
          <NuxtLink
            class="btn-primary text-xs"
            :to="`/surveys/${survey.id}/take`"
          >
            Пройти
          </NuxtLink>
        </div>
      </div>

      <p v-if="!surveysStore.loading && !surveysStore.items.length" class="text-sm text-slate-500">
        Публичных опросов пока нет.
      </p>
    </div>
  </div>
</template>


