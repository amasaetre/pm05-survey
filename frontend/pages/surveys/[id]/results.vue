<script setup lang="ts">
import { Bar, Pie } from 'vue-chartjs'

const route = useRoute()
const surveyId = route.params.id as string

const auth = useAuthStore()

const loading = ref(true)
const error = ref<string | null>(null)

interface TextResponse {
  response_id: string
  text: string
  created_at?: string | null
}

interface QuestionAnalytics {
  question_id: string
  type: 'single' | 'multi' | 'scale' | 'text'
  total_responses: number
  options?: Array<{
    option_id: string
    text: string
    count: number
    percentage: number
  }>
  histogram?: Record<string, number>
  avg?: number | null
  text_responses?: TextResponse[]
}

interface SurveyAnalytics {
  survey_id: string
  total_responses: number
  questions: QuestionAnalytics[]
}

type Survey = Awaited<ReturnType<ReturnType<typeof useSurveysStore>['getSurvey']>>

const survey = ref<Survey | null>(null)
const analytics = ref<SurveyAnalytics | null>(null)

const selectedQuestionId = ref<string | null>(null)

const loadData = async () => {
  loading.value = true
  error.value = null
  try {
    if (!auth.accessToken && !auth.refreshToken) {
      error.value = 'Требуется авторизация для просмотра результатов'
      loading.value = false
      return
    }

    const surveysStore = useSurveysStore()
    const config = useRuntimeConfig()

    survey.value = await surveysStore.getSurvey(surveyId, auth.accessToken || undefined)
    
    const fetchAnalytics = async (): Promise<SurveyAnalytics> => {
      try {
        return await $fetch<SurveyAnalytics>(`${config.public.apiBase}/api/v1/surveys/${surveyId}/analytics`, {
          headers: {
            Authorization: `Bearer ${auth.accessToken}`,
          },
        })
      } catch (e: any) {
        const statusCode = e?.status || e?.statusCode || e?.response?.status
        
        if (statusCode === 401 && auth.refreshToken) {
          console.log('401 error detected, attempting token refresh...')
          try {
            await auth.refresh()
            console.log('Token refreshed, retrying request...')
            return await $fetch<SurveyAnalytics>(`${config.public.apiBase}/api/v1/surveys/${surveyId}/analytics`, {
              headers: {
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
        throw e
      }
    }
    
    const a = await fetchAnalytics()
    analytics.value = a
    selectedQuestionId.value = a.questions[0]?.question_id ?? null
  } catch (e: any) {
    const statusCode = e?.status || e?.statusCode || e?.response?.status
    console.log('Error in loadData:', { statusCode, error: e })
    
    if (statusCode === 401) {
      error.value = 'Сессия истекла. Пожалуйста, войдите снова.'
      if (process.client) {
        await navigateTo('/login')
      }
    } else {
      error.value = e?.data?.detail || e?.message || 'Не удалось загрузить аналитику'
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

const selectedQuestion = computed(() =>
  analytics.value?.questions.find((q) => q.question_id === selectedQuestionId.value) ?? null,
)

const choiceChartData = computed(() => {
  const q = selectedQuestion.value
  if (!q || !q.options) return null
  return {
    labels: q.options.map((o) => o.text),
    datasets: [
      {
        label: 'Ответы',
        data: q.options.map((o) => o.count),
        backgroundColor: ['#3b82f6', '#22c55e', '#f97316', '#e11d48', '#6366f1'],
      },
    ],
  }
})

const scaleChartData = computed(() => {
  const q = selectedQuestion.value
  if (!q || !q.histogram) return null
  const entries = Object.entries(q.histogram).sort(
    (a, b) => Number(a[0]) - Number(b[0]),
  )
  return {
    labels: entries.map(([v]) => v),
    datasets: [
      {
        label: 'Частота',
        data: entries.map(([, c]) => c),
        backgroundColor: '#3b82f6',
      },
    ],
  }
})
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-semibold">
      Результаты опроса
    </h1>

    <div v-if="loading" class="text-sm text-slate-500">
      Загрузка данных...
    </div>

    <div v-else-if="error" class="text-sm text-red-600">
      {{ error }}
    </div>

    <div v-else-if="survey && analytics" class="space-y-6">
      <section class="card space-y-2 text-sm">
        <h2 class="text-lg font-semibold">
          {{ survey.title }}
        </h2>
        <p class="text-slate-600">
          {{ survey.description }}
        </p>
        <p class="text-xs text-slate-500">
          Всего ответов: {{ analytics.total_responses }}
        </p>
      </section>

      <section class="space-y-3">
        <div class="flex flex-wrap gap-2 text-xs">
          <button
            v-for="q in analytics.questions"
            :key="q.question_id"
            type="button"
            class="px-3 py-1 rounded-full border"
            :class="q.question_id === selectedQuestionId
              ? 'bg-primary-600 text-white border-primary-600'
              : 'border-slate-300 text-slate-700'"
            @click="selectedQuestionId = q.question_id"
          >
            Вопрос {{
              survey.questions.findIndex((sq: { id: string }) => sq.id === q.question_id) + 1
            }}
          </button>
        </div>

        <div v-if="selectedQuestion" class="grid gap-4 md:grid-cols-2">
          <div class="card space-y-2 text-sm">
            <p class="font-medium">
              {{
                survey.questions.find((sq: { id: string }) => sq.id === selectedQuestion.question_id)?.text
              }}
            </p>
            <p class="text-xs text-slate-500">
              Ответов: {{ selectedQuestion.total_responses }}
            </p>
            <div v-if="selectedQuestion.type === 'scale' && selectedQuestion.avg != null" class="text-xs text-slate-500">
              Среднее значение: {{ selectedQuestion.avg.toFixed(2) }}
            </div>
          </div>

          <div class="card">
            <template v-if="(selectedQuestion.type === 'single' || selectedQuestion.type === 'multi') && choiceChartData">
              <Bar :data="choiceChartData" :options="{ responsive: true, maintainAspectRatio: false }" style="height: 220px" />
            </template>
            <template v-else-if="selectedQuestion.type === 'scale' && scaleChartData">
              <Bar :data="scaleChartData" :options="{ responsive: true, maintainAspectRatio: false }" style="height: 220px" />
            </template>
            <template v-else-if="selectedQuestion.type === 'text'">
              <p class="text-xs text-slate-500 mb-3">
                Текстовые ответы отображаются в таблице ниже.
              </p>
            </template>
          </div>
        </div>

        <div v-if="selectedQuestion?.type === 'text' && selectedQuestion.text_responses?.length" class="card overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-slate-200">
                <th class="text-left py-2 px-3 font-medium text-slate-700">№</th>
                <th class="text-left py-2 px-3 font-medium text-slate-700">Ответ</th>
                <th class="text-left py-2 px-3 font-medium text-slate-700">Дата</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(response, index) in selectedQuestion.text_responses"
                :key="response.response_id"
                class="border-b border-slate-100 hover:bg-slate-50"
              >
                <td class="py-2 px-3 text-slate-600">
                  {{ index + 1 }}
                </td>
                <td class="py-2 px-3">
                  {{ response.text }}
                </td>
                <td class="py-2 px-3 text-slate-500 text-xs">
                  {{ response.created_at ? new Date(response.created_at).toLocaleString() : '—' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else-if="selectedQuestion?.type === 'text' && !selectedQuestion.text_responses?.length" class="card">
          <p class="text-sm text-slate-500 text-center py-4">
            Пока нет текстовых ответов на этот вопрос.
          </p>
        </div>
      </section>
    </div>
  </div>
</template>


