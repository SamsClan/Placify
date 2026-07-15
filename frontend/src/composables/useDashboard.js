import { computed, ref, watch } from 'vue'
import http from '../api/http'

export function useDashboard(endpoint) {
  const loading = ref(true)
  const data = ref(null)
  const error = ref('')

  async function fetchDashboard() {
    loading.value = true
    error.value = ''

    try {
      const response = await http.get(endpoint)
      data.value = response.data
    } catch (err) {
      error.value = err?.response?.data?.message || 'Unable to load dashboard data.'
      throw err
    } finally {
      loading.value = false
    }
  }

  const stats = computed(() => {
    const statsData = data.value?.stats || {}
    return Object.entries(statsData).map(([label, value]) => ({
      label: label.replaceAll('_', ' '),
      value,
    }))
  })

  const recentApplications = computed(() => data.value?.recent_applications || [])

  if (endpoint) {
    watch(
      () => (typeof endpoint === 'function' ? endpoint() : endpoint),
      (value) => {
        if (value) {
          fetchDashboard()
        }
      },
      { immediate: true },
    )
  }

  return { loading, data, error, stats, recentApplications, fetchDashboard }
}
