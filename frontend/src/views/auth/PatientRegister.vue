<template>
  <div class="min-vh-100 bg-light d-flex align-items-center justify-content-center p-4 py-5">
    <div class="card border-0 shadow-sm p-4 w-100" style="max-width: 500px; border-radius: 1rem;">
      
      <div class="text-center mb-4">
        <h1 class="h3 fw-bold text-dark">Create Account</h1>
      </div>

      <div v-if="error" class="alert alert-danger small p-2 text-center mb-4 fw-medium">
        {{ error }}
      </div>

      <div v-if="success" class="alert alert-success small p-2 text-center mb-4 fw-medium">
        Registration successful. Redirecting...
      </div>

      <div class="d-grid gap-3">
        <input v-model="form.name" placeholder="Full Name" class="form-control p-3" />
        <input v-model="form.username" placeholder="Pick a username" class="form-control p-3" />
        <input v-model="form.email" type="email" placeholder="Email Address" class="form-control p-3" />
        <input v-model="form.password" type="password" placeholder="Create Password" class="form-control p-3" />

        <div class="row g-3">
          <div class="col-4">
            <input v-model="form.age" type="number" placeholder="Age" class="form-control p-3" />
          </div>
          <div class="col-8">
            <select v-model="form.gender" class="form-select p-3">
              <option value="">Gender</option>
              <option>Male</option>
              <option>Female</option>
              <option>Other</option>
            </select>
          </div>
        </div>

        <input v-model="form.phone" placeholder="Phone Number" class="form-control p-3" />
        <input v-model="form.address" placeholder="Residential Address" class="form-control p-3 mb-2" />

        <button @click="handleRegister" :disabled="loading" class="btn btn-primary w-100 p-3 fw-bold shadow-sm">
          {{ loading ? 'Creating your profile...' : 'Complete Registration' }}
        </button>
      </div>

      <div class="mt-4 text-center">
        <p class="small text-muted mb-2">
          Already registered? 
          <RouterLink to="/login/patient" class="text-primary fw-bold text-decoration-none ms-1">Log in here</RouterLink>
        </p>
        <p class="small text-muted mb-0">
          <RouterLink to="/" class="text-primary fw-bold text-decoration-none">Back to Home</RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../api/index.js'

const router  = useRouter()
const loading = ref(false)
const error   = ref('')
const success = ref(false)

const form = ref({
  name:     '',
  username: '',
  email:    '',
  password: '',
  age:      '',
  gender:   '',
  phone:    '',
  address:  '',
})

async function handleRegister() {
  error.value   = ''
  loading.value = true

  try {
    await api.post('/api/auth/register/patient', form.value)
    success.value = true
    setTimeout(() => router.push('/login/patient'), 1500)
  } catch (err) {
    error.value = err.response?.data?.message || 'Registration failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>