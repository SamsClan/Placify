<template>
  <AppLayout>
    <PageHeader eyebrow="Student workspace" title="Job details" back-to="/student/jobs" back-label="Jobs" />

    <SkeletonBlock v-if="loading" height="260px" border-radius="16px" />
    <StateMessage v-else-if="!drive" icon="fas fa-briefcase" title="Job not found"
      description="This drive may have been closed or removed." />

    <div v-else class="pp-panel">
      <div class="d-flex flex-wrap justify-content-between gap-3 mb-4">
        <div class="d-flex align-items-center gap-3">
          <EntityAvatar :name="drive.company_name" :size="52" />
          <div>
            <h2 class="fw-bold mb-1" style="color: var(--pp-navy);">{{ drive.job_title }}</h2>
            <div class="text-muted">{{ drive.company_name }}</div>
          </div>
        </div>
        <span v-if="hasApplied" class="badge-status badge-green"><i class="fas fa-check"
            aria-hidden="true"></i>Applied</span>
      </div>

      <div class="row g-4 mb-4">
        <div class="col-12 col-lg-7">
          <div class="pp-subpanel h-100">
            <h3 class="h6 fw-bold mb-3" style="color: var(--pp-navy);"><i class="fas fa-align-left me-2"
                aria-hidden="true"></i>Description</h3>
            <p class="text-muted mb-0">{{ drive.job_description }}</p>
          </div>
        </div>
        <div class="col-12 col-lg-5">
          <div class="pp-subpanel h-100">
            <h3 class="h6 fw-bold mb-3" style="color: var(--pp-navy);"><i class="fas fa-info-circle me-2"
                aria-hidden="true"></i>Details</h3>
            <div class="d-flex flex-column gap-2 small">
              <div><i class="fas fa-clipboard-check me-2 text-muted"
                  aria-hidden="true"></i><strong>Eligibility:</strong> {{ drive.eligibility_criteria || 'N/A' }}</div>
              <div><i class="fas fa-tools me-2 text-muted" aria-hidden="true"></i><strong>Skills:</strong>
                {{ drive.required_skills || 'N/A' }}
              </div>
              <div><i class="fas fa-briefcase me-2 text-muted" aria-hidden="true"></i><strong>Experience:</strong>
                {{ drive.experience_required || 'N/A' }}
              </div>
              <div><i class="fas fa-rupee-sign me-2 text-muted" aria-hidden="true"></i><strong>Salary:</strong>
                {{ drive.salary_range || 'N/A' }}
              </div>
              <div><i class="fas fa-calendar-times me-2 text-muted" aria-hidden="true"></i><strong>Deadline:</strong>
                {{ formatDate(drive.deadline) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="pp-subpanel">
        <h3 class="h6 fw-bold mb-3" style="color: var(--pp-navy);"><i class="fas fa-paper-plane me-2"
            aria-hidden="true"></i>Apply</h3>
        <div v-if="hasApplied">
          <div class="mb-3">
            <label class="pp-form-label">Resume</label><br>

            <a :href="application.resume_link" target="_blank" class="btn-pp-outline btn-sm">
              View Resume
            </a>
          </div>

          <div class="mb-3">
            <label class="pp-form-label">Cover Letter</label>

            <textarea class="form-control" rows="6" :value="application.cover_letter" readonly></textarea>
          </div>

          <div class="alert alert-success mb-0">
            <i class="fas fa-check-circle me-2"></i>
            You have already applied for this drive.
          </div>
        </div>

        <form v-else @submit.prevent="submitApplication" enctype="multipart/form-data">
          <!-- Existing form -->
        </form>
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
import StateMessage from '../components/StateMessage.vue'
import SkeletonBlock from '../components/SkeletonBlock.vue'
import http from '../api/http'
import { useToast } from '../composables/useToast'

const route = useRoute()
const toast = useToast()
const loading = ref(true)
const drive = ref(null)
const hasApplied = ref(false)
const form = ref({ cover_letter: '' })
const resumeFile = ref(null)
const error = ref('')
const success = ref('')
const application = ref(null)

onMounted(loadDrive)

async function loadDrive() {
  loading.value = true
  error.value = ''
  success.value = ''

  try {
    const response = await http.get(`/api/v1/student/jobs/${route.params.id}`)

    drive.value = response.data.drive
    hasApplied.value = response.data.has_applied
    application.value = response.data.application

    if (application.value) {
      form.value.cover_letter = application.value.cover_letter || ''
    }
  } catch (err) {
    console.error(err)
    drive.value = null
  } finally {
    loading.value = false
  }
}

function onResumeSelected(event) {
  resumeFile.value = event.target.files?.[0] || null
}

async function submitApplication() {
  error.value = ''
  success.value = ''

  if (!resumeFile.value) {
    error.value = 'Please upload a PDF resume from your device.'
    return
  }

  const formData = new FormData()
  formData.append('resume', resumeFile.value)
  formData.append('cover_letter', form.value.cover_letter)

  try {
    await http.post(`/api/v1/student/jobs/${route.params.id}/apply`, formData)
    success.value = 'Application submitted successfully.'
    toast.success(success.value)
    await loadDrive()
    resumeFile.value = null
  } catch (err) {
    error.value = err?.response?.data?.message || 'Unable to submit application.'
  }
}

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

.pp-form-alert {
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 0.86rem;
  font-weight: 600;
}

.pp-form-alert-error {
  background: #fcebeb;
  color: #a32d2d;
}

.pp-form-alert-success {
  background: #eaf3de;
  color: #3b6d11;
}
</style>
