<template>
  <div class="pp-panel mb-4">
    <h3 class="info-section-title"><i :class="icon" aria-hidden="true"></i>{{ title }}</h3>
    <div class="row g-3">
      <div v-for="item in items" :key="item.label" class="col-12 col-md-6 col-lg-4">
        <div class="info-item">
          <span class="info-item-label">{{ item.label }}</span>
          <div class="info-item-value">{{ item.value || 'Not provided' }}</div>
        </div>
      </div>
    </div>
    <slot />
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  icon: { type: String, default: 'fas fa-info-circle' },
  items: { type: Array, default: () => [] }, // [{ label, value }]
})
</script>

<style scoped>
.info-section-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--pp-navy);
  display: flex;
  align-items: center;
  gap: 10px;
  padding-bottom: 12px;
  margin-bottom: 18px;
  border-bottom: 2px solid var(--pp-blue-light);
}

.info-item {
  border-left: 4px solid var(--pp-blue-light);
  padding: 4px 0 4px 14px;
  height: 100%;
}

.info-item-label {
  display: block;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--pp-text-muted);
  font-weight: 700;
  margin-bottom: 4px;
}

.info-item-value {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--pp-navy-light);
  word-break: break-word;
}
</style>
