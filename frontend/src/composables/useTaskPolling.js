import { ref } from 'vue'
import http from '../api/http'


export function useTaskPolling(statusEndpoint, { intervalMs = 1500, maxAttempts = 40 } = {}) {
  const polling = ref(false)
  const status = ref('')
  const result = ref(null)
  const error = ref('')
  let timer = null

  function stop() {
    if (timer) clearTimeout(timer)
    timer = null
    polling.value = false
  }

  function start(taskId, onDone) {
    stop()
    polling.value = true
    status.value = 'Pending'
    result.value = null
    error.value = ''
    let attempts = 0

    async function poll() {
      attempts += 1
      try {
        const response = await http.get(statusEndpoint(taskId))
        status.value = response.data.status

        if (status.value === 'Completed') {
          result.value = response.data
          polling.value = false
          if (onDone) onDone(null, response.data)
          return
        }
        if (status.value === 'Failed') {
          error.value = response.data.error || 'Task failed.'
          polling.value = false
          if (onDone) onDone(error.value, response.data)
          return
        }
        if (attempts >= maxAttempts) {
          error.value = 'Task is taking longer than expected.'
          polling.value = false
          if (onDone) onDone(error.value, null)
          return
        }
        timer = setTimeout(poll, intervalMs)
      } catch (err) {
        error.value = err?.response?.data?.message || 'Unable to check task status.'
        polling.value = false
        if (onDone) onDone(error.value, null)
      }
    }

    poll()
  }

  return { polling, status, result, error, start, stop }
}
