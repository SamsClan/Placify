<template>
  <div class="stat-card">
    <i :class="icon" class="stat-icon" aria-hidden="true"></i>
    <div class="stat-value">{{ value }}</div>
    <div class="stat-label">{{ label }}</div>
    <div v-if="trend" class="stat-trend" :class="trendClass">
      <i v-if="trendIcon" :class="trendIcon" aria-hidden="true"></i>
      {{ trend }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  icon: { type: String, default: 'fas fa-chart-bar' },
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  trend: { type: String, default: '' },
  trendType: { type: String, default: 'neutral' }, 
})

const trendClass = computed(() => ({
  'text-success': props.trendType === 'success',
  'text-warning': props.trendType === 'warning',
  'text-danger': props.trendType === 'danger',
  'text-secondary': props.trendType === 'neutral',
}))

const trendIcon = computed(() => {
  if (props.trendType === 'success') return 'fas fa-arrow-up'
  if (props.trendType === 'danger') return 'fas fa-arrow-down'
  if (props.trendType === 'warning') return 'fas fa-clock'
  return ''
})
</script>
