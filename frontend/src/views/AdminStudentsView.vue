<template>
  <AppLayout>
    <PageHeader title="Student moderation" subtitle="Manage student accounts across the portal." back-to="/admin/dashboard" back-label="Dashboard" />

    <SkeletonBlock v-if="loading" height="260px" border-radius="16px" />

    <template v-else>
      <section class="mb-5">
        <h2 class="section-heading"><i class="fas fa-user-graduate" aria-hidden="true"></i>Active students <span class="badge-status badge-green ms-2">{{ active.length }}</span></h2>
        <StateMessage v-if="active.length === 0" icon="fas fa-user-graduate" title="No active students" description="Active student accounts will show up here." />
        <template v-else>
          <div class="entity-grid">
            <EntityCard
              v-for="student in active"
              :key="student.id"
              :title="student.name"
              avatar-icon="fas fa-graduation-cap"
              variant="blue"
              status-label="Active"
              status-badge-class="badge-green"
              status-icon="fas fa-check-circle"
              :fields="studentFields(student)"
            >
              <template #actions>
                <RouterLink :to="`/admin/students/${student.id}`" class="btn-pp-outline"><i class="fas fa-eye" aria-hidden="true"></i>View</RouterLink>
                <button class="btn-pp-outline" type="button" @click="toggleBlacklist(student.id)"><i class="fas fa-ban" aria-hidden="true"></i>Blacklist</button>
              </template>
            </EntityCard>
          </div>
        </template>
      </section>

      <section>
        <h2 class="section-heading"><i class="fas fa-user-slash" aria-hidden="true"></i>Blacklisted students <span class="badge-status badge-red ms-2">{{ blacklisted.length }}</span></h2>
        <StateMessage v-if="blacklisted.length === 0" icon="fas fa-check-circle" title="No blacklisted students" description="Blacklisted accounts will appear here." />
        <template v-else>
          <div class="entity-grid">
            <EntityCard
              v-for="student in blacklisted"
              :key="student.id"
              :title="student.name"
              avatar-icon="fas fa-user-slash"
              variant="red"
              status-label="Blacklisted"
              status-badge-class="badge-red"
              status-icon="fas fa-ban"
              :fields="studentFields(student)"
            >
              <template #actions>
                <RouterLink :to="`/admin/students/${student.id}`" class="btn-pp-outline"><i class="fas fa-eye" aria-hidden="true"></i>View</RouterLink>
                <button class="btn-pp-outline" type="button" @click="toggleBlacklist(student.id)"><i class="fas fa-undo" aria-hidden="true"></i>Unblacklist</button>
              </template>
            </EntityCard>
          </div>
        </template>
      </section>
    </template>
  </AppLayout>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '../layouts/AppLayout.vue'
import PageHeader from '../components/PageHeader.vue'
import EntityCard from '../components/EntityCard.vue'
import StateMessage from '../components/StateMessage.vue'
import SkeletonBlock from '../components/SkeletonBlock.vue'
import http from '../api/http'
import { useToast } from '../composables/useToast'

const route = useRoute()
const toast = useToast()
const loading = ref(true)
const active = ref([])
const blacklisted = ref([])

const activePage = null
const blacklistedPage = null

onMounted(loadStudents)
watch(
  () => route.query.q,
  () => {
    loadStudents()
  }
)

async function loadStudents() {
  loading.value = true
  try {
    const response = await http.get('/api/v1/admin/students', {
      params: {
        q: route.query.q || undefined,
      },
    })
    active.value = response.data.active || []
    blacklisted.value = response.data.blacklisted || []
  } finally {
    loading.value = false
  }
}

function studentFields(student) {
  const fields = [{ icon: 'fas fa-envelope', label: student.email }]
  if (student.enrollment_number) fields.push({ icon: 'fas fa-id-card', label: student.enrollment_number })
  if (student.department || student.course) {
    fields.push({ icon: 'fas fa-book', label: [student.department, student.course].filter(Boolean).join(' - ') })
  }
  if (student.year_of_study) fields.push({ icon: 'fas fa-graduation-cap', label: `Year ${student.year_of_study}` })
  return fields
}

async function toggleBlacklist(studentId) {
  try {
    await http.post(`/api/v1/admin/students/${studentId}/blacklist`)
    toast.success('Student status updated.')
    await loadStudents()
  } catch (error) {
    toast.error(error.response?.data?.message || 'Unable to update student status.')
  }
}
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
