<template>
  <AppLayout>
    <PageHeader eyebrow="Company workspace" title="Application review" subtitle="Update status and add remarks for applicants." back-to="/company/dashboard" back-label="Dashboard" />

    <SkeletonBlock v-if="loading" height="220px" border-radius="16px" />

    <StateMessage
      v-else-if="applications.length === 0"
      icon="fas fa-file-alt"
      title="No applications received yet"
      description="Once students apply to your drives, you can review and update their status here."
    />

    <template v-else>
      <div class="row g-4">
        <div v-for="item in applications" :key="item.id" class="col-12 col-md-6 col-lg-4">
          <div class="pp-panel application-card h-100 d-flex flex-column">
            <div class="d-flex justify-content-between gap-3 mb-2">
              <div class="d-flex align-items-center gap-2">
                <EntityAvatar :name="item.student.name" :size="32" />
                <div>
                  <h2 class="h6 fw-bold mb-0" style="color: var(--pp-navy);">{{ item.student.name }}</h2>
                  <div class="small text-muted">{{ item.drive.job_title }}</div>
                </div>
              </div>
              <StatusBadge :status="item.status" />
            </div>
            <div class="card-meta mb-3">
              <div><i class="fas fa-calendar me-1" aria-hidden="true"></i>Applied {{ formatDate(item.application_date) }}</div>
              <div class="text-truncate"><i class="fas fa-comment me-1" aria-hidden="true"></i>{{ item.remarks || 'No remarks yet' }}</div>
              <div class="meta-links mt-2">
                <a v-if="item.resume_url" :href="item.resume_url" target="_blank" rel="noopener" class="me-3 small">View resume</a>
                <a v-if="item.cover_letter_url" :href="item.cover_letter_url" target="_blank" rel="noopener" class="small">View cover letter</a>
              </div>
            </div>
            
            <!-- selection confirmation modal is rendered globally below -->
            <div class="mt-2">
              <button class="btn-pp-outline btn-sm w-100" type="button" @click="viewApplication(item.id)"><i class="fas fa-eye me-1" aria-hidden="true"></i>View</button>
      
            </div>
          </div>
        </div>
      </div>
    </template>
  </AppLayout>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '../layouts/AppLayout.vue'
import PageHeader from '../components/PageHeader.vue'
import EntityAvatar from '../components/EntityAvatar.vue'
import StatusBadge from '../components/StatusBadge.vue'
import StateMessage from '../components/StateMessage.vue'
import SkeletonBlock from '../components/SkeletonBlock.vue'
import http from '../api/http'
import { useToast } from '../composables/useToast'

const toast = useToast()
const loading = ref(true)
const applications = ref([])
const statusMap = ref({})
const remarkMap = ref({})
const router = useRouter()
const pendingSelectionId = ref(null)
const pendingJoinDateMap = ref({})
const selectedApplication = computed(() => applications.value.find(a => a.id === pendingSelectionId.value))

onMounted(loadApplications)

async function loadApplications() {
  loading.value = true
  try {
    const response = await http.get('/api/v1/company/applications')
    applications.value = response.data.applications || []
    applications.value.forEach((item) => {
      statusMap.value[item.id] = item.status
      remarkMap.value[item.id] = item.remarks || ''
    })
  } finally {
    loading.value = false
  }
}

async function updateStatus(applicationId) {
  try {
    const status = statusMap.value[applicationId]
    if (status === 'Selected') {
      // require explicit confirmation with join date
      pendingSelectionId.value = applicationId
      pendingJoinDateMap.value[applicationId] = ''
      return
    }
    await http.post(`/api/v1/company/applications/${applicationId}/status`, {
      status: statusMap.value[applicationId],
      remark: remarkMap.value[applicationId],
    })
    toast.success('Application updated.')
    await loadApplications()
  } catch (error) {
    toast.error(error.response?.data?.message || 'Unable to update application status.')
  }
}

async function confirmSelection(applicationId) {
  const join_date = pendingJoinDateMap.value[applicationId] || ''
  if (!join_date) {
    toast.error('Please choose a joining date before confirming selection.')
    return
  }
  try {
    await http.post(`/api/v1/company/applications/${applicationId}/status`, {
      status: 'Selected',
      remark: remarkMap.value[applicationId],
      join_date,
    })
    toast.success('Application marked as Selected.')
    pendingSelectionId.value = null
    await loadApplications()
  } catch (error) {
    toast.error(error.response?.data?.message || 'Unable to update application status.')
  }
}

function cancelSelection(applicationId) {
  pendingSelectionId.value = null
  pendingJoinDateMap.value[applicationId] = ''
 
  loadApplications()
}

function viewApplication(id) {
  router.push(`/company/applications/${id}`)
}

function formatDate(value) {
  return value ? new Date(value).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : 'N/A'
}
</script>

<style scoped>
.application-card {
  transition: transform 0.18s ease, box-shadow 0.18s ease;
  padding: 16px;
}
.application-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 14px 30px rgba(0, 0, 0, 0.14);
}
.application-card .card-meta {
  color: var(--pp-text-muted);
  font-size: 0.95rem;
  min-height: 56px;
}
.application-card .card-meta .text-truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.application-card .meta-links a {
  color: var(--pp-navy);
  text-decoration: none;
  font-weight: 600;
}
.application-card .meta-links a:hover {
  text-decoration: underline;
}

.application-card .view-btn { display:none; }
</style>
