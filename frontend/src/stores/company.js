import { defineStore } from 'pinia'

export const useCompanyStore = defineStore('company', {
  state: () => ({
    profile: null,
    jobs: [],
    applications: [],
    selectedStudents: [],
    loading: false,
    error: null,
  }),
  actions: {
    setProfile(data) {
      this.profile = data
    },
    setJobs(data) {
      this.jobs = data
    },
    setApplications(data) {
      this.applications = data
    },
    setSelectedStudents(data) {
      this.selectedStudents = data
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
      this.profile = null
      this.jobs = []
      this.applications = []
      this.selectedStudents = []
      this.loading = false
      this.error = null
    },
  },
})
