<template>
  <div class="detail-hero">
    <div class="detail-hero-avatar">
      <i :class="avatarIcon" aria-hidden="true"></i>
    </div>
    <div class="detail-hero-info">
      <h2 class="detail-hero-name">{{ name }}</h2>
      <div v-if="email" class="detail-hero-line"><i class="fas fa-envelope" aria-hidden="true"></i>{{ email }}</div>
      <div v-if="idLabel" class="detail-hero-line"><i class="fas fa-id-badge" aria-hidden="true"></i>{{ idLabel }}: {{ idValue }}</div>
    </div>
    <div v-if="$slots.badge" class="detail-hero-badge"><slot name="badge" /></div>
  </div>
</template>

<script setup>
defineProps({
  name: { type: String, required: true },
  email: { type: String, default: '' },
  idLabel: { type: String, default: '' },
  idValue: { type: String, default: '' },
  avatarIcon: { type: String, default: 'fas fa-user' },
})
</script>

<style scoped>
.detail-hero {
  background: linear-gradient(90deg, #00498d, #5295d3);
  border-radius: 16px;
  padding: 28px 32px;
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
  margin-bottom: 24px;
  box-shadow: 0 10px 30px rgba(0, 38, 77, 0.25);
}

.detail-hero-avatar {
  width: 90px;
  height: 90px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 2.4rem;
  flex-shrink: 0;
}

.detail-hero-info {
  flex-grow: 1;
  color: #fff;
}

.detail-hero-name {
  font-size: 1.9rem;
  font-weight: 800;
  margin-bottom: 8px;
}

.detail-hero-line {
  font-size: 0.92rem;
  color: rgba(255, 255, 255, 0.92);
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.detail-hero-badge {
  flex-shrink: 0;
}

@media (max-width: 576px) {
  .detail-hero {
    flex-direction: column;
    text-align: center;
    padding: 24px 20px;
  }
  .detail-hero-line {
    justify-content: center;
  }
}
</style>
