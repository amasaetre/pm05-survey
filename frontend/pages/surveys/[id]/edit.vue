<script setup lang="ts">
const route = useRoute()
const auth = useAuthStore()
const surveysStore = useSurveysStore()

const surveyId = route.params.id as string

const loading = ref(true)
const saving = ref(false)
const error = ref<string | null>(null)

type QuestionType = 'single' | 'multi' | 'scale' | 'text'

interface BuilderOption {
  id: string
  text: string
}

interface BuilderQuestion {
  id: string
  text: string
  type: QuestionType
  required: boolean
  meta: Record<string, any> | null
  options: BuilderOption[]
}

const title = ref('')
const description = ref('')
const isAnonymous = ref(true)
const questions = ref<BuilderQuestion[]>([])

const genId = () => Math.random().toString(36).slice(2)

const loadSurvey = async () => {
  loading.value = true
  try {
    const survey = await surveysStore.getSurvey(surveyId, auth.accessToken || undefined)
    title.value = survey.title
    description.value = survey.description
    isAnonymous.value = !!survey.settings?.anonymous
    questions.value = survey.questions
      .slice()
      .sort((a, b) => a.order - b.order)
      .map((q) => ({
        id: q.id,
        text: q.text,
        type: q.type,
        required: q.required,
        meta: (q.meta as any) || null,
        options: (q.options || []).map((o) => ({
          id: o.id,
          text: o.text,
        })),
      }))
  } catch (e: any) {
    error.value = e?.data?.detail || 'Не удалось загрузить опрос'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadSurvey()
})

const addQuestion = () => {
  questions.value.push({
    id: genId(),
    text: '',
    type: 'single',
    required: true,
    meta: null,
    options: [],
  })
}

const removeQuestion = (id: string) => {
  questions.value = questions.value.filter((q) => q.id !== id)
}

const moveQuestion = (index: number, dir: -1 | 1) => {
  const newIndex = index + dir
  if (newIndex < 0 || newIndex >= questions.value.length) return
  const arr = [...questions.value]
  const [item] = arr.splice(index, 1)
  arr.splice(newIndex, 0, item)
  questions.value = arr
}

const addOption = (q: BuilderQuestion) => {
  q.options.push({
    id: genId(),
    text: '',
  })
}

const removeOption = (q: BuilderQuestion, optId: string) => {
  q.options = q.options.filter((o) => o.id !== optId)
}

const onSubmit = async () => {
  error.value = null
  if (!title.value || !description.value) {
    error.value = 'Заполните заголовок и описание'
    return
  }
  if (!auth.accessToken) {
    error.value = 'Требуется авторизация'
    return
  }
  saving.value = true
  try {
    await surveysStore.updateSurvey(
      surveyId,
      {
        title: title.value,
        description: description.value,
        settings: { anonymous: isAnonymous.value },
      },
      auth.accessToken,
    )
    await loadSurvey()
  } catch (e: any) {
    error.value = e?.data?.detail || 'Ошибка сохранения opроса'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-semibold">
      Редактирование опроса
    </h1>

    <div v-if="loading" class="text-sm text-slate-500">
      Загрузка опроса...
    </div>

    <div v-else class="grid gap-6 md:grid-cols-[2fr,3fr]">
      <div class="card space-y-4">
        <div class="space-y-1">
          <label class="text-sm font-medium">Заголовок</label>
          <input
            v-model="title"
            type="text"
            class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
        </div>
        <div class="space-y-1">
          <label class="text-sm font-medium">Описание</label>
          <textarea
            v-model="description"
            rows="4"
            class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <div class="flex items-center gap-2 text-sm">
          <input
            id="anonymous"
            v-model="isAnonymous"
            type="checkbox"
            class="rounded border-slate-300 text-primary-600 focus:ring-primary-500"
          >
          <label for="anonymous">Разрешить анонимные ответы</label>
        </div>
        <p v-if="error" class="text-sm text-red-600">
          {{ error }}
        </p>
        <button
          class="btn-primary w-full"
          :disabled="saving"
          @click="onSubmit"
        >
          Сохранить изменения
        </button>
      </div>

      <div class="space-y-3">
        <div class="flex justify-between items-center">
          <h2 class="text-lg font-semibold">
            Вопросы
          </h2>
          <button class="btn-primary text-xs" type="button" @click="addQuestion">
            Добавить вопрос (UI)
          </button>
        </div>
        <div v-if="!questions.length" class="text-sm text-slate-500">
          Пока нет вопросов.
        </div>
        <div
          v-for="(q, index) in questions"
          :key="q.id"
          class="card space-y-3"
        >
          <div class="flex justify-between items-center gap-2">
            <span class="text-xs text-slate-500">
              Вопрос {{ index + 1 }}
            </span>
            <div class="flex gap-1">
              <button
                type="button"
                class="text-xs text-slate-500 hover:text-primary-600"
                @click="moveQuestion(index, -1)"
              >
                ↑
              </button>
              <button
                type="button"
                class="text-xs text-slate-500 hover:text-primary-600"
                @click="moveQuestion(index, 1)"
              >
                ↓
              </button>
              <button
                type="button"
                class="text-xs text-red-500 hover:text-red-600"
                @click="removeQuestion(q.id)"
              >
                Удалить
              </button>
            </div>
          </div>
          <div class="space-y-2">
            <input
              v-model="q.text"
              type="text"
              placeholder="Текст вопроса"
              class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
            <div class="flex gap-3 items-center text-sm">
              <select
                v-model="q.type"
                class="rounded-md border border-slate-300 px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="single">
                  Одиночный выбор
                </option>
                <option value="multi">
                  Множественный выбор
                </option>
                <option value="scale">
                  Шкала
                </option>
                <option value="text">
                  Текстовый ответ
                </option>
              </select>
              <label class="flex items-center gap-1">
                <input
                  v-model="q.required"
                  type="checkbox"
                  class="rounded border-slate-300 text-primary-600 focus:ring-primary-500"
                >
                Обязательный
              </label>
            </div>

            <div v-if="q.type === 'scale'" class="flex gap-3 text-sm">
              <div class="space-y-1">
                <label class="text-xs text-slate-500">Мин.</label>
                <input
                  v-model.number="(q.meta || (q.meta = { min: 1, max: 5 })).min"
                  type="number"
                  class="w-20 rounded-md border border-slate-300 px-2 py-1 text-sm"
                >
              </div>
              <div class="space-y-1">
                <label class="text-xs text-slate-500">Макс.</label>
                <input
                  v-model.number="(q.meta || (q.meta = { min: 1, max: 5 })).max"
                  type="number"
                  class="w-20 rounded-md border border-slate-300 px-2 py-1 text-sm"
                >
              </div>
            </div>

            <div v-if="q.type === 'single' || q.type === 'multi'" class="space-y-2">
              <div class="flex justify-between items-center text-sm">
                <span class="text-slate-600">Варианты ответа</span>
                <button
                  type="button"
                  class="text-xs text-primary-600 hover:underline"
                  @click="addOption(q)"
                >
                  Добавить вариант
                </button>
              </div>
              <div v-if="!q.options.length" class="text-xs text-slate-500">
                Пока нет вариантов.
              </div>
              <div
                v-for="opt in q.options"
                :key="opt.id"
                class="flex items-center gap-2"
              >
                <input
                  v-model="opt.text"
                  type="text"
                  placeholder="Текст варианта"
                  class="flex-1 rounded-md border border-slate-300 px-2 py-1 text-sm"
                >
                <button
                  type="button"
                  class="text-xs text-red-500 hover:text-red-600"
                  @click="removeOption(q, opt.id)"
                >
                  ✕
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


