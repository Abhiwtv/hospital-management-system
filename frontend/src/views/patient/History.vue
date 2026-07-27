<template>
  <div class="min-vh-100 bg-light">
    <PatientNavbar />

    <div class="container py-4" style="max-width: 800px;">
      
      <div class="d-flex justify-content-between align-items-center mb-4 border-bottom pb-3">
        <div>
          <h2 class="mb-0">Clinical History</h2>
          <p class="text-muted">Your past medical visits.</p>
        </div>
        
        <div>
          <button @click="exportCSV" :disabled="exporting" class="btn btn-secondary btn-bg-black">
            {{ exporting ? 'Exporting...' : 'Export CSV' }}
          </button>
        </div>
      </div>

      <div v-if="exportMsg" class="alert alert-success py-2">{{ exportMsg }}</div>

      <div v-if="loading" class="text-center mt-5">Loading records...</div>
      <div v-else-if="appointments.length === 0" class="text-center mt-5">No clinical history found.</div>

      <div v-else>
        <div v-for="a in appointments" :key="a.app_id" class="card mb-4 shadow-sm">
          
          <div class="card-header bg-white d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Dr. {{ a.doctor_name }}</h5>
            <span :class="statusBadge(a.status)">{{ a.status }}</span>
          </div>

          <div class="card-body">
            <p class="mb-3">
              <strong>Date:</strong> {{ a.date }} &nbsp;|&nbsp; 
              <strong>Time:</strong> {{ a.time }} &nbsp;|&nbsp; 
              <strong>Type:</strong> {{ a.visit_type }}
            </p>

            <div v-if="a.treatment" class="bg-light p-3 border rounded">
              <h6 class="mb-3 border-bottom pb-1">Treatment Notes</h6>
              <p class="mb-1"><strong>Diagnosis:</strong> {{ a.treatment.diagnosis || 'None' }}</p>
              <p class="mb-1"><strong>Prescription:</strong> {{ a.treatment.prescription || 'None' }}</p>
              <p class="mb-0"><strong>Medication:</strong> {{ a.treatment.medication || 'None' }}</p>
            </div>
            
            <div v-else class="text-muted">
              <em>No treatment notes recorded.</em>
            </div>
          </div>

          <div class="card-footer bg-white text-end" v-if="a.status === 'COMPLETED'">
            <button 
              @click="a.chat_open ? openChat(a) : null" 
              :disabled="!a.chat_open"
              class="btn btn-sm"
              :class="a.chat_open ? 'btn-primary' : 'btn-outline-secondary'"
            >
              {{ a.chat_open ? 'Open Follow-up Chat' : (a.chat_closed ? 'Chat Closed' : 'Follow-up Period Ended') }}
            </button>
          </div>
          
        </div>
      </div>
    </div>

    <ChatModal v-if="chatAppointment" :appointment="chatAppointment" role="patient" @close="chatAppointment = null" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import PatientNavbar from '../../components/PatientNavbar.vue'
import ChatModal from '../../components/ChatModal.vue'
import api from '../../api/index.js'

const appointments   = ref([])
const loading        = ref(false)
const exporting      = ref(false)
const exportMsg      = ref('')
const chatAppointment = ref(null)

onMounted(loadHistory)

async function loadHistory() {
  loading.value = true
  try {
    const res          = await api.get('/api/patient/history')
    appointments.value = res.data.data.appointments
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

function openChat(a) {
  chatAppointment.value = a
}

async function exportCSV() {
  exporting.value = true
  exportMsg.value = ''
  try {
    await api.post('/api/patient/export/csv')
    exportMsg.value = 'Export started, check your email shortly.'
    setTimeout(() => exportMsg.value = '', 6000)
  } catch (e) {
    exportMsg.value = 'Export failed. Please try again.'
    setTimeout(() => exportMsg.value = '', 6000)
  } finally {
    exporting.value = false
  }
}


function statusBadge(status) {
  if (status === 'COMPLETED') return 'badge bg-success'
  if (status === 'CANCELLED') return 'badge bg-danger'
  if (status === 'BOOKED') return 'badge bg-primary'
  return 'badge bg-secondary'
}
</script>