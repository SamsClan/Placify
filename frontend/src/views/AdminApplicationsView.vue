<template>
  <AppLayout>
    <PageHeader title="Application review" subtitle="Track student applications across every stage." back-to="/admin/dashboard" back-label="Dashboard" />

    <SkeletonBlock v-if="loading" height="260px" border-radius="16px" />

    <template v-else>
      <section v-for="section in sections" :key="section.title" class="mb-5">
        <h2 class="section-heading"><i :class="section.icon" aria-hidden="true"></i>{{ section.title }} <span class="badge-status ms-2" :class="section.badgeClass">{{ section.items.length }}</span></h2>
        <StateMessage v-if="section.items.length === 0" icon="fas fa-file-alt" title="Nothing here" :description="`No ${section.title.toLowerCase()} applications.`" />
        <template v-else>
          <div class="entity-grid">
            <EntityCard
              v-for="application in section.items"
              :key="application.id"
              :title="application.student.name"
              avatar-icon="fas fa-user-graduate"
              :variant="section.variant"
              :status-label="section.title"
              :status-badge-class="section.badgeClass"
              :status-icon="section.icon"
              :fields="applicationFields(application)"
            >
              <template #actions>
                <!-- Admin users are not allowed to modify application status -->
                <button
                  v-if="section.title === 'Selected' || section.title === 'Rejected'"
                  class="btn-pp-outline"
                  type="button"
                  :disabled="updatingId === application.id"
                  @click="removeApplication(application)"
                ><i class="fas fa-trash" aria-hidden="true"></i>Remove</button>
                <button class="btn-pp-outline" type="button" @click="viewApplication(application)"><i class="fas fa-eye" aria-hidden="true"></i>View</button>
              </template>
            </EntityCard>
          </div>
        </template>
      </section>
    </template>
  </AppLayout>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '../layouts/AppLayout.vue'
import PageHeader from '../components/PageHeader.vue'
import EntityCard from '../components/EntityCard.vue'
import StateMessage from '../components/StateMessage.vue'
import SkeletonBlock from '../components/SkeletonBlock.vue'
import http from '../api/http'
import { useToast } from '../composables/useToast'

const toast = useToast()
const loading = ref(true)
const applications = ref({})
const updatingId = ref(null)
const router = useRouter()

onMounted(loadApplications)

async function loadApplications() {
  loading.value = true
  try {
    const response = await http.get('/api/v1/admin/applications')
    applications.value = response.data || {}
  } finally {
    loading.value = false
  }
}

function applicationFields(application) {
  const fields = [{ icon: 'fas fa-briefcase', label: application.drive.job_title }]
  fields.push({ icon: 'fas fa-building', label: application.drive.company_name || '' })
  if (application.application_date) {
    fields.push({ icon: 'fas fa-calendar', label: formatDate(application.application_date) })
  }
  return fields.filter((field) => field.label)
}

function formatDate(value) {
  return value ? new Date(value).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : 'N/A'
}

const statusCopy = {
  SHORTLISTED: 'shortlisted',
  SELECTED: 'selected',
  REJECTED: 'rejected',
}

// Admins are not permitted to change application status; backend enforces this.

async function removeApplication(application) {
  if (!window.confirm(`Remove ${application.student.name}'s application for ${application.drive.job_title}? This cannot be undone.`)) {
    return
  }
  updatingId.value = application.id
  try {
    await http.post(`/api/v1/admin/applications/${application.id}/delete`)
    toast.success('Application removed.')
    await loadApplications()
  } catch (error) {
    toast.error(error.response?.data?.message || 'Unable to remove application.')
  } finally {
    updatingId.value = null
  }
}

function viewApplication(application) {
  router.push(`/admin/applications/${application.id}`)
}

const sections = computed(() => [
  { title: 'Applied', icon: 'fas fa-paper-plane', badgeClass: 'badge-blue', variant: 'blue', items: applications.value.applied || [] },
  { title: 'Shortlisted', icon: 'fas fa-star', badgeClass: 'badge-amber', variant: 'amber', items: applications.value.shortlisted || [] },
  { title: 'Selected', icon: 'fas fa-check-circle', badgeClass: 'badge-green', variant: 'green', items: applications.value.selected || [] },
  { title: 'Rejected', icon: 'fas fa-times-circle', badgeClass: 'badge-red', variant: 'red', items: applications.value.rejected || [] },
])
</script>

<style scoped>
.section-heading {
  color: #ffffff;
  font-size: 1.2rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  text-shadow: 1px 1px 6px rgba(0, 0, 0, 0.3);
}

.entity-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}
</style>
