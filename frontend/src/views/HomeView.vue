<template>
  <AppLayout>
    <section class="landing-hero">
      <div class="landing-hero-content">
        <span class="landing-eyebrow"><i class="fas fa-graduation-cap" aria-hidden="true"></i>Placement Management System</span>
        <h1>Welcome to your campus placement hub.</h1>
        <h3>Streamline applications, interviews, and hiring decisions in one place.</h3>
        <p>
          Placify helps students discover opportunities, lets companies manage drives, and gives admins
          complete visibility over the entire placement workflow.
        </p>
        <div class="landing-hero-actions">
          <RouterLink class="btn-pp-primary btn-lg" to="/login"><i class="fas fa-right-to-bracket" aria-hidden="true"></i>Enter portal</RouterLink>
          <RouterLink class="btn-pp-outline btn-lg" style="color: #fff; border-color: rgba(255,255,255,0.6);" to="/register">
            <i class="fas fa-user-plus me-1" aria-hidden="true"></i>Register
          </RouterLink>
        </div>

        <div class="landing-highlights">
          <div class="landing-highlight-card">
            <i class="fas fa-user-graduate" aria-hidden="true"></i>
            <h4>For students</h4>
            <p>Discover openings, apply in a few clicks, and track every application's status.</p>
          </div>
          <div class="landing-highlight-card">
            <i class="fas fa-building" aria-hidden="true"></i>
            <h4>For companies</h4>
            <p>Post drives, review candidates, and manage your hiring pipeline end-to-end.</p>
          </div>
          <div class="landing-highlight-card">
            <i class="fas fa-shield-halved" aria-hidden="true"></i>
            <h4>For admins</h4>
            <p>Approve companies and drives, moderate accounts, and oversee placements.</p>
          </div>
        </div>
      </div>
    </section>
  </AppLayout>
</template>

<script setup>
import AppLayout from '../layouts/AppLayout.vue'
</script>

<style src="../styles/pages/public/home.css"></style>
