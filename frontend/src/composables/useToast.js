import { reactive } from 'vue'

const state = reactive({ toasts: [] })
let counter = 0

function push(message, type = 'info') {
  const id = ++counter
  state.toasts.push({ id, message, type })
  setTimeout(() => dismiss(id), 4000)
}

function dismiss(id) {
  const index = state.toasts.findIndex((t) => t.id === id)
  if (index !== -1) state.toasts.splice(index, 1)
}

export function useToast() {
  return {
    toasts: state.toasts,
    success: (message) => push(message, 'success'),
    error: (message) => push(message, 'error'),
    info: (message) => push(message, 'info'),
    dismiss,
  }
}
