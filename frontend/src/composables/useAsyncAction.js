import { ref } from 'vue'

export function useAsyncAction() {
  const loading = ref(false)
  const error = ref('')
  const success = ref('')

  async function run(request, options = {}) {
    loading.value = true
    error.value = ''
    success.value = ''

    try {
      const result = await request()
      if (options.onSuccess) {
        options.onSuccess(result)
      }
      return result
    } catch (err) {
      error.value = err?.response?.data?.message || options.fallbackMessage || 'Request failed.'
      throw err
    } finally {
      loading.value = false
    }
  }

  function reset() {
    error.value = ''
    success.value = ''
  }

  return { loading, error, success, run, reset }
}
