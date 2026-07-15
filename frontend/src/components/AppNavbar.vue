<template>
  <nav class="navbar navbar-expand-lg navbar-custom">
    <div class="container-fluid px-3 px-lg-4">
      <RouterLink class="navbar-brand" :to="brandLink">
        <i class="fas fa-graduation-cap" aria-hidden="true"></i>
        Placify
      </RouterLink>

      <button
        class="navbar-toggler border-0 text-white"
        type="button"
        aria-label="Toggle navigation"
        @click="collapsed = !collapsed"
      >
        <i class="fas fa-bars" aria-hidden="true" style="color: #fff"></i>
      </button>

      <div class="collapse navbar-collapse d-lg-flex justify-content-lg-between align-items-lg-center" :class="{ show: !collapsed }">
        <ul class="navbar-nav align-items-lg-center gap-lg-1 mb-3 mb-lg-0">
          <li v-for="link in navLinks" :key="link.to" class="nav-item">
            <RouterLink class="nav-link px-3 py-2" :to="link.to">
              <i :class="link.icon" class="me-1" aria-hidden="true"></i>{{ link.label }}
            </RouterLink>
          </li>
        </ul>

        <div class="d-flex flex-column flex-lg-row align-items-stretch align-items-lg-center gap-2 gap-lg-3">
          <form v-if="auth.isAuthenticated" class="navbar-search" role="search" @submit.prevent="handleSearch">
            <i class="fas fa-search" style="opacity: 0.85" aria-hidden="true"></i>
            <input v-model="searchQuery" type="text" :placeholder="searchPlaceholder" aria-label="Search" />
            <button type="submit" aria-label="Search">
              <i class="fas fa-arrow-right" style="font-size: 0.75rem" aria-hidden="true"></i>
            </button>
          </form>

          <div v-if="auth.role === 'STUDENT'" class="dropdown">
            <a
              href="#"
              class="navbar-bell"
              role="button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
              aria-label="Notifications"
              @click.prevent="onBellOpen"
            >
              <i class="fas fa-bell" aria-hidden="true"></i>
              <span v-if="unreadCount > 0" class="notif-dot">{{ unreadCount > 9 ? '9+' : unreadCount }}</span>
            </a>
            <ul class="dropdown-menu dropdown-menu-end notification-dropdown">
              <li><h6 class="dropdown-header mb-0">Notifications</h6></li>
              <li v-if="notifLoading" class="px-3 py-2 text-muted small">Loading...</li>
              <template v-else-if="notifications.length">
                <li v-for="item in notifications.slice(0, 5)" :key="item.id">
                  <a class="dropdown-item" href="#" @click.prevent="goToNotifications">
                    <i class="fas fa-info-circle me-2 text-primary" aria-hidden="true"></i>{{ item.message }}
                  </a>
                </li>
              </template>
              <li v-else class="dropdown-item text-muted">
                <i class="fas fa-check-circle me-2 text-success" aria-hidden="true"></i>No new notifications
              </li>
              <li><hr class="dropdown-divider" /></li>
              <li>
                <RouterLink class="dropdown-item text-center fw-semibold" to="/student/notifications">
                  <i class="fas fa-eye me-1" aria-hidden="true"></i>View all
                </RouterLink>
              </li>
            </ul>
          </div>

          <div v-if="auth.isAuthenticated" class="navbar-user-pill">
            <div class="pp-avatar navbar-user-avatar" :title="auth.user?.name">
              {{ initials }}
            </div>
            <button class="btn btn-sm btn-light rounded-pill fw-semibold" type="button" @click="handleLogout">
              <i class="fas fa-sign-out-alt me-1" aria-hidden="true"></i>Logout
            </button>
          </div>
          <div v-else class="d-flex gap-2">
            <RouterLink class="nav-link auth-link px-3 py-2" to="/register">
              <i class="fas fa-user-plus me-1" aria-hidden="true"></i>Register
            </RouterLink>
            <RouterLink class="nav-link auth-link px-3 py-2" to="/login">
              <i class="fas fa-sign-in-alt me-1" aria-hidden="true"></i>Login
            </RouterLink>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useNotificationBell } from '../composables/useNotificationBell'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const collapsed = ref(true)
const searchQuery = ref('')

const { notifications, loading: notifLoading, fetchNotifications } = useNotificationBell()
const unreadCount = computed(() => notifications.value.filter((n) => n.status !== 'read').length)

let notifLoaded = false
function onBellOpen() {
  if (!notifLoaded) {
    notifLoaded = true
    fetchNotifications()
  }
}

function goToNotifications() {
  router.push('/student/notifications')
}

const brandLink = computed(() => {
  if (auth.role === 'STUDENT') return '/student/dashboard'
  if (auth.role === 'COMPANY') return '/company/dashboard'
  if (auth.role === 'ADMIN') return '/admin/dashboard'
  return '/'
})

const searchPlaceholder = computed(() => {
  if (auth.role === 'STUDENT') return 'Search jobs by title, company, or skills...'
  if (auth.role === 'COMPANY') return 'Search your placement drives...'
  if (auth.role === 'ADMIN') return 'Search companies, students, or drives...'
  return 'Search...'
})

const initials = computed(() => {
  const parts = (auth.user?.name || '').trim().split(/\s+/).filter(Boolean)
  if (parts.length === 0) return 'U'
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
})

const navLinks = computed(() => {
  if (auth.role === 'STUDENT') {
    return [
      { to: '/student/dashboard', label: 'Dashboard', icon: 'fas fa-home' },
      { to: '/student/jobs', label: 'Jobs', icon: 'fas fa-briefcase' },
      { to: '/student/applications', label: 'Applications', icon: 'fas fa-file-alt' },
      { to: '/student/profile', label: 'Profile', icon: 'fas fa-user' },
    ]
  }
  if (auth.role === 'COMPANY') {
    return [
      { to: '/company/dashboard', label: 'Dashboard', icon: 'fas fa-home' },
      { to: '/company/jobs', label: 'Jobs', icon: 'fas fa-briefcase' },
      { to: '/company/applications', label: 'Applications', icon: 'fas fa-file-alt' },
      { to: '/company/shortlisted', label: 'Shortlisted', icon: 'fas fa-star' },
      { to: '/company/selected-students', label: 'Selected', icon: 'fas fa-user-check' },
      { to: '/company/profile', label: 'Profile', icon: 'fas fa-building' },
    ]
  }
  if (auth.role === 'ADMIN') {
    return [
      { to: '/admin/dashboard', label: 'Dashboard', icon: 'fas fa-home' },
      { to: '/admin/companies', label: 'Companies', icon: 'fas fa-building' },
      { to: '/admin/students', label: 'Students', icon: 'fas fa-user-graduate' },
      { to: '/admin/drives', label: 'Drives', icon: 'fas fa-briefcase' },
      { to: '/admin/applications', label: 'Applications', icon: 'fas fa-file-alt' },
      { to: '/admin/analytics', label: 'Analytics', icon: 'fas fa-chart-pie' },
    ]
  }
  return []
})

function handleSearch() {
  const query = searchQuery.value.trim()
  if (!query) return

  // Use a unified search results page so Admin can search companies, students, and drives
  router.push({ path: '/search', query: { q: query } })
}

if (route.query.q) {
  searchQuery.value = String(route.query.q)
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>
