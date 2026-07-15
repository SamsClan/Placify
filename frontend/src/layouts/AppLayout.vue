<template>
  <div class="app-shell">
    <AppNavbar />
    <ToastHost />
    <main class="page-content container-fluid px-3 px-lg-4 py-4 py-lg-5" style="max-width: 1600px;">
      <slot />
    </main>
    <footer class="site-footer">
      <div class="site-footer-content">
        <p class="site-footer-title">Placify</p>
        <p class="site-footer-text">&copy; 2026 · Connecting students and companies for better careers.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import AppNavbar from '../components/AppNavbar.vue'
import ToastHost from '../components/ToastHost.vue'
</script>
