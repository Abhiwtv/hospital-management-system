<template>
  <div class="min-vh-100 bg-light">
    <AdminNavbar />

    <div class="container py-4" style="max-width: 1140px;">
      <div class="mb-3">
        <select v-model="filter.status" @change="loadAppointments" class="form-select form-select-sm w-auto shadow-sm">
          <option value="">All Statuses</option>
          <option value="BOOKED">Booked</option>
          <option value="COMPLETED">Completed</option>
          <option value="CANCELLED">Cancelled</option>
        </select>
      </div>

      <div class="card border-0 shadow-sm overflow-hidden">
        <table class="table table-hover mb-0 small">
          <thead class="table-light">
            <tr>
              <th class="ps-3 py-2">ID</th>
              <th class="py-2">Patient</th>
              <th class="py-2">Doctor</th>
              <th class="py-2">Date</th>
              <th class="py-2">Time</th>
              <th class="py-2">Status</th>
              <th class="pe-3 py-2">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="7" class="text-center py-4 text-muted">Loading...</td>
            </tr>
            <tr v-else-if="appointments.length === 0">
              <td colspan="7" class="text-center py-4 text-muted">No data</td>
            </tr>
            <tr v-for="a in appointments" :key="a.app_id">
              <td class="ps-3 align-middle">#{{ a.app_id }}</td>
              <td class="align-middle">{{ a.patient_name }}</td>
              <td class="align-middle">{{ a.doctor_name }}</td>
              <td class="align-middle">{{ a.date }}</td>
              <td class="align-middle">{{ a.time }}</td>
              <td class="align-middle">
                <span :class="statusBadge(a.status)">{{ a.status }}</span>
              </td>
              <td class="pe-3 align-middle">
                <button @click="openView(a)" class="btn btn-link text-primary text-decoration-none p-0 small fw-medium">View</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="modal" @click="modal = null" class="position-fixed top-0 start-0 w-100 h-100 bg-dark bg-opacity-50 d-flex align-items-center justify-content-center p-3" style="z-index: 1050;">
      <div @click.stop class="card border-0 shadow-lg w-100" style="max-width: 450px;">
        <div class="card-body p-4">
          <h3 class="h6 fw-bold mb-3 border-bottom pb-2">Appointment Details</h3>

          <div class="small mb-3">
            <p class="mb-1"><strong>ID:</strong> #{{ selected.app_id }}</p>
            <p class="mb-1"><strong>Patient:</strong> {{ selected.patient_name }}</p>
            <p class="mb-1"><strong>Doctor:</strong> {{ selected.doctor_name }}</p>
            <p class="mb-1"><strong>Date:</strong> {{ selected.date }}</p>
            <p class="mb-1"><strong>Time:</strong> {{ selected.time }}</p>
            <p class="mb-1"><strong>Status:</strong> <span :class="statusBadge(selected.status)">{{ selected.status }}</span></p>
          </div>

          <div v-if="selected.treatment" class="small bg-light p-3 rounded mb-3 border">
            <p class="mb-1"><strong>Diagnosis:</strong> {{ selected.treatment.diagnosis || '—' }}</p>
            <p class="mb-1"><strong>Prescription:</strong> {{ selected.treatment.prescription || '—' }}</p>
            <p class="mb-1"><strong>Medication:</strong> {{ selected.treatment.medication || '—' }}</p>
            <p class="mb-1"><strong>Tests:</strong> {{ selected.treatment.tests_done || '—' }}</p>
            <p class="mb-0"><strong>Next Visit:</strong> {{ selected.treatment.next_visit_date || '—' }}</p>
          </div>
          <div v-else class="small text-muted mb-3 fst-italic">No treatment recorded yet.</div>

          <button @click="modal = null" class="btn btn-outline-secondary btn-sm w-100">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AdminNavbar from '../../components/AdminNavbar.vue'
import api from '../../api/index.js'

const appointments = ref([])
const loading = ref(false)
const modal = ref(null)
const selected = ref({})
const filter = ref({ status: '' })

onMounted(loadAppointments)

async function loadAppointments() {
  loading.value = true
  try {
    const params = {}
    if (filter.value.status) params.status = filter.value.status
    const res = await api.get('/api/admin/appointments', { params })
    appointments.value = res.data.data.appointments
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function openView(a) {
  selected.value = a
  modal.value = 'view'
}

function statusBadge(status) {
  if (status === 'COMPLETED') return 'badge bg-success'
  if (status === 'CANCELLED') return 'badge bg-danger'
  if (status === 'BOOKED') return 'badge bg-primary'
  return 'badge bg-secondary'
}
</script>