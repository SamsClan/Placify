<template>
  <AppLayout>
    <PageHeader eyebrow="Company workspace" title="Company profile" subtitle="Keep your company details up to date." back-to="/company/dashboard" back-label="Dashboard" />

    <SkeletonBlock v-if="loading" height="260px" border-radius="16px" />

    <div v-else class="pp-panel">
      <div class="d-flex align-items-center gap-3 mb-4">
        <EntityAvatar :name="profile.company_name || profile.name" :size="56" />
        <div>
          <h2 class="fw-bold mb-1" style="color: var(--pp-navy);">{{ profile.company_name || 'Your company' }}</h2>
          <div class="text-muted small">{{ profile.email }}</div>
        </div>
      </div>

      <form @submit.prevent="saveProfile">
        <div class="row g-3">
          <div class="col-12 col-lg-6">
            <label class="pp-form-label">Contact name</label>
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
            <label class="pp-form-label">Company name</label>
            <input v-model="profile.company_name" class="form-control" />
          </div>
          <div class="col-12 col-lg-6">
            <label class="pp-form-label">HR contact</label>
            <input v-model="profile.hr_contact" class="form-control" />
          </div>
          <div class="col-12 col-lg-6">
            <label class="pp-form-label">Website</label>
            <input v-model="profile.website" class="form-control" />
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

onMounted(async () => {
  loading.value = true
  try {
    const response = await http.get('/api/v1/company/profile')
    profile.value = response.data.company || {}
  } finally {
    loading.value = false
  }
})

async function saveProfile() {
  try {
    const response = await http.put('/api/v1/company/profile', profile.value)
    profile.value = response.data.company || profile.value
    toast.success(response.data.message || 'Profile updated.')
  } catch (error) {
    toast.error(error.response?.data?.message || 'Unable to save profile.')
  }
}
</script>
