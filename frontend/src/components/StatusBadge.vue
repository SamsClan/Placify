<template>
  <span class="badge-status" :class="colorClass">
    <i v-if="icon" :class="icon" aria-hidden="true"></i>{{ label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, required: true },
})

const MAP = {
  applied: { color: 'badge-blue', icon: 'fas fa-paper-plane' },
  shortlisted: { color: 'badge-amber', icon: 'fas fa-star' },
  selected: { color: 'badge-green', icon: 'fas fa-check-circle' },
  rejected: { color: 'badge-red', icon: 'fas fa-times-circle' },
  pending: { color: 'badge-amber', icon: 'fas fa-hourglass-half' },
  approved: { color: 'badge-green', icon: 'fas fa-check-circle' },
  blacklisted: { color: 'badge-red', icon: 'fas fa-ban' },
  upcoming: { color: 'badge-blue', icon: 'fas fa-calendar-alt' },
  ongoing: { color: 'badge-amber', icon: 'fas fa-spinner' },
  completed: { color: 'badge-green', icon: 'fas fa-flag-checkered' },
}

const key = computed(() => (props.status || '').toLowerCase())
const colorClass = computed(() => MAP[key.value]?.color || 'badge-gray')
const icon = computed(() => MAP[key.value]?.icon || '')
const label = computed(() => props.status)
</script>
