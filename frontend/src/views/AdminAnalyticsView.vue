<template>
  <AppLayout>
    <PageHeader
      title="Analytics"
      subtitle="Visual breakdown of applications, drives, and placement trends."
      back-to="/admin/dashboard"
      back-label="Dashboard"
    >
      <template #actions>
        <button class="btn-pp-outline" type="button" :disabled="chartsLoading" @click="loadCharts">
          <i :class="chartsLoading ? 'fas fa-spinner fa-spin' : 'fas fa-rotate'" aria-hidden="true"></i>Refresh
        </button>
      </template>
    </PageHeader>

    <div class="row g-4">
      <div class="col-12 col-lg-6">
        <ChartCard :src="charts?.applications_by_status" alt="Applications by status" :loading="chartsLoading" />
      </div>
      <div class="col-12 col-lg-6">
        <ChartCard :src="charts?.drives_by_status" alt="Drives by status" :loading="chartsLoading" />
      </div>
      <div class="col-12 col-lg-6 mx-auto">
        <ChartCard :src="charts?.monthly_trend" alt="Monthly applications and selections trend" :loading="chartsLoading" />
      </div>
      <div class="col-12 col-lg-6">
        <ChartCard :src="charts?.top_companies" alt="Top recruiting companies" :loading="chartsLoading" />
      </div>
      <div class="col-12 col-lg-6 mx-auto">
        <ChartCard :src="charts?.department_distribution" alt="Applications by department" :loading="chartsLoading" />
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import AppLayout from '../layouts/AppLayout.vue'
import PageHeader from '../components/PageHeader.vue'
import ChartCard from '../components/ChartCard.vue'
import http from '../api/http'
import { useToast } from '../composables/useToast'

const toast = useToast()
const charts = ref(null)
const chartsLoading = ref(true)

async function loadCharts() {
  chartsLoading.value = true
  try {
    const response = await http.get('/api/v1/admin/charts')
    charts.value = response.data
  } catch {
    toast.error('Unable to load analytics charts.')
  } finally {
    chartsLoading.value = false
  }
}

onMounted(loadCharts)
</script>
