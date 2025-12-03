<script setup lang="ts">
const route = useRoute()
const surveyId = route.params.id as string

const surveysStore = useSurveysStore()
const auth = useAuthStore()

const loading = ref(true)
const submitting = ref(false)
const error = ref<string | null>(null)
const success = ref(false)
const alreadyResponded = ref(false)

const survey = ref<Awaited<ReturnType<typeof surveysStore.getSurvey>> | null>(null)

type QuestionType = 'single' | 'multi' | 'scale' | 'text'

interface AnswerState {
  valueText: string | null
  valueNumber: number | null
  optionIds: string[]
}

const answers = ref<Record<string, AnswerState>>({})

interface QuestionAnalyticsPreview {
  question_id: string
  total_responses: number
}

const basicStats = ref<QuestionAnalyticsPreview[] | null>(null)

const initAnswers = () => {
  if (!survey.value) return
  const map: Record<string, AnswerState> = {}
  for (const q of survey.value.questions) {
    map[q.id] = {
      valueText: null,
      valueNumber: null,
      optionIds: [],
    }
  }
  answers.value = map
}

const loadSurvey = async () => {
  loading.value = true
  error.value = null
  try {
    const s = await surveysStore.getSurvey(surveyId)
    survey.value = s
    initAnswers()
    
    const config = useRuntimeConfig()
    try {
      const check = await $fetch<{ has_responded: boolean }>(
        `${config.public.apiBase}/api/v1/surveys/${surveyId}/responses/check`,
        {
          headers: auth.accessToken
            ? { Authorization: `Bearer ${auth.accessToken}` }
            : undefined,
          credentials: 'include',
        }
      )
      alreadyResponded.value = check.has_responded
    } catch {
      alreadyResponded.value = false
    }
  } catch (e: any) {
    error.value = e?.data?.detail || 'Не удалось загрузить опрос'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadSurvey()
})

const toggleMultiOption = (questionId: string, optionId: string) => {
  const a = answers.value[questionId]
  if (!a) return
  if (a.optionIds.includes(optionId)) {
    a.optionIds = a.optionIds.filter((id) => id !== optionId)
  } else {
    a.optionIds = [...a.optionIds, optionId]
  }
}

const onSubmit = async () => {
  if (!survey.value) return
  error.value = null
  success.value = false

  for (const q of survey.value.questions) {
    if (!q.required) continue
    const a = answers.value[q.id]
    if (!a) continue
    if (q.type === 'text' && !a.valueText) {
      error.value = 'Заполните все обязательные вопросы'
      return
    }
    if (q.type === 'scale' && (a.valueNumber === null || a.valueNumber === undefined)) {
      error.value = 'Заполните все обязательные вопросы'
      return
    }
    if ((q.type === 'single' || q.type === 'multi') && !a.optionIds.length) {
      error.value = 'Заполните все обязательные вопросы'
      return
    }
  }

  submitting.value = true
  try {
    const config = useRuntimeConfig()
    const payload = {
      user_id: null as string | null,
      answers: survey.value.questions.map((q) => {
        const a = answers.value[q.id]
        return {
          question_id: q.id,
          value_text: q.type === 'text' ? a?.valueText ?? null : null,
          value_number: q.type === 'scale' ? a?.valueNumber ?? null : null,
          option_ids: (q.type === 'single' || q.type === 'multi') ? a?.optionIds ?? [] : undefined,
        }
      }),
    }

    await $fetch(`${config.public.apiBase}/api/v1/surveys/${surveyId}/responses`, {
      method: 'POST',
      body: payload,
      headers: auth.accessToken
        ? { Authorization: `Bearer ${auth.accessToken}` }
        : undefined,
      credentials: 'include',
    })

    success.value = true

    try {
      const analytics = await $fetch<{
        survey_id: string
        total_responses: number
        questions: Array<{ question_id: string; total_responses: number }>
      }>(`${config.public.apiBase}/api/v1/surveys/${surveyId}/analytics`, {
        headers: auth.accessToken
          ? { Authorization: `Bearer ${auth.accessToken}` }
          : undefined,
      })
      basicStats.value = analytics.questions.map((q) => ({
        question_id: q.question_id,
        total_responses: q.total_responses,
      }))
    } catch {
      basicStats.value = null
    }
  } catch (e: any) {
    const errorMessage = e?.data?.detail || 'Ошибка отправки ответов'
    error.value = errorMessage
    
    if (errorMessage.includes('already submitted') || errorMessage.includes('уже проходили')) {
      alreadyResponded.value = true
    }
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="space-y-6">
    <div v-if="loading" class="text-sm text-slate-500">
      Загрузка опроса...
    </div>
    <div v-else-if="!survey" class="text-sm text-red-600">
      {{ error || 'Опрос не найден' }}
    </div>
    <div v-else class="space-y-6">
      <header class="space-y-2">
        <h1 class="text-2xl font-semibold">
          {{ survey.title }}
        </h1>
        <p class="text-slate-600">
          {{ survey.description }}
        </p>
      </header>

      <div v-if="alreadyResponded" class="card bg-yellow-50 border-yellow-200">
        <p class="text-sm text-yellow-800">
          Вы уже проходили этот опрос. Повторное прохождение недоступно.
        </p>
      </div>

      <form v-else class="space-y-6" @submit.prevent="onSubmit">
        <div
          v-for="(q, index) in survey.questions"
          :key="q.id"
          class="card space-y-3"
        >
          <div class="flex justify-between items-center">
            <div class="space-y-1">
              <p class="font-medium">
                {{ index + 1 }}. {{ q.text }}
              </p>
              <p class="text-xs text-slate-500">
                <span v-if="q.required">Обязательный вопрос</span>
                <span v-else>Необязательный вопрос</span>
              </p>
            </div>
          </div>

          <div v-if="q.type === 'single' || q.type === 'multi'" class="space-y-2 text-sm">
            <div
              v-for="opt in q.options"
              :key="opt.id"
              class="flex items-center gap-2"
            >
              <input
                :id="`${q.id}-${opt.id}`"
                :type="q.type === 'single' ? 'radio' : 'checkbox'"
                :name="q.id"
                class="h-4 w-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
                :checked="answers[q.id]?.optionIds.includes(opt.id)"
                @change="q.type === 'single'
                  ? (answers[q.id].optionIds = [opt.id])
                  : toggleMultiOption(q.id, opt.id)"
              >
              <label
                :for="`${q.id}-${opt.id}`"
                class="text-slate-700"
              >
                {{ opt.text }}
              </label>
            </div>
          </div>

          <div v-else-if="q.type === 'scale'" class="space-y-2 text-sm">
            <div class="flex items-center gap-3">
              <span class="text-xs text-slate-500">
                {{ (q.meta as any)?.min ?? 1 }}
              </span>
              <input
                v-model.number="answers[q.id].valueNumber"
                type="range"
                class="flex-1"
                :min="(q.meta as any)?.min ?? 1"
                :max="(q.meta as any)?.max ?? 5"
                :step="1"
              >
              <span class="text-xs text-slate-500">
                {{ (q.meta as any)?.max ?? 5 }}
              </span>
            </div>
            <div class="text-xs text-slate-500">
              Ваш ответ: {{ answers[q.id].valueNumber ?? '-' }}
            </div>
          </div>

          <div v-else class="space-y-2 text-sm">
            <textarea
              v-model="answers[q.id].valueText"
              rows="3"
              class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="Ваш ответ"
            />
          </div>
        </div>

        <p v-if="error" class="text-sm text-red-600">
          {{ error }}
        </p>

        <button
          type="submit"
          class="btn-primary"
          :disabled="submitting"
        >
          Отправить ответы
        </button>
      </form>

      <div v-if="success" class="space-y-2">
        <p class="text-sm text-green-600">
          Спасибо! Ваши ответы отправлены.
        </p>
        <div v-if="basicStats" class="card space-y-2 text-sm">
          <h2 class="font-semibold">
            Краткая статистика
          </h2>
          <p class="text-xs text-slate-500">
            Количество ответов по вопросам:
          </p>
          <ul class="list-disc pl-5 space-y-1">
            <li
              v-for="stat in basicStats"
              :key="stat.question_id"
            >
              Вопрос {{
                survey.questions.findIndex((q: { id: string }) => q.id === stat.question_id) + 1
              }}: {{ stat.total_responses }} ответов
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>


