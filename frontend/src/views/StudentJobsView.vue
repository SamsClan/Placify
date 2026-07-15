<template>
  <AppLayout>
    <PageHeader eyebrow="Student workspace" title="Job openings" subtitle="Find and apply to placement drives that match your profile." back-to="/student/dashboard" back-label="Dashboard">
      <template #actions>
        <RouterLink to="/student/applications" class="btn-pp-outline"><i class="fas fa-file-alt me-1" aria-hidden="true"></i>My applications</RouterLink>
      </template>
    </PageHeader>

    <!-- <div class="pp-panel mb-4">
      <form class="row g-3" @submit.prevent="loadJobs">
        <div class="col-6 col-md-3">
          <label class="pp-form-label">Keyword</label>
          <input v-model="filters.q" type="search" class="form-control" placeholder="Search jobs" />
        </div>
        <div class="col-6 col-md-3">
          <label class="pp-form-label">Company</label>
          <input v-model="filters.company" type="search" class="form-control" placeholder="Company" />
        </div>
        <div class="col-6 col-md-3">
          <label class="pp-form-label">Position</label>
          <input v-model="filters.position" type="search" class="form-control" placeholder="Position" />
        </div>
        <div class="col-6 col-md-3">
          <label class="pp-form-label">Skills</label>
          <input v-model="filters.skills" type="search" class="form-control" placeholder="Skills" />
        </div>
        <div class="col-12 d-flex gap-2">
          <button class="btn-pp-primary" type="submit"><i class="fas fa-search" aria-hidden="true"></i>Search</button>
          <button class="btn-pp-outline" type="button" @click="resetFilters">Reset</button>
        </div>
      </form>
    </div> -->

    <SkeletonBlock v-if="loading" height="220px" border-radius="16px" />

    <StateMessage
      v-else-if="drives.length === 0"
      icon="fas fa-briefcase"
      title="No drives found"
      description="Try adjusting your filters, or check back soon for new openings."
    /> 

    <template v-else>
      <div class="row g-4">
        <div v-for="drive in drives" :key="drive.id" class="col-12 col-lg-6">
          <div class="pp-panel h-100 d-flex flex-column">
            <div class="d-flex justify-content-between gap-3 mb-2">
              <div class="d-flex align-items-center gap-2">
                <EntityAvatar :name="drive.company_name" :size="38" />
                <div>
                  <h2 class="h5 fw-bold mb-1" style="color: var(--pp-navy);">{{ drive.job_title }}</h2>
                  <div class="small text-muted">{{ drive.company_name }}</div>
                </div>
              </div>
              <span v-if="drive.applied" class="badge-status badge-green"><i class="fas fa-check" aria-hidden="true"></i>Applied</span>
            </div>
            <p class="text-muted small mb-3">{{ drive.job_description }}</p>
            <div class="d-flex flex-wrap gap-2 mb-3">
              <span class="badge-status badge-gray"><i class="fas fa-calendar-times me-1" aria-hidden="true"></i>{{ formatDate(drive.deadline) }}</span>
              <span v-if="drive.salary_range" class="cgpa-pill"><i class="fas fa-rupee-sign" aria-hidden="true"></i>{{ drive.salary_range }}</span>
              <span v-if="drive.required_skills" class="badge-status badge-blue"><i class="fas fa-tools me-1" aria-hidden="true"></i>{{ drive.required_skills }}</span>
            </div>
            <div class="d-flex gap-2 mt-auto">
              <button class="btn-pp-primary btn-sm" type="button" :disabled="drive.applied" @click="openApply(drive)">
                <i class="fas fa-paper-plane" aria-hidden="true"></i>{{ drive.applied ? 'Applied' : 'Apply' }}
              </button>
              <RouterLink class="btn-pp-outline btn-sm" :to="`/student/jobs/${drive.id}`">View details</RouterLink>
            </div>
          </div>
        </div>
      </div>
    </template>

    <div v-if="selectedDrive" class="pp-modal-backdrop" @click.self="closeApply">
      <div class="pp-modal-card">
        <h3 class="h5 fw-bold mb-3" style="color: var(--pp-navy);">Apply to {{ selectedDrive.job_title }}</h3>
        <form @submit.prevent="submitApplication" enctype="multipart/form-data">
          <div class="mb-3">
            <label class="pp-form-label">Resume (PDF only)</label>
            <input ref="resumeUpload" type="file" accept=".pdf" class="form-control" @change="onResumeChange" required />
          </div>
          <div class="mb-3">
            <label class="pp-form-label">Cover letter</label>
            <textarea v-model="applyForm.cover_letter" class="form-control" rows="5" required maxlength="1000"></textarea>
          </div>
          <div v-if="error" class="pp-form-alert pp-form-alert-error mb-3"><i class="fas fa-exclamation-circle me-2" aria-hidden="true"></i>{{ error }}</div>
          <div class="d-flex justify-content-end gap-2">
            <button class="btn-pp-outline" type="button" @click="closeApply">Cancel</button>
            <button class="btn-pp-primary" type="submit"><i class="fas fa-paper-plane" aria-hidden="true"></i>Submit</button>
          </div>
        </form>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '../layouts/AppLayout.vue'
import PageHeader from '../components/PageHeader.vue'
import EntityAvatar from '../components/EntityAvatar.vue'
import StateMessage from '../components/StateMessage.vue'
import SkeletonBlock from '../components/SkeletonBlock.vue'
import http from '../api/http'
import { useToast } from '../composables/useToast'

const route = useRoute()
const toast = useToast()
const loading = ref(true)
const drives = ref([])
const error = ref('')
const selectedDrive = ref(null)
const resumeFile = ref(null)
const filters = reactive({ q: '', company: '', position: '', skills: '' })
const applyForm = reactive({ cover_letter: '' })
onMounted(() => {
  if (route.query.q) filters.q = String(route.query.q)
  loadJobs()
})

watch(
  () => route.query.q,
  (q) => {
    filters.q = String(q || '')
    loadJobs()
  }
)

async function loadJobs() {
  loading.value = true
  try {
    const response = await http.get('/api/v1/student/jobs', { params: { ...filters } })
    drives.value = response.data.drives || []
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filters.q = ''
  filters.company = ''
  filters.position = ''
  filters.skills = ''
  loadJobs()
}

function openApply(drive) {
  selectedDrive.value = drive
  applyForm.cover_letter = ''
  resumeFile.value = null
  error.value = ''
}

function closeApply() {
  selectedDrive.value = null
  resumeFile.value = null
}

function onResumeChange(event) {
  resumeFile.value = event.target.files?.[0] || null
}

async function submitApplication() {
  error.value = ''
  if (!resumeFile.value) {
    error.value = 'Please upload a PDF resume from your device.'
    return
  }

  const formData = new FormData()
  formData.append('resume', resumeFile.value)
  formData.append('cover_letter', applyForm.cover_letter)

  try {
    await http.post(`/api/v1/student/jobs/${selectedDrive.value.id}/apply`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    toast.success('Application submitted.')
    closeApply()
    resumeFile.value = null
    applyForm.cover_letter = ''
    await loadJobs()
  } catch (err) {
    error.value = err?.response?.data?.message || 'Unable to submit application.'
  }
}

function formatDate(value) {
  return value ? new Date(value).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : 'N/A'
}
</script>

<style scoped>
.pp-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 20, 40, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1500;
  padding: 16px;
}
.pp-modal-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  width: 100%;
  max-width: 480px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
}
.pp-form-alert {
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 0.86rem;
  font-weight: 600;
}
.pp-form-alert-error { background: #fcebeb; color: #a32d2d; }
</style>
