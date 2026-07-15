<template>
  <nav v-if="totalPages > 1" class="pp-pagination" aria-label="Pagination">
    <button
      class="pp-page-btn pp-page-nav"
      type="button"
      :disabled="currentPage === 1"
      aria-label="Previous page"
      @click="$emit('update:currentPage', currentPage - 1)"
    >
      <i class="fas fa-chevron-left" aria-hidden="true"></i>
    </button>

    <button
      v-for="page in pages"
      :key="page"
      class="pp-page-btn"
      :class="{ active: page === currentPage, ellipsis: page === '...' }"
      type="button"
      :disabled="page === '...'"
      @click="page !== '...' && $emit('update:currentPage', page)"
    >
      {{ page }}
    </button>

    <button
      class="pp-page-btn pp-page-nav"
      type="button"
      :disabled="currentPage === totalPages"
      aria-label="Next page"
      @click="$emit('update:currentPage', currentPage + 1)"
    >
      <i class="fas fa-chevron-right" aria-hidden="true"></i>
    </button>
  </nav>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentPage: { type: Number, required: true },
  totalPages: { type: Number, required: true },
})

defineEmits(['update:currentPage'])

// Builds a compact page list like: 1 ... 4 5 [6] 7 8 ... 20
const pages = computed(() => {
  const total = props.totalPages
  const current = props.currentPage
  const delta = 1
  const range = []

  for (let i = 1; i <= total; i += 1) {
    if (i === 1 || i === total || (i >= current - delta && i <= current + delta)) {
      range.push(i)
    }
  }

  const withEllipsis = []
  let prev = 0
  for (const page of range) {
    if (prev && page - prev > 1) withEllipsis.push('...')
    withEllipsis.push(page)
    prev = page
  }
  return withEllipsis
})
</script>

<style scoped>
.pp-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 20px;
  flex-wrap: wrap;
}

.pp-page-btn {
  min-width: 36px;
  height: 36px;
  padding: 0 10px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.25);
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
  font-weight: 600;
  font-size: 0.85rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.pp-page-btn:hover:not(:disabled):not(.active) {
  background: rgba(255, 255, 255, 0.2);
}

.pp-page-btn:disabled {
  opacity: 0.4;
  cursor: default;
}

.pp-page-btn.ellipsis {
  border: none;
  background: transparent;
}
</style>
