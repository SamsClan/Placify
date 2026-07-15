<template>
  <AppLayout>
    <PageHeader eyebrow="Student workspace" title="Notifications" subtitle="Updates about your applications and drives." back-to="/student/dashboard" back-label="Dashboard">
      <template #actions>
        <button v-if="notifications.length" class="btn-pp-outline" type="button" @click="clearNotifications">
          <i class="fas fa-trash-alt me-1" aria-hidden="true"></i>Clear all
        </button>
      </template>
    </PageHeader>

    <SkeletonBlock v-if="loading" height="220px" border-radius="16px" />

    <StateMessage
      v-else-if="notifications.length === 0"
      icon="fas fa-bell-slash"
      title="No notifications yet"
      description="You'll see updates here as your applications progress."
    />

    <div v-else class="pp-panel">
      <div class="d-flex flex-column">
        <div v-for="item in notifications" :key="item.id" class="pp-notif-row">
          <i class="fas fa-info-circle" aria-hidden="true"></i>
          <div class="flex-grow-1">
            <div class="fw-semibold">{{ item.message }}</div>
            <div class="small text-muted">{{ item.status }} · {{ formatDate(item.created_at) }}</div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import AppLayout from '../layouts/AppLayout.vue'
import PageHeader from '../components/PageHeader.vue'
import StateMessage from '../components/StateMessage.vue'
import SkeletonBlock from '../components/SkeletonBlock.vue'
import http from '../api/http'
import { useToast } from '../composables/useToast'

const toast = useToast()
const loading = ref(true)
const notifications = ref([])

onMounted(loadNotifications)

async function loadNotifications() {
  loading.value = true
  try {
    const response = await http.get('/api/v1/student/notifications')
    notifications.value = response.data.notifications || []
  } finally {
    loading.value = false
  }
}

async function clearNotifications() {
  try {
    await http.post('/api/v1/student/notifications/clear')
    notifications.value = []
    toast.success('Notifications cleared.')
  } catch (error) {
    toast.error(error.response?.data?.message || 'Unable to clear notifications.')
  }
}

function formatDate(value) {
  return value ? new Date(value).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : 'N/A'
}
</script>

<style scoped>
.pp-notif-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 4px;
  border-bottom: 1px solid var(--pp-border);
}
.pp-notif-row:last-child { border-bottom: none; }
.pp-notif-row i { color: var(--pp-navy-light); margin-top: 3px; }
</style>
