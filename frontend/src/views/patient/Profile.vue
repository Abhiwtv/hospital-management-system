<template>
  <div class="min-vh-100 bg-light">
    <PatientNavbar />

    <div class="container py-4 py-md-5" style="max-width: 700px;">

      <div class="mb-5 pb-4 border-bottom">
        <h2 class="h3 fw-bold text-dark mb-1">Your Profile</h2>
        <p class="small text-muted mb-0">View and update your personal details.</p>
      </div>

      <div v-if="loading" class="text-muted small py-5 text-center border-top border-bottom bg-white rounded shadow-sm">
        Loading profile data...
      </div>

      <div v-else class="card border-0 shadow-sm p-4 p-md-5">
        <div class="row g-4">
          
          <div class="col-12">
            <label class="form-label small fw-bold text-muted text-uppercase mb-1" style="font-size: 0.75rem;">Full Name</label>
            <input v-model="form.patient_name" type="text" class="form-control bg-light" />
          </div>
          
          <div class="col-12">
            <label class="form-label small fw-bold text-muted text-uppercase mb-1" style="font-size: 0.75rem;">Username</label>
            <input v-model="form.patient_username" type="text" class="form-control bg-light" />
          </div>
          
          <div class="col-12">
            <label class="form-label small fw-bold text-muted text-uppercase mb-1" style="font-size: 0.75rem;">Email</label>
            <input v-model="form.email" type="email" class="form-control bg-light" />
          </div>
          
          <div class="col-12">
            <label class="form-label small fw-bold text-muted text-uppercase mb-1" style="font-size: 0.75rem;">Phone</label>
            <input v-model="form.phone" type="text" class="form-control bg-light" />
          </div>
          
          <div class="col-md-6">
            <label class="form-label small fw-bold text-muted text-uppercase mb-1" style="font-size: 0.75rem;">Age</label>
            <input v-model="form.age" type="number" class="form-control bg-light" />
          </div>
          <div class="col-md-6">
            <label class="form-label small fw-bold text-muted text-uppercase mb-1" style="font-size: 0.75rem;">Gender</label>
            <select v-model="form.gender" class="form-select bg-light">
              <option value="">Select</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
          </div>
          
          <div class="col-12">
            <label class="form-label small fw-bold text-muted text-uppercase mb-1" style="font-size: 0.75rem;">Address</label>
            <input v-model="form.address" type="text" class="form-control bg-light" />
          </div>
        </div>

        <div class="mt-3 min-h-[20px]">
          <p v-if="errorMsg" class="text-danger small fw-bold mb-0">{{ errorMsg }}</p>
          <p v-if="successMsg" class="text-success small fw-bold mb-0">{{ successMsg }}</p>
        </div>

        <div class="mt-5 pt-4 border-top">
          <button @click="save" :disabled="saving"
            class="btn btn-dark fw-bold px-4 py-2 w-100">
            {{ saving ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import PatientNavbar from '../../components/PatientNavbar.vue'
import api from '../../api/index.js'

const loading    = ref(false)
const saving     = ref(false)
const errorMsg   = ref('')
const successMsg = ref('')

const form = ref({
  patient_name: '', patient_username: '', email: '',
  phone: '', age: '', gender: '', address: '',
})

onMounted(loadProfile)

async function loadProfile() {
  loading.value = true
  try {
    const res = await api.get('/api/patient/dashboard')
    const p   = res.data.data.patient
    form.value = {
      patient_name:     p.patient_name,
      patient_username: p.patient_username,
      email:            p.email,
      phone:            p.phone,
      age:              p.age,
      gender:           p.gender,
      address:          p.address,
    }
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

async function save() {
  saving.value     = true
  errorMsg.value   = ''
  successMsg.value = ''
  try {
    await api.put('/api/patient/profile', form.value)
    successMsg.value = 'Profile updated successfully.'
    setTimeout(() => successMsg.value = '', 3000)
  } catch (e) {
    errorMsg.value = e.response?.data?.message || 'Failed to update profile.'
  } finally {
    saving.value = false
  }
}
</script>