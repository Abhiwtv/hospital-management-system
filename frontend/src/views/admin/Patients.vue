<template>
  <div class="min-vh-100 bg-light">
    <AdminNavbar />

    <div class="container py-4" style="max-width: 1140px;">
      <div class="card border-0 shadow-sm overflow-hidden">
        <table class="table table-hover mb-0 small">
          <thead class="table-light">
            <tr>
              <th class="ps-3 py-2">Name</th>
              <th class="py-2">Username</th>
              <th class="py-2">Email</th>
              <th class="py-2">Phone</th>
              <th class="py-2">Status</th>
              <th class="pe-3 py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="6" class="text-center py-4 text-muted">Loading...</td>
            </tr>
            <tr v-else-if="patients.length === 0">
              <td colspan="6" class="text-center py-4 text-muted">No data</td>
            </tr>
            <tr v-for="p in patients" :key="p.patient_id">
              <td class="ps-3 align-middle fw-medium">{{ p.patient_name }}</td>
              <td class="align-middle text-muted">{{ p.patient_username }}</td>
              <td class="align-middle">{{ p.email }}</td>
              <td class="align-middle">{{ p.phone }}</td>
              <td class="align-middle">
                <span :class="p.is_blacklisted ? 'text-danger' : 'text-success'" class="fw-bold">
                  {{ p.is_blacklisted ? 'Blacklisted' : 'Active' }}
                </span>
              </td>
              <td class="pe-3 align-middle">
                <div class="d-flex gap-2">
                  <button @click="openHistory(p)" class="btn btn-link text-primary text-decoration-none p-0 small fw-bold">History</button>
                  <button @click="toggleBlacklist(p)" class="btn btn-link text-decoration-none p-0 small fw-bold" :class="p.is_blacklisted ? 'text-success' : 'text-warning'">
                    {{ p.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}
                  </button>
                  <button @click="openDeleteModal(p)" class="btn btn-link text-danger text-decoration-none p-0 small fw-bold">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="modal" @click="closeModal" class="position-fixed top-0 start-0 w-100 h-100 bg-dark bg-opacity-50 d-flex align-items-center justify-content-center p-3" style="z-index: 1050;">
      <div @click.stop class="card border-0 shadow-lg w-100" style="max-width: 500px; max-height: 90vh; overflow-y: auto;">
        <div class="card-body p-4">

          <template v-if="modal === 'history'">
            <h3 class="h6 fw-bold mb-0">{{ selected.patient_name }}</h3>
            <p class="small text-muted mb-3 border-bottom pb-2">{{ selected.email }}</p>

            <div v-if="history.length === 0" class="text-center py-4 text-muted small fst-italic">
              No medical history found.
            </div>

            <div class="d-flex flex-column gap-2 mb-3">
              <div v-for="a in history" :key="a.app_id" class="card border border-secondary-subtle shadow-none">
                <div class="card-body p-3">
                  <div class="d-flex justify-content-between mb-1">
                    <span class="fw-bold small">{{ a.doctor_name }}</span>
                    <span :class="statusBadge(a.status)" class="small">{{ a.status }}</span>
                  </div>
                  <p class="small text-muted mb-2">{{ a.date }} at {{ a.time }}</p>

                  <div v-if="a.treatment" class="small bg-light p-2 rounded">
                    <p class="mb-1"><strong>Diagnosis:</strong> {{ a.treatment.diagnosis || '—' }}</p>
                    <p class="mb-1"><strong>Prescription:</strong> {{ a.treatment.prescription || '—' }}</p>
                    <p class="mb-1"><strong>Medication:</strong> {{ a.treatment.medication || '—' }}</p>
                    <p class="mb-0"><strong>Next Visit:</strong> {{ a.treatment.next_visit_date || '—' }}</p>
                  </div>
                </div>
              </div>
            </div>

            <button @click="closeModal" class="btn btn-outline-secondary btn-sm w-100 mt-2">Close</button>
          </template>

          <template v-if="modal === 'delete'">
            <h3 class="h6 fw-bold text-danger mb-2">Confirm Delete</h3>
            <p class="small mb-4">Are you sure you want to permanently delete patient <strong>{{ selected.patient_name }}</strong>?</p>
            <div class="d-flex gap-2">
              <button @click="deletePatient" class="btn btn-danger btn-sm flex-grow-1">Delete</button>
              <button @click="closeModal" class="btn btn-outline-secondary btn-sm flex-grow-1">Cancel</button>
            </div>
          </template>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AdminNavbar from '../../components/AdminNavbar.vue'
import api from '../../api/index.js'

const patients = ref([])
const history = ref([])
const loading = ref(false)
const modal = ref(null)
const selected = ref({})

onMounted(loadPatients)

async function loadPatients() {
  loading.value = true
  try {
    const res = await api.get('/api/admin/patients')
    patients.value = res.data.data.patients
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function openHistory(p) {
  selected.value = p
  try {
    const res = await api.get(`/api/admin/patients/${p.patient_id}/history`)
    history.value = res.data.data.appointments
  } catch (e) {
    console.error(e)
  }
  modal.value = 'history'
}

async function toggleBlacklist(p) {
  const action = p.is_blacklisted ? 'unblacklist' : 'blacklist'
  try {
    await api.post(`/api/admin/patients/${p.patient_id}/${action}`)
    loadPatients()
  } catch (e) {
    console.error(e)
  }
}

function openDeleteModal(p) {
  selected.value = p
  modal.value = 'delete'
}

async function deletePatient() {
  try {
    await api.delete(`/api/admin/patients/${selected.value.patient_id}`)
    closeModal()
    loadPatients()
  } catch (e) {
    console.error(e)
  }
}

function closeModal() {
  modal.value = null
}

function statusBadge(status) {
  if (status === 'COMPLETED') return 'badge bg-success'
  if (status === 'CANCELLED') return 'badge bg-danger'
  if (status === 'BOOKED') return 'badge bg-primary'
  return 'badge bg-secondary'
}
</script>