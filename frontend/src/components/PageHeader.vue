<template>
  <div class="d-flex flex-wrap justify-content-between align-items-end gap-3 mb-4 pp-page-header">
    <div>
      <span v-if="eyebrow" class="pp-page-eyebrow">{{ eyebrow }}</span>
      <h1 class="pp-page-title mb-0">{{ title }}</h1>
      <p v-if="subtitle" class="pp-page-subtitle mb-0">{{ subtitle }}</p>
    </div>
    <div class="d-flex flex-wrap gap-2">
      <RouterLink v-if="backTo" :to="backTo" class="btn-pp-outline">
        <i class="fas fa-arrow-left me-1" aria-hidden="true"></i>{{ backLabel }}
      </RouterLink>
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  eyebrow: { type: String, default: 'Admin workspace' },
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  backTo: { type: String, default: '' },
  backLabel: { type: String, default: 'Back' },
})
</script>

<style scoped>
.pp-page-eyebrow {
  display: inline-block;
  color: rgba(255, 255, 255, 0.75);
  font-size: 0.7rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-weight: 700;
  margin-bottom: 4px;
}

.pp-page-title {
  font-size: 1.6rem;
  font-weight: 800;
  color: #ffffff;
  text-shadow: 1px 1px 6px rgba(0, 0, 0, 0.3);
}

.pp-page-subtitle {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
}
</style>
