<template>
  <AppLayout>
    <PageHeader title="Student profile" back-to="/admin/students" back-label="Students" />

    <SkeletonBlock v-if="loading" height="260px" border-radius="16px" />
    <StateMessage v-else-if="!student" icon="fas fa-user-graduate" title="Student not found" description="This student record may have been removed." />

    <template v-else>
      <DetailHero :name="student.name" :email="student.email" id-label="Enrollment" :id-value="student.enrollment_number || 'N/A'" avatar-icon="fas fa-graduation-cap">
        <template #badge>
          <span class="badge-status badge-hero" :class="student.is_blacklisted ? 'badge-red' : 'badge-green'">
            <i :class="student.is_blacklisted ? 'fas fa-ban' : 'fas fa-check-circle'" aria-hidden="true"></i>
            {{ student.is_blacklisted ? 'Blacklisted' : 'Active' }}
          </span>
        </template>
      </DetailHero>

      <InfoSection
        title="Personal Information"
        icon="fas fa-user"
        :items="[
          { label: 'Phone', value: student.phone },
          { label: 'Skills', value: student.skills },
        ]"
      />

      <InfoSection
        title="Academic Information"
        icon="fas fa-book"
        :items="[
          { label: 'Enrollment number', value: student.enrollment_number },
          { label: 'Department', value: student.department },
          { label: 'Course', value: student.course },
          { label: 'Year of study', value: student.year_of_study ? `Year ${student.year_of_study}` : '' },
        ]"
      />

      <InfoSection
        title="Additional Information"
        icon="fas fa-align-left"
        :items="[{ label: 'Bio', value: student.bio }]"
      />

      <div class="pp-panel">
        <h3 class="pp-section-title"><i class="fas fa-gears" aria-hidden="true"></i>Actions</h3>
        <div class="d-flex flex-wrap gap-2">
          <button class="btn-pp-outline" type="button" @click="toggleBlacklist">
            <i :class="student.is_blacklisted ? 'fas fa-undo' : 'fas fa-ban'" class="me-1" aria-hidden="true"></i>
            {{ student.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}
          </button>
        </div>
      </div>
    </template>
  </AppLayout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
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
const student = ref(null)

onMounted(loadStudent)

async function loadStudent() {
  loading.value = true
  try {
    const response = await http.get(`/api/v1/admin/students/${route.params.id}`)
    student.value = response.data.student
  } finally {
    loading.value = false
  }
}

async function toggleBlacklist() {
  try {
    await http.post(`/api/v1/admin/students/${route.params.id}/blacklist`)
    toast.success('Student status updated.')
    await loadStudent()
  } catch (error) {
    toast.error(error.response?.data?.message || 'Unable to update student.')
  }
}

async function approveStudent() {
  try {
    await http.post(`/api/v1/admin/students/${route.params.id}/approve`)
    toast.success('Student approved.')
    await loadStudent()
  } catch (error) {
    toast.error(error.response?.data?.message || 'Unable to approve student.')
  }
}

async function rejectStudent() {
  try {
    await http.post(`/api/v1/admin/students/${route.params.id}/reject`)
    toast.info('Student rejected.')
    await loadStudent()
  } catch (error) {
    toast.error(error.response?.data?.message || 'Unable to reject student.')
  }
}
</script>

<style scoped>
.badge-hero {
  font-size: 0.85rem;
  padding: 8px 16px;
}
</style>
