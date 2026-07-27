<template>
  <div class="min-vh-100 bg-white">
    <DoctorNavbar />

    <div class="container py-5" style="max-width: 800px;">
      <div class="mb-4 border-bottom pb-3">
        <h2 class="h5 fw-bold text-dark mb-1">Appointment History</h2>
        <p class="small text-muted mb-0">Completed and cancelled visits</p>
      </div>

      <div v-if="loading" class="text-center text-muted py-5">
        Loading...
      </div>

      <div v-else-if="appointments.length === 0" class="text-muted small text-center py-5">
        No history found.
      </div>

      <div v-else class="d-flex flex-column gap-3">
        <div
          v-for="a in appointments"
          :key="a.app_id"
          class="card border-0 shadow-sm p-4 bg-light"
        >
          <div class="d-flex justify-content-between align-items-start mb-3">
            <div>
              <p class="small fw-bold text-dark mb-0">
                {{ a.patient_name }}
              </p>
              <p class="text-muted mb-0" style="font-size: 0.75rem;">
                {{ a.date }} · {{ a.time }} · {{ a.visit_type }}
              </p>
            </div>

            <span :class="statusBadge(a.status)">
              {{ a.status }}
            </span>
          </div>

          <div v-if="a.treatment" class="small bg-white p-3 rounded border">
            <p class="mb-1"><span class="text-muted fw-semibold">Diagnosis:</span> {{ a.treatment.diagnosis || '—' }}</p>
            <p class="mb-1"><span class="text-muted fw-semibold">Prescription:</span> {{ a.treatment.prescription || '—' }}</p>
            <p class="mb-1"><span class="text-muted fw-semibold">Medication:</span> {{ a.treatment.medication || '—' }}</p>
            <p class="mb-1"><span class="text-muted fw-semibold">Tests:</span> {{ a.treatment.tests_done || '—' }}</p>
            <p class="mb-0"><span class="text-muted fw-semibold">Next visit:</span> {{ a.treatment.next_visit_date || '—' }}</p>
          </div>

          <div v-else-if="a.status === 'COMPLETED'" class="small text-muted mt-2 fst-italic">
            No treatment recorded
          </div>

          <div class="mt-3 d-flex gap-3">
            <RouterLink
              v-if="a.status === 'COMPLETED'"
              :to="`/doctor/appointments/${a.app_id}/treatment`"
              class="btn btn-link text-decoration-none small p-0 text-secondary fw-bold"
            >
              {{ a.treatment ? 'Edit' : 'Add treatment' }}
            </RouterLink>

            <button
              v-if="a.status === 'COMPLETED'"
              @click="a.chat_open ? openChat(a) : null"
              class="btn btn-link text-decoration-none small p-0 fw-bold"
              :class="a.chat_open ? 'text-primary' : 'text-muted'"
              :disabled="!a.chat_open"
            >
              <span v-if="a.chat_open">Messages</span>
              <span v-else-if="a.chat_closed">Chat closed</span>
              <span v-else>Expired</span>
            </button>
          </div>

        </div>
      </div>
    </div>
  </div>

  <ChatModal
    v-if="chatAppointment"
    :appointment="chatAppointment"
    role="doctor"
    @close="chatAppointment = null"
    @chat-closed="handleChatClosed"
  />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import DoctorNavbar from '../../components/DoctorNavbar.vue'
import ChatModal from '../../components/ChatModal.vue'
import api from '../../api/index.js'

const appointments   = ref([])
const loading        = ref(false)
const chatAppointment = ref(null)

onMounted(loadHistory)

async function loadHistory() {
  loading.value = true
  try {
    const res          = await api.get('/api/doctor/appointments/history')
    appointments.value = res.data.data.appointments
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

function openChat(a) {
  chatAppointment.value = a
}

function handleChatClosed(appId) {
  const appt = appointments.value.find(a => a.app_id === appId)
  if (appt) {
    appt.chat_closed = true
    appt.chat_open   = false
  }
}

function statusBadge(status) {
  if (status === 'COMPLETED') return 'badge bg-success'
  if (status === 'CANCELLED') return 'badge bg-danger'
  if (status === 'BOOKED') return 'badge bg-primary'
  return 'badge bg-secondary'
}
</script>