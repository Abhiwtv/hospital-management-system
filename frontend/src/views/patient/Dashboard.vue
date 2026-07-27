<template>
  <div class="min-vh-100 bg-light">
    <PatientNavbar />

    <main class="container py-4 py-md-5" style="max-width: 960px;">
      
      <header class="mb-5 d-flex flex-column flex-md-row align-items-md-end justify-content-between gap-3">
        <div>
          <h2 class="h3 fw-bold text-dark mb-1">
            Hello, {{ patient.patient_name }}
          </h2>
          <p class="small text-muted fw-medium mb-0">{{ todayLabel }}</p>
        </div>
      </header>

      <div class="row row-cols-2 row-cols-md-4 g-4 mb-5">
        <div class="col">
          <div class="card border-0 shadow-sm p-4 h-100">
            <p class="small text-muted fw-bold mb-1">Upcoming</p>
            <p class="fs-2 fw-bold text-dark mb-0">{{ upcomingAppointments.length }}</p>
          </div>
        </div>
        <div class="col">
          <div class="card border-0 shadow-sm p-4 h-100">
            <p class="small text-muted fw-bold mb-1">Total Visits</p>
            <p class="fs-2 fw-bold text-dark mb-0">{{ pastCount }}</p>
          </div>
        </div>
      </div>

      <section class="mb-5">
        <div class="d-flex align-items-center justify-content-between mb-3">
          <h3 class="h6 fw-bold text-dark mb-0">Upcoming Appointments</h3>
          <RouterLink v-if="upcomingAppointments.length > 0" to="/patient/departments" 
            class="btn btn-outline-dark btn-sm fw-bold px-3">
            New Booking
          </RouterLink>
        </div>

        <div v-if="upcomingAppointments.length === 0"
          class="card border border-2 border-dashed bg-white p-5 text-center shadow-none">
          <p class="text-muted small mb-3">No appointments scheduled.</p>
          <RouterLink to="/patient/departments" 
            class="btn btn-dark fw-bold px-4" style="width: fit-content; margin: 0 auto;">
            Book your first visit
          </RouterLink>
        </div>

        <div v-else class="row row-cols-1 row-cols-md-2 g-3">
          <div v-for="a in upcomingAppointments" :key="a.app_id" class="col">
            <div class="card border-0 shadow-sm p-3 h-100 d-flex flex-row align-items-center justify-content-between">
              <div>
                <div class="d-flex align-items-center gap-2 mb-1">
                  <p class="fw-bold text-dark mb-0">Dr. {{ a.doctor_name }}</p>
                  <span v-if="a.token_no" class="badge bg-secondary bg-opacity-10 text-secondary border border-secondary" style="font-size: 0.7rem;">
                    Token: {{ a.token_no }}
                  </span>
                </div>
                <p class="small text-muted mb-0">
                  {{ a.date }} &middot; {{ a.time }} &middot; {{ a.visit_type }}
                </p>
              </div>
              
              <button @click="openCancelModal(a)" 
                class="btn btn-outline-secondary btn-sm fw-bold px-3">
                Cancel
              </button>
            </div>
          </div>
        </div>
      </section>

      <section>
        <div class="mb-3">
          <h3 class="h6 fw-bold text-dark mb-0">Recent Activity</h3>
        </div>

        <div v-if="recentHistory.length === 0" class="small text-muted fst-italic">No historical data found.</div>

        <div v-else class="card border-0 shadow-sm overflow-hidden">
          <div class="list-group list-group-flush">
            <div v-for="a in recentHistory" :key="a.app_id" class="list-group-item p-4">
              <div class="d-flex justify-content-between align-items-start mb-2">
                <div>
                  <p class="fw-bold text-dark mb-0">Dr. {{ a.doctor_name }}</p>
                  <p class="small text-muted mb-0">{{ a.date }} &middot; {{ a.time }}</p>
                </div>
                <span :class="statusBadge(a.status)">
                  {{ a.status === 'COMPLETED' ? 'Completed' : (a.status === 'CANCELLED' ? 'Cancelled' : a.status) }}
                </span>
              </div>
              
              <div v-if="a.treatment" class="mt-2 ps-3 border-start border-2 border-secondary-subtle">
                <p class="small text-dark mb-0"><span class="fw-bold me-1">Diagnosis:</span> {{ a.treatment.diagnosis || '—' }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>

    <div v-if="modal === 'cancel'" @click="modal = null"
      class="position-fixed top-0 start-0 w-100 h-100 bg-dark bg-opacity-50 d-flex align-items-center justify-content-center p-3" style="z-index: 1050;">
      <div @click.stop class="card border-0 shadow-lg w-100 p-4" style="max-width: 400px;">
        <h3 class="h5 fw-bold text-dark mb-2">Cancel Appointment</h3>
        <p class="small text-muted mb-4">
          Cancel appointment with <strong class="text-dark">Dr. {{ cancelTarget.doctor_name }}</strong>?
        </p>
        <div class="d-grid gap-2">
          <button @click="cancelAppointment" 
            class="btn btn-danger fw-bold py-2">
            Confirm Cancel
          </button>
          <button @click="modal = null" 
            class="btn btn-outline-secondary fw-bold py-2">
            Go Back
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import PatientNavbar from '../../components/PatientNavbar.vue'
import api from '../../api/index.js'

const patient              = ref({})
const upcomingAppointments = ref([])
const recentHistory        = ref([])
const pastCount            = ref(0)
const modal                = ref(null)
const cancelTarget         = ref({})

const todayLabel = computed(() =>
  new Date().toLocaleDateString('en-US', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  })
)

onMounted(() => {
  loadDashboard()
  loadHistory()
})

async function loadDashboard() {
  try {
    const res                  = await api.get('/api/patient/dashboard')
    patient.value              = res.data.data.patient
    upcomingAppointments.value = res.data.data.appointments
  } catch (e) { console.error(e) }
}

async function loadHistory() {
  try {
    const res  = await api.get('/api/patient/history')
    const all  = res.data.data.appointments
    const past = all.filter(a => a.status !== 'BOOKED')
    pastCount.value     = past.length
    recentHistory.value = past.slice(0, 3)
  } catch (e) { console.error(e) }
}

function openCancelModal(a) {
  cancelTarget.value = a
  modal.value        = 'cancel'
}

async function cancelAppointment() {
  try {
    await api.post(`/api/patient/appointments/${cancelTarget.value.app_id}/cancel`)
    modal.value = null
    loadDashboard()
    loadHistory()
  } catch (e) { console.error(e) }
}

function statusBadge(status) {
  if (status === 'COMPLETED') return 'badge bg-success'
  if (status === 'CANCELLED') return 'badge bg-danger'
  if (status === 'BOOKED') return 'badge bg-primary'
  return 'badge bg-secondary'
}
</script>