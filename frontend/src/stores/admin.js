import { defineStore } from 'pinia'

export const useAdminStore = defineStore('admin', {
  state: () => ({
    dashboard: null,
    companies: [],
    students: [],
    drives: [],
    applications: [],
    loading: false,
    error: null,
  }),
  actions: {
    setDashboard(data) {
      this.dashboard = data
    },
    setCompanies(data) {
      this.companies = data
    },
    setStudents(data) {
      this.students = data
    },
    setDrives(data) {
      this.drives = data
    },
    setApplications(data) {
      this.applications = data
    },
    setLoading(value) {
      this.loading = value
    },
    setError(message) {
      this.error = message
    },
    clearError() {
      this.error = null
    },
    reset() {
      this.dashboard = null
      this.companies = []
      this.students = []
      this.drives = []
      this.applications = []
      this.loading = false
      this.error = null
    },
  },
})
