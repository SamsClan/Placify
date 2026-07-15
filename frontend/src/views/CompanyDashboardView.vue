<template>
  <AppLayout>
    <div class="hero-section">
      <span class="hero-eyebrow">Company dashboard</span>
      <h1>{{ dashboard?.company?.company_name || 'Your company' }}</h1>
      <p>Post drives, review applicants, and track your hiring pipeline.</p>
    </div>

    <template v-if="loading">
      <SkeletonBlock height="220px" border-radius="16px" class="mb-4" />
      <div class="row g-3 mb-4">
        <div v-for="n in 4" :key="n" class="col-6 col-lg-3"><SkeletonBlock height="140px" border-radius="12px" /></div>
      </div>
    </template>

    <StateMessage v-else-if="error" type="error" title="Couldn't load the dashboard" :description="error">
      <button class="btn-pp-outline" type="button" @click="fetchDashboard">
        <i class="fas fa-redo me-1" aria-hidden="true"></i>Retry
      </button>
    </StateMessage>

    <template v-else>
      <HeroCarousel :slides="carouselSlides" />

      <div class="row g-3 mb-4">
        <div class="col-6 col-lg-3"><StatCard icon="fas fa-briefcase" label="Total drives" :value="stat('total_drives')" /></div>
        <div class="col-6 col-lg-3"><StatCard icon="fas fa-file-alt" label="Applications received" :value="stat('total_applications')" /></div>
        <div class="col-6 col-lg-3"><StatCard icon="fas fa-star" label="Shortlisted" :value="stat('shortlisted_count')" /></div>
        <div class="col-6 col-lg-3"><StatCard icon="fas fa-check-circle" label="Selected" :value="stat('selected_count')" /></div>
      </div>

      <div class="row g-4">
        <div class="col-lg-7">
          <div class="pp-panel h-100">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="pp-panel-title mb-0"><i class="fas fa-file-alt me-2" aria-hidden="true"></i>Recent applications</h5>
              <RouterLink to="/company/applications" class="small fw-semibold text-decoration-none" style="color: var(--pp-navy-light)">View all</RouterLink>
            </div>
            <StateMessage
              v-if="recentApplicationsList.length === 0"
              icon="fas fa-file-alt"
              title="No applications yet"
              description="Once students start applying to your drives, they'll show up here."
            />
            <div v-else class="table-responsive">
              <table class="table table-modern mb-0">
                <thead><tr><th>Student</th><th>Drive</th><th>Status</th></tr></thead>
                <tbody>
                  <tr v-for="item in recentApplicationsList" :key="item.id">
                    <td><div class="d-flex align-items-center gap-2"><EntityAvatar :name="item.student_name" :size="30" /><span class="fw-semibold">{{ item.student_name }}</span></div></td>
                    <td>{{ item.job_title }}</td>
                    <td><StatusBadge :status="item.status" /></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="col-lg-5">
          <div class="pp-panel h-100">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="pp-panel-title mb-0"><i class="fas fa-briefcase me-2" aria-hidden="true"></i>Your drives</h5>
              <RouterLink to="/company/jobs" class="small fw-semibold text-decoration-none" style="color: var(--pp-navy-light)">Manage</RouterLink>
            </div>
            <StateMessage
              v-if="drives.length === 0"
              icon="fas fa-briefcase"
              title="No drives posted yet"
              description="Post your first placement drive to start receiving applications."
            >
              <RouterLink to="/company/jobs/post" class="btn-pp-primary">
                <i class="fas fa-plus" aria-hidden="true"></i>Post a job
              </RouterLink>
            </StateMessage>
            <div v-else class="d-flex flex-column gap-2">
              <div v-for="item in drives" :key="item.id" class="pp-row">
                <div>
                  <div class="fw-semibold pp-row-title">{{ item.job_title }}</div>
                  <div class="text-muted small">Deadline: {{ formatDate(item.deadline) }}</div>
                </div>
                <StatusBadge :status="item.approval_status" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </AppLayout>
</template>

<script setup>
import { computed } from 'vue'
import AppLayout from '../layouts/AppLayout.vue'
import HeroCarousel from '../components/HeroCarousel.vue'
import StatCard from '../components/StatCard.vue'
import StatusBadge from '../components/StatusBadge.vue'
import EntityAvatar from '../components/EntityAvatar.vue'
import StateMessage from '../components/StateMessage.vue'
import SkeletonBlock from '../components/SkeletonBlock.vue'
import { useDashboard } from '../composables/useDashboard'

const { loading, data: dashboard, error, recentApplications, fetchDashboard } = useDashboard('/api/v1/dashboard/company')

const recentApplicationsList = computed(() => recentApplications.value.slice(0, 6))
const drives = computed(() => (dashboard.value?.drives || []).slice(0, 5))

function stat(key) {
  return dashboard.value?.stats?.[key] ?? 0
}

const carouselSlides = computed(() => [
  {
    icon: 'fas fa-plus-circle',
    title: 'Post a new drive',
    description: 'Reach qualified students by posting a new placement drive with eligibility, salary, and interview details.',
    cta: 'Post a job',
    to: '/company/jobs/post',
  },
  {
    icon: 'fas fa-briefcase',
    title: 'Manage your drives',
    description: `Track all ${stat('total_drives')} placement drives — activate, close, or review their progress.`,
    cta: 'Manage jobs',
    to: '/company/jobs',
  },
  {
    icon: 'fas fa-star',
    title: 'Shortlisted candidates',
    description: `You currently have ${stat('shortlisted_count')} shortlisted candidates awaiting your final decision.`,
    cta: 'View shortlisted',
    to: '/company/shortlisted',
  },
  {
    icon: 'fas fa-user-check',
    title: 'Selected students',
    description: `Manage offer details and joining information for your ${stat('selected_count')} selected students.`,
    cta: 'View selected',
    to: '/company/selected-students',
  },
])

function formatDate(value) {
  return value ? new Date(value).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : 'N/A'
}
</script>

<style scoped>
.pp-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--pp-surface-muted);
  border-radius: 12px;
  padding: 10px 14px;
}
.pp-row-title { color: #1c1f26; }
</style>
