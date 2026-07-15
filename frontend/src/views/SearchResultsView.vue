<template>
  <AppLayout>
    <PageHeader title="Search results" :subtitle="subtitle" back-to="/dashboard" back-label="Dashboard" />

    <div class="row g-4">
      <div class="col-12">
        <SkeletonBlock v-if="loading" height="220px" border-radius="12px" />
        <div v-else>
          <section v-if="results.companies && results.companies.length" class="mb-5">
            <h2 class="section-heading"><i class="fas fa-building" aria-hidden="true"></i>Companies <span class="badge-status badge-blue ms-2">{{ results.companies.length }}</span></h2>
            <div class="entity-grid">
              <EntityCard
                v-for="c in results.companies"
                :key="c.id"
                :title="c.company_name || c.name"
                avatar-icon="fas fa-building"
                variant="blue"
                :status-label="c.approval_status"
                :status-badge-class="c.approval_status === 'Pending' ? 'badge-amber' : 'badge-green'"
                :fields="companyFields(c)"
              >
                <template #actions>
                  <RouterLink :to="companyLink(c)" class="btn-pp-outline"><i class="fas fa-eye" aria-hidden="true"></i>View</RouterLink>
                </template>
              </EntityCard>
            </div>
          </section>

          <section v-if="results.students && results.students.length" class="mb-5">
            <h2 class="section-heading"><i class="fas fa-user-graduate" aria-hidden="true"></i>Students <span class="badge-status badge-blue ms-2">{{ results.students.length }}</span></h2>
            <div class="entity-grid">
              <EntityCard
                v-for="s in results.students"
                :key="s.id"
                :title="s.name"
                avatar-icon="fas fa-graduation-cap"
                variant="blue"
                status-label=""
                status-badge-class="badge-blue"
                :fields="studentFields(s)"
              >
                <template #actions>
                  <RouterLink :to="studentLink(s)" class="btn-pp-outline"><i class="fas fa-eye" aria-hidden="true"></i>View</RouterLink>
                </template>
              </EntityCard>
            </div>
          </section>

          <section v-if="results.drives && results.drives.length" class="mb-5">
            <h2 class="section-heading"><i class="fas fa-briefcase" aria-hidden="true"></i>Placement drives <span class="badge-status badge-blue ms-2">{{ results.drives.length }}</span></h2>
            <div class="entity-grid">
              <EntityCard
                v-for="d in results.drives"
                :key="d.id"
                :title="d.job_title"
                avatar-icon="fas fa-briefcase"
                :variant="driveVariant(d)"
                :status-label="d.status"
                :status-badge-class="driveBadgeClass(d)"
                :fields="driveFields(d)"
              >
                <template #actions>
                  <RouterLink :to="driveLink(d)" class="btn-pp-outline"><i class="fas fa-eye" aria-hidden="true"></i>View</RouterLink>
                </template>
              </EntityCard>
            </div>
          </section>

          <div v-if="!results.companies?.length && !results.students?.length && !results.drives?.length" class="text-muted">No results found.</div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted, watch, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '../layouts/AppLayout.vue'
import PageHeader from '../components/PageHeader.vue'
import EntityCard from '../components/EntityCard.vue'
import SkeletonBlock from '../components/SkeletonBlock.vue'
import http from '../api/http'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const query = computed(() => String(route.query.q || ''))
const subtitle = computed(() => (query.value ? `Results for "${query.value}"` : ''))
const loading = ref(true)
const results = ref({ companies: [], students: [], drives: [] })

async function doSearch() {
  if (!query.value) {
    results.value = { companies: [], students: [], drives: [] }
    loading.value = false
    return
  }
  loading.value = true
  try {
    const resp = await http.get('/api/v1/public/search', { params: { q: query.value } })
    results.value = resp.data || { companies: [], students: [], drives: [] }
  } catch (err) {
    results.value = { companies: [], students: [], drives: [] }
  } finally {
    loading.value = false
  }
}

function companyLink(c) {
  if (auth.role === 'ADMIN') return `/admin/companies/${c.id}`
  if (auth.role === 'COMPANY') return `/company/profile`
  return `/admin/companies/${c.id}`
}

function studentLink(s) {
  if (auth.role === 'ADMIN') return `/admin/students/${s.id}`
  if (auth.role === 'COMPANY') return `/company/selected-students/${s.id}`
  return `/admin/students/${s.id}`
}

function driveLink(d) {
  if (auth.role === 'ADMIN') return `/admin/drives/${d.id}`
  if (auth.role === 'COMPANY') return `/company/jobs/${d.id}`
  return `/admin/drives/${d.id}`
}

function companyFields(company) {
  const fields = [{ icon: 'fas fa-envelope', label: company.email }]
  if (company.hr_contact) fields.push({ icon: 'fas fa-id-badge', label: company.hr_contact })
  if (company.website) fields.push({ icon: 'fas fa-globe', label: company.website })
  return fields
}

function studentFields(student) {
  const fields = [{ icon: 'fas fa-envelope', label: student.email }]
  if (student.enrollment_number) fields.push({ icon: 'fas fa-id-card', label: student.enrollment_number })
  if (student.department || student.course) fields.push({ icon: 'fas fa-book', label: [student.department, student.course].filter(Boolean).join(' - ') })
  return fields
}

function driveFields(drive) {
  const fields = [{ icon: 'fas fa-building', label: drive.company_name }]
  if (drive.deadline) fields.push({ icon: 'fas fa-calendar-alt', label: new Date(drive.deadline).toLocaleDateString() })
  if (drive.salary_range) fields.push({ icon: 'fas fa-dollar-sign', label: drive.salary_range })
  return fields
}

function driveVariant(drive) {
  const status = (drive.status || '').toLowerCase()
  if (status === 'pending' || (drive.approval_status && drive.approval_status.toLowerCase() === 'pending')) return 'amber'
  if (status === 'ongoing') return 'amber'
  if (status === 'completed') return 'green'
  return 'blue'
}

function driveBadgeClass(drive) {
  const status = (drive.status || '').toLowerCase()
  if (status === 'pending' || (drive.approval_status && drive.approval_status.toLowerCase() === 'pending')) return 'badge-amber'
  if (status === 'ongoing') return 'badge-amber'
  if (status === 'completed') return 'badge-green'
  return 'badge-blue'
}

onMounted(doSearch)
watch(() => route.query.q, doSearch)
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
