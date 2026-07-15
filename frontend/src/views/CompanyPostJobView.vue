<template>
  <AppLayout>
    <PageHeader eyebrow="Company workspace" title="Post a new job" subtitle="Fill in the drive details students will see." back-to="/company/jobs" back-label="Jobs" />

    <div class="pp-panel">
      <form @submit.prevent="submitJob">
        <div class="row g-3">
          <div class="col-12 col-lg-6">
            <label class="pp-form-label">Job title</label>
            <input v-model="form.job_title" class="form-control" required />
          </div>
          <div class="col-12 col-lg-6">
            <label class="pp-form-label"><i class="fas fa-rupee-sign me-1" aria-hidden="true"></i>Salary package</label>
            <input v-model="form.salary_range" class="form-control" placeholder="e.g. 8-12 LPA" />
          </div>
          <div class="col-12 col-lg-6">
            <label class="pp-form-label"><i class="fas fa-calendar-plus me-1" aria-hidden="true"></i>Drive start date</label>
            <input v-model="form.drive_start_date" class="form-control" type="date" required />
          </div>
          <div class="col-12 col-lg-6">
            <label class="pp-form-label"><i class="fas fa-calendar-times me-1" aria-hidden="true"></i>Application deadline</label>
            <input v-model="form.deadline" class="form-control" type="date" required />
          </div>
          <div class="col-12">
            <label class="pp-form-label">Job description</label>
            <textarea v-model="form.job_description" class="form-control" rows="5" required></textarea>
          </div>
          <div class="col-12">
            <label class="pp-form-label"><i class="fas fa-clipboard-check me-1" aria-hidden="true"></i>Eligibility criteria (CGPA, branch, backlogs, etc.)</label>
            <textarea v-model="form.eligibility_criteria" class="form-control" rows="3" placeholder="e.g. Minimum 7.0 CGPA, no active backlogs, CSE/IT branches"></textarea>
          </div>
          <div class="col-12 col-lg-6">
            <label class="pp-form-label">Required skills</label>
            <input v-model="form.required_skills" class="form-control" placeholder="e.g. Python, SQL, REST APIs" />
          </div>
          <div class="col-12 col-lg-6">
            <label class="pp-form-label">Experience required</label>
            <input v-model="form.experience_required" class="form-control" placeholder="e.g. Freshers welcome" />
          </div>
        </div>

        <div v-if="error" class="pp-form-alert pp-form-alert-error mt-3"><i class="fas fa-exclamation-circle me-2" aria-hidden="true"></i>{{ error }}</div>
        <div v-if="success" class="pp-form-alert pp-form-alert-success mt-3"><i class="fas fa-check-circle me-2" aria-hidden="true"></i>{{ success }}</div>

        <button class="btn-pp-primary mt-4" type="submit">
          <i class="fas fa-paper-plane" aria-hidden="true"></i>Post job
        </button>
      </form>
    </div>
  </AppLayout>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '../layouts/AppLayout.vue'
import PageHeader from '../components/PageHeader.vue'
import http from '../api/http'
import { useToast } from '../composables/useToast'

const router = useRouter()
const toast = useToast()
const form = reactive({
  job_title: '',
  job_description: '',
  eligibility_criteria: '',
  drive_start_date: '',
  deadline: '',
  required_skills: '',
  experience_required: '',
  salary_range: '',
})
const error = ref('')
const success = ref('')

async function submitJob() {
  error.value = ''
  success.value = ''
  try {
    const response = await http.post('/api/v1/company/jobs', form)
    success.value = response.data.message || 'Job posted successfully.'
    toast.success(success.value)
    router.push('/company/jobs')
  } catch (err) {
    error.value = err?.response?.data?.message || 'Unable to post job.'
  }
}
</script>

<style scoped>
.pp-form-alert {
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 0.88rem;
  font-weight: 600;
}
.pp-form-alert-error { background: #fcebeb; color: #a32d2d; }
.pp-form-alert-success { background: #eaf3de; color: #3b6d11; }
</style>
