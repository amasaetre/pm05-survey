export default defineNuxtConfig({
  srcDir: '.',
  typescript: {
    strict: true,
    typeCheck: false,
  },
  modules: [
    '@pinia/nuxt',
  ],
  css: [
    '~/assets/css/tailwind.css',
  ],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
    },
  },
  app: {
    head: {
      title: 'Online Surveys',
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      ],
    },
  },
  pinia: {
    autoImports: ['defineStore'],
  },
  postcss: {
    plugins: {
      tailwindcss: {},
      autoprefixer: {},
    },
  },
})


