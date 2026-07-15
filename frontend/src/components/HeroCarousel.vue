<template>
  <div class="carousel-wrap mb-4">
    <div class="carousel-slide-box position-relative overflow-hidden">
      <div
        class="carousel-track"
        :style="{ transform: `translateX(-${active * 100}%)` }"
      >
        <div v-for="slide in slides" :key="slide.title" class="carousel-slide-content">
          <i :class="slide.icon" class="carousel-icon" aria-hidden="true"></i>
          <div class="flex-grow-1">
            <h2>{{ slide.title }}</h2>
            <p>{{ slide.description }}</p>
            <RouterLink :to="slide.to" class="btn-pp-primary">
              <i class="fas fa-arrow-right" aria-hidden="true"></i>{{ slide.cta }}
            </RouterLink>
          </div>
        </div>
      </div>

      <button
        v-if="slides.length > 1"
        class="carousel-nav-btn carousel-nav-prev"
        type="button"
        aria-label="Previous"
        @click="prev"
      >
        <i class="fas fa-chevron-left" aria-hidden="true"></i>
      </button>
      <button
        v-if="slides.length > 1"
        class="carousel-nav-btn carousel-nav-next"
        type="button"
        aria-label="Next"
        @click="next"
      >
        <i class="fas fa-chevron-right" aria-hidden="true"></i>
      </button>
    </div>

    <div v-if="slides.length > 1" class="carousel-dots">
      <button
        v-for="(slide, index) in slides"
        :key="slide.title"
        class="carousel-dot"
        :class="{ active: index === active }"
        type="button"
        :aria-label="`Go to ${slide.title}`"
        @click="goTo(index)"
      ></button>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps({
  slides: { type: Array, required: true },
  interval: { type: Number, default: 6000 },
})

const active = ref(0)
let timer = null

function next() {
  active.value = (active.value + 1) % props.slides.length
}

function prev() {
  active.value = (active.value - 1 + props.slides.length) % props.slides.length
}

function goTo(index) {
  active.value = index
  restart()
}

function restart() {
  if (timer) clearInterval(timer)
  if (props.slides.length > 1) {
    timer = setInterval(next, props.interval)
  }
}

onMounted(restart)
onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.carousel-slide-box {
  background: rgb(232, 232, 232);
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.carousel-track {
  display: flex;
  width: 100%;
  transition: transform 0.55s cubic-bezier(0.65, 0, 0.35, 1);
}

.carousel-slide-content {
  display: flex;
  align-items: center;
  gap: 32px;
  padding: 40px 56px;
  min-height: 260px;
  flex: 0 0 100%;
  width: 100%;
}

.carousel-slide-content h2 {
  color: #00264d;
  font-size: 1.9rem;
  font-weight: 800;
  margin-bottom: 12px;
}

.carousel-slide-content p {
  color: #333;
  font-size: 1rem;
  line-height: 1.65;
  margin-bottom: 16px;
  max-width: 720px;
}

.carousel-icon {
  font-size: 5rem;
  color: #00264d;
  flex-shrink: 0;
}

.carousel-nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(0, 38, 77, 0.35);
  border: none;
  color: #fff;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.carousel-nav-btn:hover {
  background: rgba(0, 38, 77, 0.55);
}

.carousel-nav-prev {
  left: 14px;
}

.carousel-nav-next {
  right: 14px;
}

.carousel-dots {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 14px;
}

.carousel-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.4);
}

.carousel-dot.active {
  background: #00264d;
}

@media (max-width: 768px) {
  .carousel-slide-content {
    flex-direction: column;
    text-align: center;
    padding: 24px 20px;
    min-height: auto;
  }
}
</style>
