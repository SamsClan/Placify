<template>
  <AppLayout>
    <div class="hero-section">
      <span class="hero-eyebrow">Admin dashboard</span>
      <h1>Welcome, {{ dashboard?.admin?.name || 'Admin' }}</h1>
      <p>Manage your placement ecosystem — students, companies, drives and applications, all in one place.</p>
    </div>

    <template v-if="loading">
      <SkeletonBlock height="220px" border-radius="16px" class="mb-4" />
      <div class="row g-3 mb-4">
        <div v-for="n in 4" :key="n" class="col-6 col-lg-3">
          <SkeletonBlock height="140px" border-radius="12px" />
        </div>
      </div>
    </template>

    <StateMessage
      v-else-if="error"
      type="error"
      title="Couldn't load the dashboard"
      :description="error"
    >
      <button class="btn-pp-outline" type="button" @click="fetchDashboard">
        <i class="fas fa-redo me-1" aria-hidden="true"></i>Retry
      </button>
    </StateMessage>

    <template v-else>
      <HeroCarousel :slides="carouselSlides" />

      <div class="pp-panel mb-4">
        <div class="d-flex flex-wrap justify-content-between align-items-center gap-3">
          <div>
            <h5 class="pp-panel-title mb-1"><i class="fas fa-bolt me-2" aria-hidden="true"></i>Background jobs</h5>
            <p class="text-muted small mb-0">Manually trigger scheduled jobs instead of waiting for their daily/monthly run.</p>
          </div>
          <div class="d-flex flex-wrap gap-2">
            <button class="btn-pp-outline" type="button" :disabled="reminderBusy" @click="triggerReminders">
              <i :class="reminderBusy ? 'fas fa-spinner fa-spin' : 'fas fa-bell'" aria-hidden="true"></i>
              {{ reminderBusy ? 'Sending...' : 'Send deadline reminders now' }}
            </button>
            <button class="btn-pp-outline" type="button" :disabled="reportBusy" @click="triggerReport">
              <i :class="reportBusy ? 'fas fa-spinner fa-spin' : 'fas fa-file-invoice'" aria-hidden="true"></i>
              {{ reportBusy ? 'Generating...' : 'Generate monthly report now' }}
            </button>
          </div>
        </div>
      </div>

      <div class="row g-3 mb-4">
        <div class="col-6 col-lg-3">
          <StatCard icon="fas fa-user-graduate" label="Active students" :value="stat('active_students')" />
        </div>
        <div class="col-6 col-lg-3">
          <StatCard
            icon="fas fa-building"
            label="Approved companies"
            :value="stat('approved_companies')"
            :trend="stat('pending_companies') > 0 ? `${stat('pending_companies')} pending` : ''"
            trend-type="warning"
          />
        </div>
        <div class="col-6 col-lg-3">
          <StatCard icon="fas fa-briefcase" label="Ongoing drives" :value="stat('ongoing_drives_count')" />
        </div>
        <div class="col-6 col-lg-3">
          <StatCard icon="fas fa-handshake" label="Total placements" :value="stat('total_placements')" />
        </div>
      </div>

      <RouterLink to="/admin/analytics" class="pp-panel mb-4 d-flex flex-wrap justify-content-between align-items-center gap-3 text-decoration-none analytics-cta">
        <div class="d-flex align-items-center gap-3">
          <div class="analytics-cta-icon"><i class="fas fa-chart-pie" aria-hidden="true"></i></div>
          <div>
            <h5 class="pp-panel-title mb-1">View analytics</h5>
            <p class="text-muted small mb-0">Applications, drives, monthly trends, top companies, and department breakdowns.</p>
          </div>
        </div>
        <i class="fas fa-arrow-right" style="color: var(--pp-navy-light);" aria-hidden="true"></i>
      </RouterLink>

      <div class="row g-4">
        <div class="col-lg-7">
          <div class="pp-panel h-100">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="pp-panel-title mb-0"><i class="fas fa-file-alt me-2" aria-hidden="true"></i>Recent applications</h5>
              <RouterLink to="/admin/applications" class="small fw-semibold text-decoration-none" style="color: var(--pp-navy-light)">
                View all
              </RouterLink>
            </div>

            <StateMessage
              v-if="recentApplicationsList.length === 0"
              icon="fas fa-file-alt"
              title="No applications yet"
              description="Applications will show up here as students start applying to drives."
            />
            <div v-else class="table-responsive">
              <table class="table table-modern mb-0">
                <thead>
                  <tr>
                    <th>Student</th>
                    <th>Drive</th>
                    <th>Applied on</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in recentApplicationsList" :key="item.id">
                    <td>
                      <div class="d-flex align-items-center gap-2">
                        <EntityAvatar :name="item.student_name" :size="30" />
                        <span class="fw-semibold">{{ item.student_name }}</span>
                      </div>
                    </td>
                    <td>
                      <div>{{ item.job_title }}</div>
                      <div class="text-muted small">{{ item.company_name }}</div>
                    </td>
                    <td class="text-muted small">{{ formatDate(item.application_date) }}</td>
                    <td><StatusBadge :status="item.status" /></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="col-lg-5">
          <div class="pp-panel h-100">
            <h5 class="pp-panel-title mb-3"><i class="fas fa-tasks me-2" aria-hidden="true"></i>Needs your attention</h5>

            <div v-if="attentionItems.length === 0" class="pp-state py-4">
              <i class="fas fa-check-circle" aria-hidden="true"></i>
              <p class="mb-0" style="font-size: 0.9rem;">You're all caught up. Nothing pending review.</p>
            </div>
            <div v-else class="d-flex flex-column gap-3">
              <RouterLink
                v-for="item in attentionItems"
                :key="item.label"
                :to="item.to"
                class="d-flex justify-content-between align-items-center text-decoration-none p-2 rounded-3 attention-row"
              >
                <div class="d-flex align-items-center gap-2">
                  <i :class="item.icon" style="color: var(--pp-navy); width: 20px;" aria-hidden="true"></i>
                  <span class="fw-semibold" style="color: #1c1f26; font-size: 0.9rem;">{{ item.label }}</span>
                </div>
                <span class="badge-status badge-amber">{{ item.count }}</span>
              </RouterLink>
            </div>
          </div>
        </div>
      </div>
    </template>
  </AppLayout>
</template>

<script setup>
import { computed, ref } from 'vue'
import AppLayout from '../layouts/AppLayout.vue'
import HeroCarousel from '../components/HeroCarousel.vue'
import StatCard from '../components/StatCard.vue'
import StatusBadge from '../components/StatusBadge.vue'
import EntityAvatar from '../components/EntityAvatar.vue'
import StateMessage from '../components/StateMessage.vue'
import SkeletonBlock from '../components/SkeletonBlock.vue'
import http from '../api/http'
import { useDashboard } from '../composables/useDashboard'
import { useTaskPolling } from '../composables/useTaskPolling'
import { useToast } from '../composables/useToast'

const toast = useToast()
const { loading, data: dashboard, error, recentApplications, fetchDashboard } = useDashboard('/api/v1/dashboard/admin')

const recentApplicationsList = computed(() => recentApplications.value.slice(0, 6))

const reminderBusy = ref(false)
const reportBusy = ref(false)
const reminderPolling = useTaskPolling((taskId) => `/api/v1/admin/task-status/${taskId}`)
const reportPolling = useTaskPolling((taskId) => `/api/v1/admin/task-status/${taskId}`)

async function triggerReminders() {
  reminderBusy.value = true
  try {
    const response = await http.post('/api/v1/admin/trigger-reminders')
    toast.info('Deadline reminder job queued.')
    reminderPolling.start(response.data.task_id, (err, data) => {
      reminderBusy.value = false
      if (err) {
        toast.error(err)
        return
      }
      const notified = data.result?.notified_count ?? 0
      toast.success(`Reminders sent to ${notified} student(s).`)
    })
  } catch (err) {
    reminderBusy.value = false
    const message = err?.response?.data?.message || err?.response?.data?.msg || err?.response?.data?.error || err?.message
    toast.error(message || 'Unable to queue reminder job.')
  }
}

async function triggerReport() {
  reportBusy.value = true
  try {
    const response = await http.post('/api/v1/admin/trigger-report')
    toast.info('Monthly report job queued.')
    reportPolling.start(response.data.task_id, (err) => {
      reportBusy.value = false
      if (err) {
        toast.error(err)
        return
      }
      toast.success('Monthly activity report generated and emailed to admin.')
    })
  } catch (err) {
    reportBusy.value = false
    const message = err?.response?.data?.message || err?.response?.data?.msg || err?.response?.data?.error || err?.message
    toast.error(message || 'Unable to queue report job.')
  }
}

function stat(key) {
  return dashboard.value?.stats?.[key] ?? 0
}

const attentionItems = computed(() => {
  const items = []
  if (stat('pending_companies') > 0) {
    items.push({
      label: 'Companies awaiting approval',
      count: stat('pending_companies'),
      icon: 'fas fa-building',
      to: '/admin/companies',
    })
  }
  return items
})

const carouselSlides = computed(() => [
  {
    icon: 'fas fa-users',
    title: 'Manage students',
    description: `View and manage all ${stat('total_students')} registered students. Search profiles, track placement progress, and monitor application statuses.`,
    cta: 'Manage students',
    to: '/admin/students',
  },
  {
    icon: 'fas fa-building',
    title: 'Manage companies',
    description: `Oversee all ${stat('total_companies')} registered companies. Review profiles, approve or deactivate accounts, and monitor their job postings.`,
    cta: 'Manage companies',
    to: '/admin/companies',
  },
  {
    icon: 'fas fa-briefcase',
    title: 'Placement drives',
    description: `Manage all ${stat('total_placement_drives')} placement drives. Approve or reject job postings, monitor drive timelines, and track hiring progress.`,
    cta: 'Manage drives',
    to: '/admin/drives',
  },
  {
    icon: 'fas fa-file-alt',
    title: 'Job applications',
    description: `Review all ${stat('total_job_applications')} student applications. Filter by status, track shortlisted and selected candidates, and manage outcomes.`,
    cta: 'View applications',
    to: '/admin/applications',
  },
])

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
}
</script>

<style scoped>
.attention-row {
  background: var(--pp-surface-muted);
  transition: background 0.2s ease;
}

.attention-row:hover {
  background: #eef1f5;
}

.analytics-cta {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.analytics-cta:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 32px rgba(0, 0, 0, 0.18);
}

.analytics-cta-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: var(--pp-surface-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--pp-navy);
  font-size: 1.2rem;
  flex-shrink: 0;
}
</style>
