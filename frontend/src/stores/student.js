import { defineStore } from 'pinia'

export const useStudentStore = defineStore('student', {
  state: () => ({
    profile: null,
    applications: [],
    jobs: [],
    notifications: [],
    loading: false,
    error: null,
  }),
  actions: {
    setProfile(data) {
      this.profile = data
    },
    setApplications(data) {
      this.applications = data
    },
    setJobs(data) {
      this.jobs = data
    },
    setNotifications(data) {
      this.notifications = data
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
      this.applications = []
      this.jobs = []
      this.notifications = []
      this.loading = false
      this.error = null
    },
  },
})
