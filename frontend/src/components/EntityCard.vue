<template>
  <div class="entity-card">
    <div class="entity-card-banner" :class="`banner-${variant}`">
      <div class="entity-card-avatar">
        <i :class="avatarIcon" aria-hidden="true"></i>
      </div>
    </div>
    <div class="entity-card-body">
      <h3 class="entity-card-name">{{ title }}</h3>
      <span class="badge-status mb-2" :class="statusBadgeClass">
        <i v-if="statusIcon" :class="statusIcon" aria-hidden="true"></i>{{ statusLabel }}
      </span>
      <ul class="entity-card-fields">
        <li v-for="field in fields" :key="field.label">
          <i :class="field.icon" aria-hidden="true"></i>{{ field.label }}
        </li>
      </ul>
    </div>
    <div v-if="$slots.actions" class="entity-card-actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  avatarIcon: { type: String, default: 'fas fa-user' },
  variant: { type: String, default: 'blue' }, // blue | red | green | amber
  statusLabel: { type: String, default: '' },
  statusBadgeClass: { type: String, default: 'badge-blue' },
  statusIcon: { type: String, default: '' },
  fields: { type: Array, default: () => [] }, // [{ icon, label }]
})
</script>

<style scoped>
.entity-card {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--pp-shadow-panel);
  display: flex;
  flex-direction: column;
  height: 100%;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.entity-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 14px 32px rgba(0, 0, 0, 0.18);
}

.entity-card-banner {
  padding: 28px 0 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.banner-blue { background: linear-gradient(135deg, #004f9d, #5295d3); }
.banner-red { background: linear-gradient(135deg, #a32d2d, #cf5c5c); }
.banner-green { background: linear-gradient(135deg, #3b6d11, #6ea62f); }
.banner-amber { background: linear-gradient(135deg, #854f0b, #c98a2e); }

.entity-card-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.22);
  border: 2px solid rgba(255, 255, 255, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 1.6rem;
}

.entity-card-body {
  padding: 18px 18px 6px;
  flex-grow: 1;
}

.entity-card-name {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--pp-navy);
  text-align: center;
  margin-bottom: 8px;
}

.entity-card-body .badge-status {
  display: flex;
  width: fit-content;
  margin: 0 auto 12px;
}

.entity-card-fields {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-top: 1px solid var(--pp-border);
  padding-top: 12px;
}

.entity-card-fields li {
  font-size: 0.84rem;
  color: #444a54;
  display: flex;
  align-items: center;
  gap: 8px;
}

.entity-card-fields i {
  color: var(--pp-navy-light);
  width: 16px;
  flex-shrink: 0;
}

.entity-card-actions {
  display: flex;
  gap: 8px;
  padding: 14px 18px 18px;
}

.entity-card-actions :deep(button),
.entity-card-actions :deep(a) {
  flex: 1;
  justify-content: center;
  font-size: 0.82rem;
  padding: 8px 10px;
}

/* Ensure primary action buttons are visible by default on cards
   - Keep hover only for visual enhancement (color change)
   - Scope to .entity-card-actions so global .btn-pp-outline stays unchanged */
.entity-card-actions :deep(.btn-pp-outline) {
  background: var(--pp-surface-muted);
  color: var(--pp-navy);
  border-color: rgba(0, 0, 0, 0.06);
}
.entity-card-actions :deep(.btn-pp-outline):hover {
  background: var(--pp-navy);
  color: #fff;
}

/* Make icon-only links/buttons inside cards clearly visible */
.entity-card-actions :deep(.btn-icon) {
  background: var(--pp-surface-muted);
  color: var(--pp-navy);
  padding: 8px;
  border-radius: 8px;
}
.entity-card-actions :deep(.btn-icon):hover {
  transform: translateY(-2px);
}
</style>
