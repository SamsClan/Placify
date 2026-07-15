<template>
  <AppLayout>
    <PageHeader title="Drive profile" back-to="/admin/drives" back-label="Drives" />

    <SkeletonBlock v-if="loading" height="260px" border-radius="16px" />
    <StateMessage v-else-if="!drive" icon="fas fa-briefcase" title="Drive not found" description="This placement drive may have been removed." />

    <template v-else>
      <DetailHero :name="drive.job_title" :email="drive.company_name" id-label="Status" :id-value="drive.status || 'N/A'" avatar-icon="fas fa-briefcase">
        <template #badge>
          <span class="badge-status badge-hero" :class="statusBadgeClass"><i :class="statusIcon" aria-hidden="true"></i>{{ drive.approval_status }}</span>
        </template>
      </DetailHero>

      <div class="pp-panel mb-4">
        <h3 class="pp-section-title"><i class="fas fa-align-left" aria-hidden="true"></i>Description</h3>
        <p class="mb-0 text-muted">{{ drive.job_description }}</p>
      </div>

      <InfoSection
        title="Drive Details"
        icon="fas fa-clipboard-list"
        :items="[
          { label: 'Eligibility criteria', value: drive.eligibility_criteria },
          { label: 'Required skills', value: drive.required_skills },
          { label: 'Experience required', value: drive.experience_required },
          { label: 'Salary package', value: drive.salary_range },
          { label: 'Drive start date', value: formatDate(drive.drive_start_date) },
          { label: 'Application deadline', value: formatDate(drive.deadline) },
        ]"
      />

      <div class="pp-panel">
        <h3 class="pp-section-title"><i class="fas fa-gears" aria-hidden="true"></i>Actions</h3>
        <div class="d-flex flex-wrap gap-2">
          <button class="btn-pp-primary" type="button" @click="approveDrive"><i class="fas fa-check" aria-hidden="true"></i>Approve</button>
          <button class="btn-pp-outline" type="button" @click="rejectDrive"><i class="fas fa-times me-1" aria-hidden="true"></i>Reject</button>
        </div>
      </div>
    </template>
  </AppLayout>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '../layouts/AppLayout.vue'
import PageHeader from '../components/PageHeader.vue'
import DetailHero from '../components/DetailHero.vue'
import InfoSection from '../components/InfoSection.vue'
import StateMessage from '../components/StateMessage.vue'
import SkeletonBlock from '../components/SkeletonBlock.vue'
import http from '../api/http'
import { useToast } from '../composables/useToast'

const route = useRoute()
const toast = useToast()
const loading = ref(true)
const drive = ref(null)

onMounted(loadDrive)

async function loadDrive() {
  loading.value = true
  try {
    const response = await http.get(`/api/v1/admin/drives/${route.params.id}`)
    drive.value = response.data.drive
  } finally {
    loading.value = false
  }
}

const statusBadgeClass = computed(() => {
  const status = (drive.value?.approval_status || '').toLowerCase()
  if (status === 'approved') return 'badge-green'
  if (status === 'rejected') return 'badge-red'
  return 'badge-amber'
})

const statusIcon = computed(() => {
  const status = (drive.value?.approval_status || '').toLowerCase()
  if (status === 'approved') return 'fas fa-check-circle'
  if (status === 'rejected') return 'fas fa-times-circle'
  return 'fas fa-hourglass-half'
})

async function approveDrive() {
  try {
    await http.post(`/api/v1/admin/drives/${route.params.id}/approve`)
    toast.success('Drive approved.')
    await loadDrive()
  } catch (error) {
    toast.error(error.response?.data?.message || 'Unable to approve drive.')
  }
}

async function rejectDrive() {
  try {
    await http.post(`/api/v1/admin/drives/${route.params.id}/reject`)
    toast.info('Drive rejected.')
    await loadDrive()
  } catch (error) {
    toast.error(error.response?.data?.message || 'Unable to reject drive.')
  }
}

function formatDate(value) {
  return value ? new Date(value).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : 'N/A'
}
</script>

<style scoped>
.badge-hero {
  font-size: 0.85rem;
  padding: 8px 16px;
}
</style>
