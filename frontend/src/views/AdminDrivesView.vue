<template>
  <AppLayout>
    <PageHeader title="Placement drives" subtitle="Track drives across every stage of the pipeline." back-to="/admin/dashboard" back-label="Dashboard" />

    <SkeletonBlock v-if="loading" height="260px" border-radius="16px" />

    <template v-else>
      <section v-for="section in sections" :key="section.title" class="mb-5">
        <h2 class="section-heading"><i :class="section.icon" aria-hidden="true"></i>{{ section.title }} <span class="badge-status ms-2" :class="section.badgeClass">{{ section.items.length }}</span></h2>
        <StateMessage v-if="section.items.length === 0" icon="fas fa-briefcase" title="Nothing here" :description="`No ${section.title.toLowerCase()} drives right now.`" />
        <template v-else>
          <div class="entity-grid">
            <EntityCard
              v-for="drive in section.items"
              :key="drive.id"
              :title="drive.job_title"
              avatar-icon="fas fa-briefcase"
              :variant="section.variant"
              :status-label="section.title"
              :status-badge-class="section.badgeClass"
              :status-icon="section.icon"
              :fields="driveFields(drive)"
            >
              <template #actions>
                <RouterLink :to="`/admin/drives/${drive.id}`" class="btn-pp-outline w-100"><i class="fas fa-eye" aria-hidden="true"></i>View details</RouterLink>
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
import AppLayout from '../layouts/AppLayout.vue'
import PageHeader from '../components/PageHeader.vue'
import EntityCard from '../components/EntityCard.vue'
import StateMessage from '../components/StateMessage.vue'
import SkeletonBlock from '../components/SkeletonBlock.vue'
import http from '../api/http'

const loading = ref(true)
const drives = ref({})
onMounted(async () => {
  try {
    const response = await http.get('/api/v1/admin/drives')
    drives.value = response.data || {}
  } finally {
    loading.value = false
  }
})

function driveFields(drive) {
  const fields = [{ icon: 'fas fa-building', label: drive.company_name }]
  if (drive.salary_range) fields.push({ icon: 'fas fa-rupee-sign', label: drive.salary_range })
  if (drive.deadline) fields.push({ icon: 'fas fa-calendar-times', label: `Deadline: ${formatDate(drive.deadline)}` })
  return fields
}

function formatDate(value) {
  return value ? new Date(value).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : 'N/A'
}

const sections = computed(() => {
  const pending = drives.value.pending || []
  const upcomingRaw = drives.value.upcoming || []
  // Exclude pending approval drives from upcoming list
  const upcoming = upcomingRaw.filter(d => {
    const status = (d.approval_status || '').toString().toLowerCase()
    return status !== 'pending' && status !== 'pending approval' && status !== 'pending_approval'
  })
  const ongoing = drives.value.ongoing || []
  const completed = drives.value.completed || []
  return [
    { title: 'Pending approval', icon: 'fas fa-hourglass-half', badgeClass: 'badge-amber', variant: 'amber', items: pending },
    { title: 'Upcoming', icon: 'fas fa-calendar-alt', badgeClass: 'badge-blue', variant: 'blue', items: upcoming },
    { title: 'Ongoing', icon: 'fas fa-spinner', badgeClass: 'badge-amber', variant: 'amber', items: ongoing },
    { title: 'Completed', icon: 'fas fa-flag-checkered', badgeClass: 'badge-green', variant: 'green', items: completed },
  ]
})
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
