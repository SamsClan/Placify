<template>
  <AppLayout>
    <div class="hero-section">
      <span class="hero-eyebrow">Student dashboard</span>
      <h1>Welcome, {{ dashboard?.student?.name || auth.user?.name }}</h1>
      <p>Discover new openings, track your applications, and manage your profile.</p>
    </div>

    <template v-if="loading">
      <SkeletonBlock height="220px" border-radius="16px" class="mb-4" />
      <div class="row g-3 mb-4">
        <div v-for="n in 2" :key="n" class="col-6 col-lg-3"><SkeletonBlock height="140px" border-radius="12px" /></div>
      </div>
    </template>

    <template v-else>
      <div class="pp-panel mb-4">
        <div class="d-flex flex-wrap justify-content-between align-items-center gap-3">
          <div>
            <h5 class="pp-panel-title mb-1"><i class="fas fa-file-csv me-2" aria-hidden="true"></i>Export your applications</h5>
            <p class="text-muted small mb-0">Download your complete placement application history as a CSV file.</p>
          </div>
          <button class="btn-pp-outline" type="button" :disabled="exporting" @click="exportApplications">
            <i :class="exporting ? 'fas fa-spinner fa-spin' : 'fas fa-download'" aria-hidden="true"></i>
            {{ exporting ? 'Preparing export...' : 'Export applications as CSV' }}
          </button>
        </div>
        <div v-if="exportMessage" class="pp-form-alert pp-form-alert-info mt-3">
          <i class="fas fa-info-circle me-2" aria-hidden="true"></i>{{ exportMessage }}
          <button v-if="exportDownloadUrl" type="button" class="btn btn-link p-0 ms-2 fw-semibold" @click="downloadExport">Download CSV</button>
        </div>
      </div>

      <HeroCarousel :slides="carouselSlides" />

      
      <div class="row g-4">
        <div class="col-lg-8">
          <div class="pp-panel h-100">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="pp-panel-title mb-0"><i class="fas fa-file-alt me-2" aria-hidden="true"></i>Recent applications</h5>
              <RouterLink to="/student/applications" class="small fw-semibold text-decoration-none" style="color: var(--pp-navy-light)">View all</RouterLink>
            </div>
            <StateMessage
              v-if="recentApplicationsList.length === 0"
              icon="fas fa-file-alt"
              title="No applications yet"
              description="Browse open drives and apply to get started."
            >
              <RouterLink to="/student/jobs" class="btn-pp-primary"><i class="fas fa-search" aria-hidden="true"></i>Browse jobs</RouterLink>
            </StateMessage>
            <div v-else class="table-responsive">
              <table class="table table-modern mb-0">
                <thead><tr><th>Drive</th><th>Company</th><th>Status</th></tr></thead>
                <tbody>
                  <tr v-for="item in recentApplicationsList" :key="item.id">
                    <td class="fw-semibold">{{ item.job_title }}</td>
                    <td class="text-muted">{{ item.company_name }}</td>
                    <td><StatusBadge :status="item.status" /></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="col-lg-4">
          <div class="pp-panel h-100">
            <h5 class="pp-panel-title mb-3"><i class="fas fa-user me-2" aria-hidden="true"></i>Your profile</h5>
            <div class="d-flex flex-column gap-2 small">
              <div><i class="fas fa-envelope me-2 text-muted" aria-hidden="true"></i>{{ dashboard?.student?.email }}</div>
              <div><i class="fas fa-building-columns me-2 text-muted" aria-hidden="true"></i>{{ dashboard?.student?.department || 'Department not set' }}</div>
              <div><i class="fas fa-graduation-cap me-2 text-muted" aria-hidden="true"></i>{{ dashboard?.student?.course || 'Course not set' }}</div>
              <div><i class="fas fa-calendar me-2 text-muted" aria-hidden="true"></i>Year {{ dashboard?.student?.year_of_study || 'N/A' }}</div>
              <div><i class="fas fa-tools me-2 text-muted" aria-hidden="true"></i>{{ dashboard?.student?.skills || 'No skills added yet' }}</div>
            </div>
            <RouterLink to="/student/profile" class="btn-pp-outline btn-sm mt-3 d-inline-block">
              <i class="fas fa-pen me-1" aria-hidden="true"></i>Edit profile
            </RouterLink>
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
import StateMessage from '../components/StateMessage.vue'
import SkeletonBlock from '../components/SkeletonBlock.vue'
import { useAuthStore } from '../stores/auth'
import { useDashboard } from '../composables/useDashboard'
import { useApplicationExport } from '../composables/useApplicationExport'

const auth = useAuthStore()
const { loading, data: dashboard, recentApplications } = useDashboard('/api/v1/dashboard/student')
const { exporting, exportMessage, exportDownloadUrl, exportApplications, downloadExport } = useApplicationExport()

const recentApplicationsList = computed(() => recentApplications.value.slice(0, 6))

const carouselSlides = computed(() => [
  {
    icon: 'fas fa-search',
    title: 'Browse job openings',
    description: 'Explore placement drives from companies actively hiring students like you. Filter by skills, position, or company.',
    cta: 'Browse jobs',
    to: '/student/jobs',
  },
  {
    icon: 'fas fa-file-alt',
    title: 'Track your applications',
    description: `You have ${dashboard.value?.stats?.recent_application_count ?? 0} applications on record. Check their status and next steps.`,
    cta: 'My applications',
    to: '/student/applications',
  },
  {
    icon: 'fas fa-user',
    title: 'Complete your profile',
    description: 'A complete profile with an updated resume and skills gets noticed faster by recruiters.',
    cta: 'Edit profile',
    to: '/student/profile',
  },
  {
    icon: 'fas fa-bell',
    title: 'Stay updated',
    description: `You have ${dashboard.value?.stats?.notification_count ?? 0} notifications about your applications and drives.`,
    cta: 'View notifications',
    to: '/student/notifications',
  },
])
</script>

<style scoped>
.pp-form-alert {
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 0.86rem;
  font-weight: 600;
}
.pp-form-alert-info { background: #e6f1fb; color: #0c447c; }
</style>
