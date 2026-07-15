<template>
  <AppLayout>
    <PageHeader eyebrow="Company workspace" title="Manage jobs"
      subtitle="Activate, close, or review your placement drives." back-to="/company/dashboard" back-label="Dashboard">
      <template #actions>
        <RouterLink to="/company/jobs/post" class="btn-pp-primary"><i class="fas fa-plus" aria-hidden="true"></i>Post a
          job</RouterLink>
      </template>
    </PageHeader>

    <SkeletonBlock v-if="loading" height="220px" border-radius="16px" />

    <StateMessage v-else-if="drives.length === 0" icon="fas fa-briefcase" title="No drives posted yet"
      description="Post your first placement drive to start receiving student applications.">
      <RouterLink to="/company/jobs/post" class="btn-pp-primary"><i class="fas fa-plus" aria-hidden="true"></i>Post a
        job
      </RouterLink>
    </StateMessage>

    <template v-else>
      <div class="row g-4">
        <div v-for="drive in drives" :key="drive.id" class="col-12 col-md-6 col-lg-4">
          <div class="pp-panel py-3 h-100">
            <div class="d-flex justify-content-between gap-3 mb-2">
              <div>
                <h2 class="h6 fw-bold mb-1" style="color: var(--pp-navy);">{{ drive.job_title }}</h2>
                <div class="small text-muted">Deadline: {{ formatDate(drive.deadline) }}</div>
              </div>
              <StatusBadge :status="drive.status" />
            </div>
            <div class="small text-muted mb-2" style="min-height: 48px">
              {{ drive.job_description ? (drive.job_description.length > 120 ? drive.job_description.slice(0, 120) + '...' : drive.job_description) : 'No description provided.' }}
            </div>

            <div class="d-flex gap-2">
              <template v-if="drive.approval_status && drive.approval_status.toLowerCase() === 'pending'">
                <button class="btn-pp-outline btn-sm flex-grow-1" type="button" disabled><i class="fas fa-hourglass-half me-1"></i>Pending approval</button>
              </template>
              <template v-else>
                <button class="btn-pp-outline btn-sm flex-grow-1" type="button" @click="activateDrive(drive.id)"><i class="fas fa-play me-1"></i>Activate</button>
                <button class="btn-pp-outline btn-sm flex-grow-1" type="button" @click="openEditDates(drive)"><i class="fas fa-edit me-1"></i>Edit dates</button>
                <button class="btn-pp-outline btn-sm flex-grow-1" type="button" @click="closeDrive(drive.id)"><i class="fas fa-lock me-1"></i>Close</button>
              </template>
            </div>
          </div>
        </div>
      </div>
    </template>
    <!-- Deadline modal (rendered once) -->
    <div v-if="showDeadlineModal" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.35);">
      <div class="modal-dialog modal-sm modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Set Drive Deadline</h5>
          </div>
          <div class="modal-body">
            <input type="date" v-model="pendingDeadline" class="form-control" :min="minDate" />
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-pp-outline btn-sm"
              @click="showDeadlineModal = false; pendingDriveId = null">Cancel</button>
            <button type="button" class="btn-pp-primary btn-sm" @click="confirmActivate">Activate</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showEditModal" class="modal d-block" tabindex="-1" style="background: rgba(0,0,0,0.35);">
      <div class="modal-dialog modal-sm modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Edit Drive Dates</h5>
          </div>
          <div class="modal-body">
            <label class="form-label">Start date</label>
            <input type="date" v-model="editStartDate" class="form-control mb-2" />
            <label class="form-label">Deadline</label>
            <input type="date" v-model="editDeadline" class="form-control" />
          </div>
          <div class="modal-footer">
            <button type="button" class="btn-pp-outline btn-sm" @click="closeEditModal">Cancel</button>
            <button type="button" class="btn-pp-primary btn-sm" @click="confirmEditDates">Save</button>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'

import { useRoute } from 'vue-router'
import AppLayout from '../layouts/AppLayout.vue'
import PageHeader from '../components/PageHeader.vue'
import StatusBadge from '../components/StatusBadge.vue'
import StateMessage from '../components/StateMessage.vue'
import SkeletonBlock from '../components/SkeletonBlock.vue'
import http from '../api/http'
import { useToast } from '../composables/useToast'

const route = useRoute()
const toast = useToast()
const loading = ref(true)
const drives = ref([])
const pendingDriveId = ref(null)
const pendingDeadline = ref('')
const showEditModal = ref(false)
const editDriveId = ref(null)
const editStartDate = ref('')
const editDeadline = ref('')
const minDate = new Date().toISOString().slice(0, 10)
const showDeadlineModal = ref(false)

onMounted(loadDrives)
watch(
  () => route.query.q,
  () => {
    loadDrives()
  }
)

async function loadDrives() {
  loading.value = true
  try {
    const response = await http.get('/api/v1/company/jobs', {
      params: {
        q: route.query.q || undefined,
      },
    })
    drives.value = response.data.drives || []
  } finally {
    loading.value = false
  }
}

async function activateDrive(driveId) {
  pendingDriveId.value = driveId
  pendingDeadline.value = ''
  showDeadlineModal.value = true
}

async function confirmActivate() {
  const driveId = pendingDriveId.value
  const deadline = pendingDeadline.value
  if (!deadline) {
    toast.error('Please select a deadline.')
    return
  }
  try {
    await http.post(`/api/v1/company/jobs/${driveId}/status`, { action: 'active', new_deadline: deadline })
    toast.success('Drive activated.')
    showDeadlineModal.value = false
    pendingDriveId.value = null
    await loadDrives()
  } catch (error) {
    toast.error(error.response?.data?.message || 'Unable to activate drive.')
  }
}

async function closeDrive(driveId) {
  try {
    await http.post(`/api/v1/company/jobs/${driveId}/status`, { action: 'closed' })
    toast.info('Drive closed.')
    await loadDrives()
  } catch (error) {
    toast.error(error.response?.data?.message || 'Unable to close drive.')
  }
}

function openEditDates(drive) {
  editDriveId.value = drive.id
  editStartDate.value = drive.drive_start_date ? drive.drive_start_date.slice(0, 10) : ''
  editDeadline.value = drive.deadline ? drive.deadline.slice(0, 10) : ''
  showEditModal.value = true
}

function closeEditModal() {
  showEditModal.value = false
  editDriveId.value = null
}

async function confirmEditDates() {
  const driveId = editDriveId.value
  const newStart = editStartDate.value
  const newDeadline = editDeadline.value
  if (!newStart || !newDeadline) {
    toast.error('Please provide both start date and deadline.')
    return
  }
  try {
    await http.post(`/api/v1/company/jobs/${driveId}/status`, { action: 'edit_dates', new_start_date: newStart, new_deadline_edit: newDeadline })
    toast.success('Drive dates updated.')
    closeEditModal()
    await loadDrives()
  } catch (error) {
    toast.error(error.response?.data?.message || 'Unable to update drive dates.')
  }
}

function formatDate(value) {
  return value ? new Date(value).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : 'N/A'
}
</script>
