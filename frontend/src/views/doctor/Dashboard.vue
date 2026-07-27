<template>
  <div class="min-vh-100 bg-light">
    <DoctorNavbar />

    <main class="container py-4 py-md-5" style="max-width: 1140px;">
      
      <header class="mb-5 d-flex flex-column flex-md-row justify-content-between align-items-md-end gap-3">
        <div>
          <h1 class="h3 fw-bold text-dark mb-1">
            Welcome, Dr. {{ doctor.doctor_name }}
          </h1>
          <p class="small text-muted fw-medium mb-0">
            {{ todayLabel }} &middot; {{ doctor.department_name }}
          </p>
        </div>
      </header>

      <div class="row row-cols-1 row-cols-md-3 g-4 mb-5">
        <div class="col">
          <div class="card border-0 shadow-sm p-4 h-100">
            <p class="small fw-bold text-muted text-uppercase mb-1">Today's Load</p>
            <p class="fs-2 fw-bold text-dark mb-0">{{ todayCount }} <span class="fs-6 text-muted fw-medium">Appointments</span></p>
          </div>
        </div>
        <div class="col">
          <div class="card border-0 shadow-sm p-4 h-100">
            <p class="small fw-bold text-muted text-uppercase mb-1">Patient Pool</p>
            <p class="fs-2 fw-bold text-dark mb-0">{{ assignedPatients.length }} <span class="fs-6 text-muted fw-medium">Assigned</span></p>
          </div>
        </div>
        <div class="col">
          <div class="card bg-secondary bg-opacity-10 border-0 p-4 h-100">
            <p class="small fw-bold text-muted text-uppercase mb-1">Pending Reviews</p>
            <p class="fs-2 fw-bold text-dark mb-0">{{ upcomingAppointments.length }} <span class="fs-6 text-muted fw-medium">To clear</span></p>
          </div>
        </div>
      </div>

      <div class="row g-5">
        
        <section class="col-lg-8">
          <h2 class="h6 fw-bold text-dark text-uppercase mb-3">Active Schedule</h2>
          
          <div v-if="upcomingAppointments.length === 0" class="card border border-2 border-dashed bg-white p-5 text-center shadow-none">
            <p class="text-muted fw-medium mb-0">Your schedule is clear for now.</p>
          </div>

          <div v-else class="d-flex flex-column gap-3">
            <div v-for="a in upcomingAppointments" :key="a.app_id" 
                 class="card border-0 shadow-sm p-3 d-flex flex-column flex-sm-row align-items-sm-center justify-content-between gap-3 transition-all">
              
              <div>
                <p class="fw-bold text-dark fs-5 mb-1">{{ a.patient_name }}</p>
                <p class="small text-muted fw-medium mb-0">
                  <span class="text-dark fw-bold">{{ a.time }}</span> &middot; {{ a.visit_type }}
                </p>
              </div>

              <div class="d-flex flex-wrap align-items-center gap-3">
                <button @click="openCancelModal(a)" class="btn btn-link text-secondary text-decoration-none small fw-bold p-0">Cancel</button>
                <button @click="openBlacklistModal(a)" class="btn btn-link text-secondary text-decoration-none small fw-bold p-0">Blacklist</button>
                <RouterLink :to="`/doctor/patients/${a.patient_id}`" class="text-primary text-decoration-none small fw-bold">History</RouterLink>
                <button @click="openCompleteModal(a)" class="btn btn-dark btn-sm fw-bold px-3">
                  COMPLETE
                </button>
              </div>
            </div>
          </div>
        </section>

        <aside class="col-lg-4">
          <h2 class="h6 fw-bold text-dark text-uppercase mb-3">Patient Directory</h2>
          
          <div class="card border-0 shadow-sm overflow-hidden">
            <div v-if="assignedPatients.length === 0" class="p-4 text-center small text-muted">
              No patients assigned yet.
            </div>
            
            <div v-else class="list-group list-group-flush">
              <div v-for="p in assignedPatients" :key="p.patient_id" class="list-group-item p-3">
                
                <div class="d-flex justify-content-between align-items-start mb-1">
                  <p class="small fw-bold text-dark mb-0">{{ p.patient_name }}</p>
                  <span v-if="p.is_blacklisted" class="badge bg-danger bg-opacity-10 text-danger border border-danger text-uppercase" style="font-size: 0.65rem;">Blocked</span>
                </div>
                
                <p class="small text-muted mb-2">{{ p.gender }} &middot; {{ p.age }} Years</p>
                
                <div class="d-flex align-items-center gap-3">
                  <RouterLink :to="`/doctor/patients/${p.patient_id}`" class="text-primary text-decoration-none small fw-bold">
                    View History
                  </RouterLink>
                  <button @click="toggleBlacklist(p)" class="btn btn-link text-secondary text-decoration-none small fw-bold p-0">
                    {{ p.is_blacklisted ? 'Unblock Patient' : 'Restrict Patient' }}
                  </button>
                </div>

              </div>
            </div>
          </div>
        </aside>

      </div>
    </main>

    <div v-if="modal" class="position-fixed top-0 start-0 w-100 h-100 bg-dark bg-opacity-50 d-flex align-items-center justify-content-center p-3" style="z-index: 1050;">
      <div class="card border-0 shadow-lg w-100 p-4" style="max-width: 400px; border-radius: 1rem;">
        <h3 class="h5 fw-bold text-dark mb-2">Confirm Action</h3>
        <p class="small text-muted mb-4">
          You are about to modify the record for <strong class="text-dark">{{ selectedAppt?.patient_name }}</strong>.
        </p>
        <div class="d-grid gap-2">
          <button @click="modal === 'blacklist' ? blacklistPatient() : modal === 'complete' ? completeAppointment() : cancelAppointment()" 
            class="btn btn-dark fw-bold py-2">
            Confirm Proceed
          </button>
          <button @click="closeModal" class="btn btn-link text-secondary text-decoration-none fw-bold py-2">
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import DoctorNavbar from '../../components/DoctorNavbar.vue'
import api from '../../api/index.js'

const doctor               = ref({})
const upcomingAppointments = ref([])
const assignedPatients     = ref([])
const modal                = ref(null)
const selectedAppt         = ref({})

const timeOfDay = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return 'morning'
  if (h < 17) return 'afternoon'
  return 'evening'
})

const todayLabel = computed(() =>
  new Date().toLocaleDateString('en-US', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  })
)

const todayCount = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  return upcomingAppointments.value.filter(a => a.date === today).length
})

onMounted(loadDashboard)

async function loadDashboard() {
  try {
    const res                  = await api.get('/api/doctor/dashboard')
    doctor.value               = res.data.data.doctor
    upcomingAppointments.value = res.data.data.appointments
    assignedPatients.value     = res.data.data.assigned_patients
  } catch (e) { console.error(e) }
}

function openBlacklistModal(a) { selectedAppt.value = a; modal.value = 'blacklist' }
function openCompleteModal(a)  { selectedAppt.value = a; modal.value = 'complete'  }
function openCancelModal(a)    { selectedAppt.value = a; modal.value = 'cancel'    }
function closeModal()          { modal.value = null }

async function blacklistPatient() {
  try {
    await api.post(`/api/doctor/patients/${selectedAppt.value.patient_id}/blacklist`)
    closeModal(); loadDashboard()
  } catch (e) { console.error(e) }
}

async function toggleBlacklist(p) {
  const action = p.is_blacklisted ? 'unblacklist' : 'blacklist'
  try {
    await api.post(`/api/doctor/patients/${p.patient_id}/${action}`)
    loadDashboard()
  } catch (e) { console.error(e) }
}

async function completeAppointment() {
  try {
    await api.post(`/api/doctor/appointments/${selectedAppt.value.app_id}/complete`)
    closeModal(); loadDashboard()
  } catch (e) { console.error(e) }
}

async function cancelAppointment() {
  try {
    await api.post(`/api/doctor/appointments/${selectedAppt.value.app_id}/cancel`)
    closeModal(); loadDashboard()
  } catch (e) { console.error(e) }
}
</script>