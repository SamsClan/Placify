<template>
  <div class="pp-state" :class="{ 'pp-state-error': type === 'error' }">
    <i :class="resolvedIcon" aria-hidden="true"></i>
    <h5>{{ title }}</h5>
    <p class="mb-3">{{ description }}</p>
    <slot />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: { type: String, default: 'empty' }, 
  icon: { type: String, default: '' },
  title: { type: String, default: '' },
  description: { type: String, default: '' },
})

const resolvedIcon = computed(() => {
  if (props.icon) return props.icon
  return props.type === 'error' ? 'fas fa-exclamation-triangle' : 'fas fa-inbox'
})
</script>
