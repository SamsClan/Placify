<template>
  <AppLayout>
    <PageHeader title="Company moderation" subtitle="Review, approve, or blacklist registered companies." back-to="/admin/dashboard" back-label="Dashboard" />

    <SkeletonBlock v-if="loading" height="260px" border-radius="16px" />

    <template v-else>
      <section class="mb-5">
        <h2 class="section-heading"><i class="fas fa-hourglass-half" aria-hidden="true"></i>Pending approval <span class="badge-status badge-amber ms-2">{{ pending.length }}</span></h2>
        <StateMessage v-if="pending.length === 0" icon="fas fa-check-circle" title="Nothing pending" description="All company registrations have been reviewed." />
        <template v-else>
          <div class="entity-grid">
            <EntityCard
              v-for="company in pending"
              :key="company.id"
              :title="company.company_name"
              avatar-icon="fas fa-building"
              variant="amber"
              status-label="Pending"
              status-badge-class="badge-amber"
              status-icon="fas fa-hourglass-half"
              :fields="companyFields(company)"
            >
              <template #actions>
                <RouterLink :to="`/admin/companies/${company.id}`" class="btn-pp-outline"><i class="fas fa-eye" aria-hidden="true"></i>View</RouterLink>
                <button class="btn-pp-primary" type="button" @click="approveCompany(company.id)"><i class="fas fa-check" aria-hidden="true"></i>Approve</button>
              </template>
            </EntityCard>
          </div>
        </template>
      </section>

      <section class="mb-5">
        <h2 class="section-heading"><i class="fas fa-building" aria-hidden="true"></i>Approved companies <span class="badge-status badge-green ms-2">{{ approved.length }}</span></h2>
        <StateMessage v-if="approved.length === 0" icon="fas fa-building" title="No approved companies yet" description="Companies you approve will show up here." />
        <template v-else>
          <div class="entity-grid">
            <EntityCard
              v-for="company in approved"
              :key="company.id"
              :title="company.company_name"
              avatar-icon="fas fa-building"
              variant="blue"
              status-label="Approved"
              status-badge-class="badge-green"
              status-icon="fas fa-check-circle"
              :fields="companyFields(company)"
            >
              <template #actions>
                <RouterLink :to="`/admin/companies/${company.id}`" class="btn-pp-outline"><i class="fas fa-eye" aria-hidden="true"></i>View</RouterLink>
                <button class="btn-pp-outline" type="button" @click="blacklistCompany(company.id)"><i class="fas fa-ban" aria-hidden="true"></i>Blacklist</button>
              </template>
            </EntityCard>
          </div>
        </template>
      </section>

      <section>
        <h2 class="section-heading"><i class="fas fa-ban" aria-hidden="true"></i>Blacklisted companies <span class="badge-status badge-red ms-2">{{ blacklisted.length }}</span></h2>
        <StateMessage v-if="blacklisted.length === 0" icon="fas fa-check-circle" title="No blacklisted companies" description="Blacklisted companies will appear here." />
        <template v-else>
          <div class="entity-grid">
            <EntityCard
              v-for="company in blacklisted"
              :key="company.id"
              :title="company.company_name"
              avatar-icon="fas fa-building"
              variant="red"
              status-label="Blacklisted"
              status-badge-class="badge-red"
              status-icon="fas fa-ban"
              :fields="companyFields(company)"
            >
              <template #actions>
                <RouterLink :to="`/admin/companies/${company.id}`" class="btn-pp-outline"><i class="fas fa-eye" aria-hidden="true"></i>View</RouterLink>
                <button class="btn-pp-outline" type="button" @click="unblacklistCompany(company.id)"><i class="fas fa-undo" aria-hidden="true"></i>Unblacklist</button>
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
const pending = ref([])
const approved = ref([])
const blacklisted = ref([])

onMounted(loadCompanies)
watch(
  () => route.query.q,
  () => {
    loadCompanies()
  }
)

async function loadCompanies() {
  loading.value = true
  try {
    const response = await http.get('/api/v1/admin/companies', {
      params: {
        q: route.query.q || undefined,
      },
    })
    pending.value = response.data.pending || []
    approved.value = response.data.approved || []
    blacklisted.value = response.data.blacklisted || []
  } finally {
    loading.value = false
  }
}

function companyFields(company) {
  const fields = [{ icon: 'fas fa-envelope', label: company.email }]
  if (company.hr_contact) fields.push({ icon: 'fas fa-id-badge', label: company.hr_contact })
  if (company.website) fields.push({ icon: 'fas fa-globe', label: company.website })
  return fields
}

async function approveCompany(companyId) {
  try {
    await http.post(`/api/v1/admin/companies/${companyId}/approve`)
    toast.success('Company approved.')
    await loadCompanies()
  } catch (error) {
    toast.error(error.response?.data?.message || 'Unable to approve company.')
  }
}

async function blacklistCompany(companyId) {
  try {
    await http.post(`/api/v1/admin/companies/${companyId}/blacklist`)
    toast.success('Company blacklisted.')
    await loadCompanies()
  } catch (error) {
    toast.error(error.response?.data?.message || 'Unable to blacklist company.')
  }
}

async function unblacklistCompany(companyId) {
  try {
    await http.post(`/api/v1/admin/companies/${companyId}/unblacklist`)
    toast.success('Company reinstated.')
    await loadCompanies()
  } catch (error) {
    toast.error(error.response?.data?.message || 'Unable to unblacklist company.')
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
