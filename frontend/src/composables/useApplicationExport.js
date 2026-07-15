import { ref } from 'vue'
import http from '../api/http'
import { useTaskPolling } from './useTaskPolling'
import { useToast } from './useToast'

export function useApplicationExport() {
  const toast = useToast()
  const exporting = ref(false)
  const exportMessage = ref('')
  const exportDownloadUrl = ref('')

  const { start } = useTaskPolling((taskId) => `/api/v1/student/export-status/${taskId}`)

  async function exportApplications() {
    exporting.value = true
    exportMessage.value = 'Starting export...'
    exportDownloadUrl.value = ''

    try {
      const response = await http.post('/api/v1/student/export-applications')

      if (response.data.status === 'Completed') {
        exporting.value = false
        exportMessage.value = response.data.message || 'Export completed. Your CSV is ready to download.'
        exportDownloadUrl.value = response.data.download_url || ''
        toast.success('Your application export is ready.')
        return
      }

      exportMessage.value = 'Export queued. Please wait...'

      start(response.data.task_id, (err, data) => {
        exporting.value = false
        if (err) {
          exportMessage.value = err
          toast.error(err)
          return
        }
        exportMessage.value = 'Export completed. Your CSV is ready to download.'
        exportDownloadUrl.value = data.download_url || ''
        toast.success('Your application export is ready.')
      })
    } catch (error) {
      exporting.value = false
      exportMessage.value = error.response?.data?.message || 'Unable to start export.'
      toast.error(exportMessage.value)
    }
  }

  async function downloadExport() {
  if (!exportDownloadUrl.value) return

  try {
    const response = await http.get(exportDownloadUrl.value, {
      responseType: 'blob',
    })

    const blob = new Blob([response.data], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)

    const link = document.createElement('a')
    link.href = url
    link.download = 'applications.csv'
    document.body.appendChild(link)
    link.click()

    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    toast.error('Unable to download export.')
  }
}
  return { exporting, exportMessage, exportDownloadUrl, exportApplications, downloadExport }
}
