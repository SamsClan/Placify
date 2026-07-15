<template>
  <AppLayout>
    <PageHeader eyebrow="Student workspace" title="My applications" subtitle="Track the status of every drive you've applied to." back-to="/student/dashboard" back-label="Dashboard">
      <template #actions>
        <RouterLink to="/student/jobs" class="btn-pp-outline"><i class="fas fa-search me-1" aria-hidden="true"></i>Browse jobs</RouterLink>
      </template>
    </PageHeader>

    <div class="pp-panel mb-4 d-flex flex-wrap justify-content-between align-items-center gap-2">
      <div class="text-muted small"><i class="fas fa-file-export me-1" aria-hidden="true"></i>Export your applications as a CSV file.</div>
      <button class="btn-pp-outline btn-sm" type="button" :disabled="exporting" @click="exportApplications">
        <i class="fas fa-download me-1" aria-hidden="true"></i>{{ exporting ? 'Preparing export...' : 'Export applications' }}
      </button>
    </div>

    <div v-if="exportMessage" class="pp-form-alert pp-form-alert-info mb-3">
      <i class="fas fa-info-circle me-2" aria-hidden="true"></i>{{ exportMessage }}
      <a v-if="exportDownloadUrl" :href="exportDownloadUrl" class="ms-2 fw-semibold">Download CSV</a>
    </div>

    <SkeletonBlock v-if="loading" height="220px" border-radius="16px" />

    <StateMessage
      v-else-if="applications.length === 0"
      icon="fas fa-file-alt"
      title="No applications submitted yet"
      description="Browse open drives and apply to start tracking them here."
    >
      <RouterLink to="/student/jobs" class="btn-pp-primary"><i class="fas fa-search" aria-hidden="true"></i>Browse jobs</RouterLink>
    </StateMessage>

    <template v-else>
      <div class="row g-4">
        <div v-for="item in applications" :key="item.id" class="col-12 col-lg-6">
          <div class="pp-panel h-100">
            <div class="d-flex justify-content-between gap-3 mb-2">
              <div class="d-flex align-items-center gap-2">
                <EntityAvatar :name="item.company.company_name" :size="36" />
                <div>
                  <h2 class="h6 fw-bold mb-0" style="color: var(--pp-navy);">{{ item.drive.job_title }}</h2>
                  <div class="small text-muted">{{ item.company.company_name }}</div>
                </div>
              </div>
              <StatusBadge :status="item.status" />
            </div>
            <div class="small text-muted mb-3">
              <div><i class="fas fa-calendar me-1" aria-hidden="true"></i>Applied {{ formatDate(item.application_date) }}</div>
              <div><i class="fas fa-comment me-1" aria-hidden="true"></i>{{ item.remarks || 'N/A' }}</div>
            </div>
            <RouterLink class="btn-pp-outline btn-sm" :to="`/student/applications/${item.id}`">View details</RouterLink>
          </div>
        </div>
      </div>
    </template>
  </AppLayout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import AppLayout from '../layouts/AppLayout.vue'
import PageHeader from '../components/PageHeader.vue'
import EntityAvatar from '../components/EntityAvatar.vue'
import StatusBadge from '../components/StatusBadge.vue'
import StateMessage from '../components/StateMessage.vue'
import SkeletonBlock from '../components/SkeletonBlock.vue'
import http from '../api/http'
import { useApplicationExport } from '../composables/useApplicationExport'

const loading = ref(true)
const applications = ref([])
const { exporting, exportMessage, exportDownloadUrl, exportApplications } = useApplicationExport()

onMounted(async () => {
  try {
    const response = await http.get('/api/v1/student/applications')
    applications.value = response.data.applications || []
  } finally {
    loading.value = false
  }
})

function formatDate(value) {
  return value ? new Date(value).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : 'N/A'
}
</script>

<style scoped>
.pp-form-alert {
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 0.86rem;
  font-weight: 600;
}
.pp-form-alert-info { background: #e6f1fb; color: #0c447c; }
</style>
