<template>
  <AppLayout>
    <PageHeader eyebrow="Student workspace" title="Application details" back-to="/student/applications" back-label="Applications" />

    <SkeletonBlock v-if="loading" height="260px" border-radius="16px" />
    <StateMessage v-else-if="!application" icon="fas fa-file-alt" title="Application not found" description="This application record could not be found." />

    <div v-else class="pp-panel">
      <div class="d-flex flex-wrap align-items-center justify-content-between gap-3 mb-4">
        <div class="d-flex align-items-center gap-3">
          <EntityAvatar :name="application.company.company_name" :size="52" />
          <div>
            <h2 class="fw-bold mb-1" style="color: var(--pp-navy);">{{ application.drive.job_title }}</h2>
            <div class="text-muted">{{ application.company.company_name }}</div>
          </div>
        </div>
        <StatusBadge :status="application.status" />
      </div>

      <div class="row g-4">
        <div class="col-12 col-lg-6">
          <div class="pp-subpanel h-100">
            <h3 class="h6 fw-bold mb-3" style="color: var(--pp-navy);"><i class="fas fa-info-circle me-2" aria-hidden="true"></i>Application summary</h3>
            <div class="d-flex flex-column gap-2 small">
              <div><i class="fas fa-calendar me-2 text-muted" aria-hidden="true"></i><strong>Applied on:</strong> {{ formatDate(application.application_date) }}</div>
              <div><i class="fas fa-user me-2 text-muted" aria-hidden="true"></i><strong>Student:</strong> {{ application.student.name }}</div>
              <div><i class="fas fa-envelope me-2 text-muted" aria-hidden="true"></i><strong>Email:</strong> {{ application.student.email }}</div>
              <div><i class="fas fa-briefcase me-2 text-muted" aria-hidden="true"></i><strong>Drive status:</strong> {{ application.drive.status }}</div>
            </div>
          </div>
        </div>
        <div class="col-12 col-lg-6">
          <div class="pp-subpanel h-100">
            <h3 class="h6 fw-bold mb-3" style="color: var(--pp-navy);"><i class="fas fa-file-alt me-2" aria-hidden="true"></i>Resume &amp; cover letter</h3>
            <div class="small mb-2">
              <strong>Resume:</strong>
              <a v-if="application.resume_link" :href="application.resume_link" target="_blank" rel="noreferrer" class="ms-1">
                <i class="fas fa-external-link-alt me-1" aria-hidden="true"></i>Open resume
              </a>
              <span v-else class="text-muted">No resume link provided.</span>
            </div>
            <div class="small">
              <strong>Cover letter:</strong>
              <div class="mt-2 text-dark">{{ application.cover_letter || 'No cover letter provided.' }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="pp-subpanel mt-4">
        <h3 class="h6 fw-bold mb-2" style="color: var(--pp-navy);"><i class="fas fa-comment me-2" aria-hidden="true"></i>Company remarks</h3>
        <div class="text-muted">{{ application.remarks || 'No remarks yet.' }}</div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '../layouts/AppLayout.vue'
import PageHeader from '../components/PageHeader.vue'
import EntityAvatar from '../components/EntityAvatar.vue'
import StatusBadge from '../components/StatusBadge.vue'
import StateMessage from '../components/StateMessage.vue'
import SkeletonBlock from '../components/SkeletonBlock.vue'
import http from '../api/http'

const route = useRoute()
const loading = ref(true)
const application = ref(null)

onMounted(async () => {
  loading.value = true
  try {
    const response = await http.get(`/api/v1/student/applications/${route.params.id}`)
    application.value = response.data.application
  } finally {
    loading.value = false
  }
})

function formatDate(value) {
  return value ? new Date(value).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : 'N/A'
}
</script>

<style scoped>
.pp-subpanel {
  background: var(--pp-surface-muted);
  border-radius: 12px;
  padding: 18px;
}
</style>
