<template>
  <div class="min-vh-100 bg-light">
    <PatientNavbar />

    <div class="container py-4 py-md-5" style="max-width: 900px;">

      <nav class="d-flex align-items-center small text-uppercase fw-bold text-muted mb-4 mb-md-5">
        <button @click="goBack" class="btn btn-link text-decoration-none p-0" :class="view === 'list' ? 'text-dark' : 'text-muted'">
          Departments
        </button>
        <span v-if="selectedDept" class="mx-2">/</span>
        <span v-if="selectedDept" class="text-dark">
          {{ selectedDept.dep_name }}
        </span>
      </nav>

      <div v-if="view === 'list'">
        <div class="mb-4">
          <h2 class="h3 fw-bold text-dark">Medical Departments</h2>
          <p class="small text-muted mt-1">Select a specialty to view available practitioners.</p>
        </div>

        <div v-if="loading" class="py-5 text-muted small">Fetching departments...</div>
        <div v-else-if="departments.length === 0" class="py-5 text-muted small">No departments available at this time.</div>

        <div v-else class="d-flex flex-column gap-3">
          <button
            v-for="d in departments" :key="d.dep_id"
            @click="openDept(d)"
            class="card border-0 shadow-sm p-4 text-start transition-all btn btn-light text-dark text-decoration-none"
          >
            <div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-3">
              <div>
                <p class="h5 fw-bold mb-1">{{ d.dep_name }}</p>
                <p class="small text-muted mb-0" style="display: -webkit-box; -webkit-box-orient: vertical; overflow: hidden;">
                  {{ d.dep_des || 'Specialized medical care and consultation.' }}
                </p>
              </div>
              <div>
                <span class="badge bg-white text-dark border shadow-sm px-3 py-2">
                  {{ d.no_docs_registered }} Doctors
                </span>
              </div>
            </div>
          </button>
        </div>
      </div>

      <div v-if="view === 'doctors'">
        <div class="mb-4">
          <h3 class="h3 fw-bold text-dark">{{ selectedDept.dep_name }}</h3>
          <p class="small text-muted mt-1">{{ selectedDept.dep_des }}</p>
        </div>

        <div v-if="loadingDoctors" class="py-5 text-muted small">Loading medical staff...</div>
        <div v-else-if="doctors.length === 0" class="py-5 text-muted small">No doctors are currently listed in this department.</div>

        <div v-else class="d-flex flex-column gap-3">
          <RouterLink
            v-for="doc in doctors" :key="doc.doctor_id"
            :to="`/patient/doctors/${doc.doctor_id}`"
            class="card border-0 shadow-sm p-4 text-decoration-none transition-all"
          >
            <div class="d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-3">
              <div>
                <p class="h5 fw-bold text-dark mb-1">Dr. {{ doc.doctor_name }}</p>
                <p class="small fw-bold text-primary mb-2">{{ doc.doctor_type || 'Practitioner' }}</p>
                
                <div class="small text-muted">
                  <p v-if="doc.doctor_qualification" class="mb-0">
                    <strong class="text-dark">Qualifications:</strong> {{ doc.doctor_qualification }}
                  </p>
                  <p v-if="doc.doctor_experience" class="mb-0">
                    <strong class="text-dark">Experience:</strong> {{ doc.doctor_experience }} years
                  </p>
                </div>
              </div>
              
              <div>
                <span class="btn btn-dark fw-bold px-4 py-2 shadow-sm w-100">
                  Book Appointment
                </span>
              </div>
            </div>
          </RouterLink>
        </div>
      </div>

    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import PatientNavbar from '../../components/PatientNavbar.vue'
import api from '../../api/index.js'

const departments   = ref([])
const doctors       = ref([])
const selectedDept  = ref(null)
const view          = ref('list')    
const loading       = ref(false)
const loadingDoctors = ref(false)

onMounted(loadDepartments)

async function loadDepartments() {
  loading.value = true
  try {
    const res         = await api.get('/api/patient/dashboard')
    departments.value = res.data.data.departments || []
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

async function openDept(dept) {
  selectedDept.value  = dept
  view.value          = 'doctors'
  loadingDoctors.value = true
  try {
    const res     = await api.get(`/api/patient/departments/${dept.dep_id}`)
    doctors.value = res.data.data.doctors
  } catch (e) { console.error(e) }
  finally { loadingDoctors.value = false }
}

function goBack() {
  if (view.value === 'doctors') {
    view.value        = 'list'
    selectedDept.value = null
  }
}
</script>