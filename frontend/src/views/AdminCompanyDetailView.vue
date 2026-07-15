<template>
  <AppLayout>
    <PageHeader title="Company profile" back-to="/admin/companies" back-label="Companies" />

    <SkeletonBlock v-if="loading" height="260px" border-radius="16px" />
    <StateMessage
      v-else-if="!company"
      icon="fas fa-building"
      title="Company not found"
      description="This company record may have been removed."
    />

    <template v-else>
      <DetailHero :name="company.company_name" :email="company.email" id-label="Contact" :id-value="company.name || 'N/A'" avatar-icon="fas fa-building">
        <template #badge>
          <span class="badge-status badge-hero" :class="statusBadgeClass"><i :class="statusIcon" aria-hidden="true"></i>{{ company.approval_status }}</span>
        </template>
      </DetailHero>

      <InfoSection
        title="Company Information"
        icon="fas fa-building"
        :items="[
          { label: 'Contact name', value: company.name },
          { label: 'Phone', value: company.phone },
          { label: 'HR contact', value: company.hr_contact },
          { label: 'Website', value: company.website },
        ]"
      />

      <InfoSection
        title="Additional Information"
        icon="fas fa-align-left"
        :items="[{ label: 'Company bio', value: company.bio }]"
      />

      <div class="pp-panel">
        <h3 class="pp-section-title"><i class="fas fa-gears" aria-hidden="true"></i>Actions</h3>
        <div class="d-flex flex-wrap gap-2">
          <!-- Pending companies: allow Approve and Reject -->
          <template v-if="(company.approval_status || '').toString().toLowerCase() === 'pending'">
            <button class="btn-pp-primary" type="button" @click="approveCompany"><i class="fas fa-check" aria-hidden="true"></i>Approve</button>
            <button class="btn-pp-outline" type="button" @click="blacklistCompany"><i class="fas fa-times me-1" aria-hidden="true"></i>Reject</button>
          </template>

          <!-- Approved companies: allow Blacklist only -->
          <template v-else-if="(company.approval_status || '').toString().toLowerCase() === 'approved'">
            <button class="btn-pp-outline" type="button" @click="blacklistCompany"><i class="fas fa-ban me-1" aria-hidden="true"></i>Blacklist</button>
          </template>

          <!-- Blacklisted companies: allow Unblacklist only -->
          <template v-else-if="(company.approval_status || '').toString().toLowerCase() === 'blacklisted'">
            <button class="btn-pp-outline" type="button" @click="unblacklistCompany"><i class="fas fa-undo me-1" aria-hidden="true"></i>Unblacklist</button>
          </template>
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
const company = ref(null)

onMounted(loadCompany)

async function loadCompany() {
  loading.value = true
  try {
    const response = await http.get(`/api/v1/admin/companies/${route.params.id}`)
    company.value = response.data.company
  } finally {
    loading.value = false
  }
}

const statusBadgeClass = computed(() => {
  const status = (company.value?.approval_status || '').toLowerCase()
  if (status === 'approved') return 'badge-green'
  if (status === 'blacklisted') return 'badge-red'
  return 'badge-amber'
})

const statusIcon = computed(() => {
  const status = (company.value?.approval_status || '').toLowerCase()
  if (status === 'approved') return 'fas fa-check-circle'
  if (status === 'blacklisted') return 'fas fa-ban'
  return 'fas fa-hourglass-half'
})

async function approveCompany() {
  try {
    await http.post(`/api/v1/admin/companies/${route.params.id}/approve`)
    toast.success('Company approved.')
    await loadCompany()
  } catch (error) {
    toast.error(error.response?.data?.message || 'Unable to approve company.')
  }
}

async function blacklistCompany() {
  try {
    await http.post(`/api/v1/admin/companies/${route.params.id}/blacklist`)
    toast.success('Company blacklisted.')
    await loadCompany()
  } catch (error) {
    toast.error(error.response?.data?.message || 'Unable to blacklist company.')
  }
}

async function unblacklistCompany() {
  try {
    await http.post(`/api/v1/admin/companies/${route.params.id}/unblacklist`)
    toast.success('Company reinstated.')
    await loadCompany()
  } catch (error) {
    toast.error(error.response?.data?.message || 'Unable to unblacklist company.')
  }
}
</script>

<style scoped>
.badge-hero {
  font-size: 0.85rem;
  padding: 8px 16px;
}
</style>
