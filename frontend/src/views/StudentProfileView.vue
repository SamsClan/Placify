<template>
  <AppLayout>
    <PageHeader eyebrow="Student workspace" title="My profile" subtitle="Keep your details current so recruiters see the real you." back-to="/student/dashboard" back-label="Dashboard" />

    <SkeletonBlock v-if="loading" height="300px" border-radius="16px" />

    <div v-else class="pp-panel">
      <div class="d-flex align-items-center gap-3 mb-4">
        <EntityAvatar :name="profile.name" :size="56" />
        <div>
          <h2 class="fw-bold mb-1" style="color: var(--pp-navy);">{{ profile.name || 'Your profile' }}</h2>
          <div class="text-muted small">{{ profile.email }}</div>
        </div>
      </div>

      <form @submit.prevent="saveProfile">
        <div class="row g-3">
          <div class="col-12 col-lg-6">
            <label class="pp-form-label">Name</label>
            <input v-model="profile.name" class="form-control" required />
          </div>
          <div class="col-12 col-lg-6">
            <label class="pp-form-label">Email</label>
            <input v-model="profile.email" class="form-control" required />
          </div>
          <div class="col-12 col-lg-6">
            <label class="pp-form-label">Phone</label>
            <input v-model="profile.phone" class="form-control" />
          </div>
          <div class="col-12 col-lg-6">
            <label class="pp-form-label">Enrollment number</label>
            <input v-model="profile.enrollment_number" class="form-control" />
          </div>
          <div class="col-12 col-lg-6">
            <label class="pp-form-label">Department</label>
            <input v-model="profile.department" class="form-control" />
          </div>
          <div class="col-12 col-lg-6">
            <label class="pp-form-label">Course</label>
            <input v-model="profile.course" class="form-control" />
          </div>
          <div class="col-12 col-lg-6">
            <label class="pp-form-label">Year of study</label>
            <input v-model="profile.year_of_study" class="form-control" />
          </div>
          <div class="col-12 col-lg-6">
            <label class="pp-form-label">Skills</label>
            <input v-model="profile.skills" class="form-control" placeholder="e.g. Python, SQL, React" />
          </div>
          <div class="col-12">
            <label class="pp-form-label"><i class="fas fa-file-pdf me-1" aria-hidden="true"></i>Resume</label>
            <input type="file" class="form-control" accept=".pdf,application/pdf" @change="onResumeChange" />
            <small class="text-muted d-block mt-1">
              <template v-if="profile.resume_link">
                Current resume: <a :href="profile.resume_link" target="_blank" rel="noopener">view uploaded PDF</a> — choose a new file to replace it.
              </template>
              <template v-else>PDF only. No resume uploaded yet.</template>
            </small>
          </div>
          <div class="col-12">
            <label class="pp-form-label">Bio</label>
            <textarea v-model="profile.bio" class="form-control" rows="4"></textarea>
          </div>
        </div>
        <button class="btn-pp-primary mt-4" type="submit"><i class="fas fa-save" aria-hidden="true"></i>Save profile</button>
      </form>
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import AppLayout from '../layouts/AppLayout.vue'
import PageHeader from '../components/PageHeader.vue'
import EntityAvatar from '../components/EntityAvatar.vue'
import SkeletonBlock from '../components/SkeletonBlock.vue'
import http from '../api/http'
import { useToast } from '../composables/useToast'

const toast = useToast()
const loading = ref(true)
const profile = ref({})
const resumeFile = ref(null)

onMounted(async () => {
  loading.value = true
  try {
    const response = await http.get('/api/v1/student/profile')
    profile.value = response.data.student || {}
  } finally {
    loading.value = false
  }
})

function onResumeChange(event) {
  resumeFile.value = event.target.files?.[0] || null
}

async function saveProfile() {
  try {
    let response
    if (resumeFile.value) {
      const payload = new FormData()
      Object.entries(profile.value).forEach(([key, value]) => {
        if (value !== null && value !== undefined) payload.append(key, value)
      })
      payload.append('resume', resumeFile.value)
      response = await http.put('/api/v1/student/profile', payload, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      resumeFile.value = null
    } else {
      response = await http.put('/api/v1/student/profile', profile.value)
    }
    profile.value = response.data.student || profile.value
    toast.success(response.data.message || 'Profile updated.')
  } catch (error) {
    toast.error(error.response?.data?.message || 'Unable to save profile.')
  }
}
</script>
