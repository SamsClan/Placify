<template>
  <div class="pp-panel chart-card">
    <div v-if="loading" class="chart-skeleton">
      <SkeletonBlock height="220px" border-radius="10px" />
    </div>
    <img v-else-if="src" :src="`data:image/png;base64,${src}`" :alt="alt" class="chart-image" />
    <StateMessage v-else icon="fas fa-chart-bar" title="Chart unavailable" description="Not enough data to render this chart yet." />
  </div>
</template>

<script setup>
import SkeletonBlock from './SkeletonBlock.vue'
import StateMessage from './StateMessage.vue'

defineProps({
  src: { type: String, default: '' },
  alt: { type: String, default: 'Chart' },
  loading: { type: Boolean, default: false },
})
</script>

<style scoped>
.chart-card {
  padding: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-image {
  width: 100%;
  height: auto;
  max-height: 280px;
  display: block;
  border-radius: 8px;
  object-fit: contain;
}
</style>
