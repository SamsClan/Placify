<template>
  <div class="pp-skeleton" :style="{ height, width, borderRadius }"></div>
</template>

<script setup>
defineProps({
  height: { type: String, default: '1rem' },
  width: { type: String, default: '100%' },
  borderRadius: { type: String, default: '' },
})
</script>
