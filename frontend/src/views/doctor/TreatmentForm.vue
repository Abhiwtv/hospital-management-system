<template>
  <div class="min-vh-100 bg-light">
    <DoctorNavbar />

    <div class="container py-5" style="max-width: 800px;">
      <button @click="router.back()" class="btn btn-link text-decoration-none small fw-bold text-muted px-0 mb-4 text-uppercase">
        &larr; Return to History
      </button>

      <div v-if="loading" class="text-center py-5 text-muted small">Opening consultation form...</div>

      <template v-else>
        <div class="card border-0 shadow-sm p-4 mb-4 bg-white">
          <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3">
            <div>
              <p class="small fw-bold text-muted text-uppercase mb-1">
                Current Session
              </p>
              <h2 class="h5 fw-bold text-dark mb-0">{{ appointment.patient_name }}</h2>
            </div>
            <div class="text-md-end">
              <p class="small fw-bold text-dark mb-1">{{ appointment.date }}</p>
              <p class="small text-muted mb-0">
                {{ appointment.visit_type }} &middot; {{ appointment.time }}
              </p>
            </div>
          </div>
        </div>

        <div class="card border-0 shadow-sm p-4 bg-white">
          <h2 class="h5 fw-bold text-dark mb-4 border-bottom pb-2">Treatment Plan</h2>

          <div class="row g-4">
            
            <div class="col-12">
              <label class="form-label small fw-bold text-dark mb-1">Clinical Diagnosis</label>
              <textarea v-model="form.diagnosis" placeholder="Describe the primary diagnosis..."
                class="form-control bg-light" rows="4"></textarea>
            </div>
            
            <div class="col-12">
              <label class="form-label small fw-bold text-dark mb-1">Detailed Prescription</label>
              <textarea v-model="form.prescription" placeholder="List medications, dosage, and duration..."
                class="form-control bg-light" rows="4"></textarea>
            </div>

            <div class="col-md-6">
              <label class="form-label small fw-bold text-dark mb-1">Medication Summary</label>
              <input v-model="form.medication" type="text" placeholder="Short-form list (e.g. Advil, 500mg)"
                class="form-control bg-light" />
            </div>

            <div class="col-md-6">
              <label class="form-label small fw-bold text-dark mb-1">Recommended Tests</label>
              <input v-model="form.tests_done" type="text" placeholder="e.g. MRI, Blood Panel"
                class="form-control bg-light" />
            </div>

            <div class="col-md-6">
              <label class="form-label small fw-bold text-dark mb-1">Follow-up Date</label>
              <input v-model="form.next_visit_date" type="date"
                class="form-control bg-light" />
            </div>

          </div>

          <div v-if="errorMsg || successMsg" class="mt-3">
            <p v-if="errorMsg" class="text-danger small fw-medium mb-0">{{ errorMsg }}</p>
            <p v-if="successMsg" class="text-success small fw-medium mb-0">{{ successMsg }}</p>
          </div>

          <div class="d-flex flex-column flex-md-row gap-3 pt-4 mt-4 border-top">
            <button @click="save" :disabled="saving"
              class="btn btn-dark fw-bold px-4 flex-grow-1">
              {{ saving ? 'Finalizing...' : 'Save and Close Record' }}
            </button>

            <button @click="router.back()"
              class="btn btn-outline-secondary fw-bold flex-grow-1">
              Discard Changes
            </button>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DoctorNavbar from '../../components/DoctorNavbar.vue'
import api from '../../api/index.js'

const route  = useRoute()
const router = useRouter()

const appointment = ref({})
const loading     = ref(false)
const saving      = ref(false)
const errorMsg    = ref('')
const successMsg  = ref('')

const form = ref({
  diagnosis:       '',
  prescription:    '',
  medication:      '',
  tests_done:      '',
  next_visit_date: '',
})

onMounted(loadAppointment)

async function loadAppointment() {
  loading.value = true
  try {
    const res         = await api.get(`/api/doctor/appointments/${route.params.id}/treatment`)
    appointment.value = res.data.data.appointment

    const t = res.data.data.treatment
    if (t) {
      form.value = {
        diagnosis:       t.diagnosis       || '',
        prescription:    t.prescription    || '',
        medication:      t.medication      || '',
        tests_done:      t.tests_done      || '',
        next_visit_date: t.next_visit_date || '',
      }
    }
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

async function save() {
  errorMsg.value   = ''
  successMsg.value = ''
  saving.value     = true
  try {
    await api.post(
      `/api/doctor/appointments/${route.params.id}/treatment`,
      form.value
    )
    successMsg.value = '✓ Treatment saved successfully.'
    setTimeout(() => router.back(), 1200)
  } catch (e) {
    errorMsg.value = e.response?.data?.message || 'Failed to save treatment.'
  } finally {
    saving.value = false
  }
}
</script>