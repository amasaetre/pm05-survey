import { defineStore } from 'pinia'

interface Option {
  id: string
  text: string
  order: number
}

type QuestionType = 'single' | 'multi' | 'scale' | 'text'

interface Question {
  id: string
  text: string
  type: QuestionType
  required: boolean
  order: number
  meta?: Record<string, any> | null
  options: Option[]
}

interface Survey {
  id: string
  title: string
  description: string
  is_published: boolean
  created_at: string
  owner_id: string
  settings?: Record<string, any> | null
  questions: Question[]
}

interface SurveysState {
  items: Survey[]
  loading: boolean
}

export const useSurveysStore = defineStore('surveys', {
  state: (): SurveysState => ({
    items: [],
    loading: false,
  }),
  actions: {
    async fetchPublicSurveys() {
      const config = useRuntimeConfig()
      this.loading = true
      try {
        const data = await $fetch<Survey[]>(`${config.public.apiBase}/api/v1/surveys`, {
          query: { published: true },
        })
        this.items = data
      } finally {
        this.loading = false
      }
    },
    async fetchMySurveys(accessToken: string, userId?: string) {
      const config = useRuntimeConfig()
      this.loading = true
      try {
        let ownerId = userId
        if (!ownerId) {
          const me = await $fetch<{ id: string }>(`${config.public.apiBase}/api/v1/auth/me`, {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          })
          ownerId = me.id
        }
        const data = await $fetch<Survey[]>(`${config.public.apiBase}/api/v1/surveys`, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
          query: {
            owner_id: ownerId,
          },
        })
        this.items = data
      } finally {
        this.loading = false
      }
    },
    async createSurvey(payload: {
      title: string
      description: string
      settings?: Record<string, any> | null
      questions: Array<{
        text: string
        type: QuestionType
        required: boolean
        order: number
        meta?: Record<string, any> | null
        options?: Array<{ text: string; order: number }>
      }>
    }, accessToken: string) {
      const config = useRuntimeConfig()
      const survey = await $fetch<Survey>(`${config.public.apiBase}/api/v1/surveys`, {
        method: 'POST',
        body: payload,
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      })
      this.items.unshift(survey)
      return survey
    },
    async getSurvey(id: string, accessToken?: string) {
      const config = useRuntimeConfig()
      const survey = await $fetch<Survey>(`${config.public.apiBase}/api/v1/surveys/${id}`, {
        headers: accessToken
          ? { Authorization: `Bearer ${accessToken}` }
          : undefined,
      })
      return survey
    },
    async updateSurvey(id: string, payload: Partial<Pick<Survey, 'title' | 'description' | 'settings' | 'is_published'>>, accessToken: string) {
      const config = useRuntimeConfig()
      const survey = await $fetch<Survey>(`${config.public.apiBase}/api/v1/surveys/${id}`, {
        method: 'PUT',
        body: payload,
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      })
      return survey
    },
    async togglePublish(id: string, accessToken: string) {
      const config = useRuntimeConfig()
      const survey = await $fetch<Survey>(`${config.public.apiBase}/api/v1/surveys/${id}/publish`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      })
      const index = this.items.findIndex((s) => s.id === id)
      if (index !== -1) {
        this.items[index] = survey
      }
      return survey
    },
  },
})


