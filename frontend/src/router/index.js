import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const LoginView = () => import('../views/LoginView.vue')
const RegisterView = () => import('../views/RegisterView.vue')
const DashboardView = () => import('../views/DashboardView.vue')
const HomeView = () => import('../views/HomeView.vue')
const StudentDashboardView = () => import('../views/StudentDashboardView.vue')
const StudentJobsView = () => import('../views/StudentJobsView.vue')
const StudentApplicationsView = () => import('../views/StudentApplicationsView.vue')
const StudentApplicationDetailView = () => import('../views/StudentApplicationDetailView.vue')
const StudentJobDetailView = () => import('../views/StudentJobDetailView.vue')
const StudentProfileView = () => import('../views/StudentProfileView.vue')
const StudentNotificationsView = () => import('../views/StudentNotificationsView.vue')
const CompanyDashboardView = () => import('../views/CompanyDashboardView.vue')
const CompanyJobsView = () => import('../views/CompanyJobsView.vue')
const CompanyPostJobView = () => import('../views/CompanyPostJobView.vue')
const CompanyApplicationsView = () => import('../views/CompanyApplicationsView.vue')
const CompanyApplicationsDetailView = () => import('../views/CompanyApplicationsDetailView.vue')
const CompanyProfileView = () => import('../views/CompanyProfileView.vue')
const CompanySelectedStudentsView = () => import('../views/CompanySelectedStudentsView.vue')
const CompanyStudentDetailView = () => import('../views/CompanyStudentDetailView.vue')
const CompanyShortlistedView = () => import('../views/CompanyShortlistedView.vue')
const CompanyShortlistedDetailView = () => import('../views/CompanyShortlistedDetailView.vue')
const AdminDashboardView = () => import('../views/AdminDashboardView.vue')
const AdminAnalyticsView = () => import('../views/AdminAnalyticsView.vue')
const AdminCompaniesView = () => import('../views/AdminCompaniesView.vue')
const AdminCompanyDetailView = () => import('../views/AdminCompanyDetailView.vue')
const AdminStudentsView = () => import('../views/AdminStudentsView.vue')
const AdminStudentDetailView = () => import('../views/AdminStudentDetailView.vue')
const AdminDrivesView = () => import('../views/AdminDrivesView.vue')
const AdminDriveDetailView = () => import('../views/AdminDriveDetailView.vue')
const AdminApplicationsView = () => import('../views/AdminApplicationsView.vue')
const AdminApplicationsDetailView = () => import('../views/AdminApplicationsDetailView.vue')
const SearchResultsView = () => import('../views/SearchResultsView.vue')


const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/register', name: 'register', component: RegisterView },
  { path: '/register/student', name: 'register-student', component: RegisterView },
  { path: '/register/company', name: 'register-company', component: RegisterView },
  { path: '/dashboard', name: 'dashboard', component: DashboardView, meta: { requiresAuth: true } },
  { path: '/student/dashboard', name: 'student-dashboard', component: StudentDashboardView, meta: { requiresAuth: true, roles: ['STUDENT'] } },
  { path: '/student/jobs', name: 'student-jobs', component: StudentJobsView, meta: { requiresAuth: true, roles: ['STUDENT'] } },
  { path: '/student/applications', name: 'student-applications', component: StudentApplicationsView, meta: { requiresAuth: true, roles: ['STUDENT'] } },
  { path: '/student/applications/:id', name: 'student-application-detail', component: StudentApplicationDetailView, meta: { requiresAuth: true, roles: ['STUDENT'] } },
  { path: '/student/jobs/:id', name: 'student-job-detail', component: StudentJobDetailView, meta: { requiresAuth: true, roles: ['STUDENT'] } },
  { path: '/student/profile', name: 'student-profile', component: StudentProfileView, meta: { requiresAuth: true, roles: ['STUDENT'] } },
  { path: '/student/notifications', name: 'student-notifications', component: StudentNotificationsView, meta: { requiresAuth: true, roles: ['STUDENT'] } },
  { path: '/company/dashboard', name: 'company-dashboard', component: CompanyDashboardView, meta: { requiresAuth: true, roles: ['COMPANY'] } },
  { path: '/company/jobs', name: 'company-jobs', component: CompanyJobsView, meta: { requiresAuth: true, roles: ['COMPANY'] } },
  { path: '/company/jobs/post', name: 'company-post-job', component: CompanyPostJobView, meta: { requiresAuth: true, roles: ['COMPANY'] } },
  { path: '/company/applications', name: 'company-applications', component: CompanyApplicationsView, meta: { requiresAuth: true, roles: ['COMPANY'] } },
  { path: '/company/applications/:id', name: 'company-application-detail', component: CompanyApplicationsDetailView, meta: { requiresAuth: true, roles: ['COMPANY'] } },
  { path: '/company/profile', name: 'company-profile', component: CompanyProfileView, meta: { requiresAuth: true, roles: ['COMPANY'] } },
  { path: '/company/selected-students', name: 'company-selected-students', component: CompanySelectedStudentsView, meta: { requiresAuth: true, roles: ['COMPANY'] } },
  { path: '/company/selected-students/:id', name: 'company-selected-student-detail', component: CompanyStudentDetailView, meta: { requiresAuth: true, roles: ['COMPANY'] } },
  { path: '/company/shortlisted/:id', name: 'company-shortlisted-detail', component: CompanyShortlistedDetailView, meta: { requiresAuth: true, roles: ['COMPANY'] } },
  { path: '/company/shortlisted', name: 'company-shortlisted', component: CompanyShortlistedView, meta: { requiresAuth: true, roles: ['COMPANY'] } },
  { path: '/admin/dashboard', name: 'admin-dashboard', component: AdminDashboardView, meta: { requiresAuth: true, roles: ['ADMIN'] } },
  { path: '/admin/analytics', name: 'admin-analytics', component: AdminAnalyticsView, meta: { requiresAuth: true, roles: ['ADMIN'] } },
  { path: '/admin/companies', name: 'admin-companies', component: AdminCompaniesView, meta: { requiresAuth: true, roles: ['ADMIN'] } },
  { path: '/admin/companies/:id', name: 'admin-company-detail', component: AdminCompanyDetailView, meta: { requiresAuth: true, roles: ['ADMIN'] } },
  { path: '/admin/students', name: 'admin-students', component: AdminStudentsView, meta: { requiresAuth: true, roles: ['ADMIN'] } },
  { path: '/admin/students/:id', name: 'admin-student-detail', component: AdminStudentDetailView, meta: { requiresAuth: true, roles: ['ADMIN'] } },
  { path: '/admin/drives', name: 'admin-drives', component: AdminDrivesView, meta: { requiresAuth: true, roles: ['ADMIN'] } },
  { path: '/admin/drives/:id', name: 'admin-drive-detail', component: AdminDriveDetailView, meta: { requiresAuth: true, roles: ['ADMIN'] } },
  { path: '/admin/applications', name: 'admin-applications', component: AdminApplicationsView, meta: { requiresAuth: true, roles: ['ADMIN'] } },
  { path: '/admin/applications/:id', name: 'admin-application-detail', component: AdminApplicationsDetailView, meta: { requiresAuth: true, roles: ['ADMIN'] } },
  { path: '/search', name: 'search-results', component: SearchResultsView, meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (auth.accessToken && !auth.user) {
    return auth.restoreSession().then(() => {
      if (to.meta.requiresAuth && !auth.isAuthenticated) {
        return { name: 'login' }
      }
      return true
    })
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login' }
  }

  if (to.meta.roles && to.meta.roles.length && !to.meta.roles.includes(auth.role)) {
    return { name: 'dashboard' }
  }

  if (to.name === 'login' && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }

  return true
})

export default router
