<template>
  <div class="pp-avatar" :style="style">
    <img v-if="src && !imgFailed" :src="src" :alt="name" style="width:100%;height:100%;object-fit:cover" @error="imgFailed = true" />
    <span v-else>{{ initials }}</span>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  name: { type: String, default: '' },
  src: { type: String, default: '' },
  size: { type: Number, default: 40 },
  color: { type: String, default: '' },
})

const imgFailed = ref(false)

const PALETTE = ['#00264d', '#0c447c', '#3c3489', '#3b6d11', '#854f0b', '#a32d2d']

function hashColor(str) {
  let hash = 0
  for (let i = 0; i < str.length; i += 1) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash)
  }
  return PALETTE[Math.abs(hash) % PALETTE.length]
}

const initials = computed(() =>
  (props.name || '?')
    .split(' ')
    .filter(Boolean)
    .map((part) => part[0])
    .slice(0, 2)
    .join('')
    .toUpperCase(),
)

const style = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`,
  fontSize: `${Math.max(props.size * 0.36, 11)}px`,
  background: props.color || hashColor(props.name || 'x'),
}))

</script>
