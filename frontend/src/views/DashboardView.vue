<template>
  <AppLayout>
    <div class="d-flex flex-column align-items-center justify-content-center py-5 text-white">
      <i class="fas fa-circle-notch fa-spin mb-3" style="font-size: 2rem;" aria-hidden="true"></i>
      <p class="mb-0">Redirecting to your dashboard...</p>
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '../layouts/AppLayout.vue'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const ROLE_ROUTES = {
  STUDENT: '/student/dashboard',
  COMPANY: '/company/dashboard',
  ADMIN: '/admin/dashboard',
}

onMounted(() => {
  if (!auth.isAuthenticated) {
    router.replace('/login')
    return
  }
  router.replace(ROLE_ROUTES[auth.role] || '/login')
})
</script>
