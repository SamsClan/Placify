<template>
  <AppLayout>
    <section class="login-section">
      <div class="login-card">
        <div class="login-header">
          <span class="login-icon"><i class="fas fa-lock" aria-hidden="true"></i></span>
          <h1>Welcome Back</h1>
          <p>Sign in to continue to Placify.</p>
        </div>

        <div v-if="error" class="alert alert-danger" role="alert"><i class="fas fa-exclamation-circle me-2" aria-hidden="true"></i>{{ error }}</div>

        <form class="needs-validation" novalidate @submit.prevent="handleSubmit">
          <div class="form-group">
            <label for="email" class="form-label"><i class="fas fa-envelope me-1" aria-hidden="true"></i>Email Address</label>
            <input id="email" v-model="form.email" type="email" class="form-control" required autocomplete="email" placeholder="Enter your email" />
          </div>

          <div class="form-group">
            <label for="password" class="form-label"><i class="fas fa-key me-1" aria-hidden="true"></i>Password</label>
            <input id="password" v-model="form.password" type="password" class="form-control" required autocomplete="current-password" placeholder="Enter your password" />
          </div>

          <div class="form-check">
            <input id="remember" class="form-check-input" type="checkbox" />
            <label class="form-check-label" for="remember">Remember me</label>
          </div>

          <button class="btn-login" type="submit" :disabled="auth.loading">
            <i v-if="auth.loading" class="fas fa-spinner fa-spin me-1" aria-hidden="true"></i>
            {{ auth.loading ? 'Signing in...' : 'Sign In' }}
          </button>
        </form>

        <div class="login-footer">
          <p>Don't have an account? <RouterLink to="/register">Create one</RouterLink></p>
        </div>
      </div>
    </section>
  </AppLayout>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '../layouts/AppLayout.vue'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const error = ref('')
const form = reactive({ email: '', password: '' })

async function handleSubmit() {
  error.value = ''
  if (!form.email || !form.password) {
    error.value = 'Email and password are required.'
    return
  }

  try {
    await auth.login(form.email, form.password)
    const roleRoutes = { STUDENT: '/student/dashboard', COMPANY: '/company/dashboard', ADMIN: '/admin/dashboard' }
    router.push(roleRoutes[auth.role] || '/dashboard')
  } catch (err) {
    error.value = err?.response?.data?.message || 'Unable to sign in.'
  }
}
</script>

<style src="../styles/pages/public/login.css"></style>
