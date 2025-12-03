import { defineNuxtPlugin } from '#app'
import {
  Chart,
  BarElement,
  BarController,
  CategoryScale,
  LinearScale,
  ArcElement,
  PieController,
  Tooltip,
  Legend,
} from 'chart.js'

export default defineNuxtPlugin(() => {
  Chart.register(
    BarElement,
    BarController,
    CategoryScale,
    LinearScale,
    ArcElement,
    PieController,
    Tooltip,
    Legend,
  )
})


