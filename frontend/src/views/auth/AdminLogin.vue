<template>
  <div class="min-vh-100 bg-light d-flex align-items-center justify-content-center p-4">
    <div class="card border-0 shadow-sm p-4 w-100" style="max-width: 400px; border-radius: 1rem;">
      
      <div class="text-center mb-4">
        <h1 class="h4 fw-bold text-dark">Admin Login</h1>
      </div>

      <div v-if="error" class="alert alert-danger small p-2 text-center mb-4 fw-medium">
        {{ error }}
      </div>

      <div class="d-grid gap-3">
        <input v-model="username" placeholder="admin" class="form-control p-3 bg-light" />
        <input v-model="password" type="password" placeholder="••••••••" class="form-control p-3 bg-light" />

        <button @click="handleLogin" :disabled="loading" class="btn btn-primary w-100 p-3 fw-bold mt-2 shadow-sm">
          {{ loading ? 'Authenticating...' : 'Sign In' }}
        </button>
      </div>

      <div class="mt-4 pt-4 border-top text-center">
        <RouterLink to="/" class="small text-secondary text-decoration-none fw-bold">
          &larr; Back to home
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth.js'

const router   = useRouter()
const auth     = useAuthStore()

const username = ref('')
const password = ref('')
const loading  = ref(false)
const error    = ref('')

async function handleLogin() {
  error.value   = ''
  loading.value = true

  try {
    await auth.loginAdmin(username.value, password.value)
    router.push('/admin/dashboard')
  } catch (err) {
    error.value = err.response?.data?.message || 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>