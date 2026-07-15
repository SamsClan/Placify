import { ref } from 'vue'
import http from '../api/http'

export function useNotificationBell() {
  const notifications = ref([])
  const loading = ref(false)

  async function fetchNotifications() {
    loading.value = true
    try {
      const response = await http.get('/api/v1/student/notifications')
      notifications.value = response.data.notifications || []
    } catch {
      notifications.value = []
    } finally {
      loading.value = false
    }
  }

  return { notifications, loading, fetchNotifications }
}
