<template>
  <div class="pp-toast-host">
    <transition-group name="pp-toast">
      <div v-for="toast in toasts" :key="toast.id" class="pp-toast" :class="`pp-toast-${toast.type}`">
        <i :class="iconFor(toast.type)" aria-hidden="true"></i>
        <span>{{ toast.message }}</span>
        <button type="button" aria-label="Dismiss" @click="dismiss(toast.id)">
          <i class="fas fa-times" aria-hidden="true"></i>
        </button>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { useToast } from '../composables/useToast'

const { toasts, dismiss } = useToast()

function iconFor(type) {
  if (type === 'success') return 'fas fa-check-circle'
  if (type === 'error') return 'fas fa-exclamation-circle'
  return 'fas fa-info-circle'
}
</script>

<style scoped>
.pp-toast-host {
  position: fixed;
  top: 90px;
  right: 20px;
  z-index: 2000;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 340px;
}

.pp-toast {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #ffffff;
  border-radius: 10px;
  padding: 12px 14px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
  font-size: 0.86rem;
  font-weight: 600;
}

.pp-toast-success { border-left: 4px solid #3b6d11; color: #244a0b; }
.pp-toast-error { border-left: 4px solid #a32d2d; color: #6b1f1f; }
.pp-toast-info { border-left: 4px solid #0c447c; color: #093357; }

.pp-toast i:first-child { font-size: 1rem; }

.pp-toast button {
  margin-left: auto;
  background: none;
  border: none;
  color: inherit;
  opacity: 0.6;
}

.pp-toast button:hover { opacity: 1; }

.pp-toast-enter-active,
.pp-toast-leave-active {
  transition: all 0.25s ease;
}

.pp-toast-enter-from,
.pp-toast-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>
