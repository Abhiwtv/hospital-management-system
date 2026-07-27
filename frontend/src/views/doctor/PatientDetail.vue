<template>
  <div class="min-vh-100 bg-white">
    <DoctorNavbar />

    <div class="container py-4" style="max-width: 800px;">

      <button @click="router.back()" class="btn btn-link text-muted text-decoration-none small fw-bold px-0 mb-4">
        &larr; Back
      </button>

      <div v-if="loading" class="text-center text-muted py-5">
        Loading...
      </div>

      <template v-else>

        <div class="card border-0 shadow-sm p-4 mb-4 bg-light">
          <div class="d-flex justify-content-between align-items-start mb-3">
            <div>
              <h2 class="h5 fw-bold text-dark mb-0">
                {{ patient.patient_name }}
              </h2>
              <p class="small text-muted mb-0">
                @{{ patient.patient_username }}
              </p>
            </div>

            <span class="badge" :class="patient.is_blacklisted ? 'bg-danger' : 'bg-success'">
              {{ patient.is_blacklisted ? 'Blacklisted' : 'Active' }}
            </span>
          </div>

          <div class="small text-dark mb-3">
            <p class="mb-1"><strong>Email:</strong> {{ patient.email || '—' }}</p>
            <p class="mb-1"><strong>Phone:</strong> {{ patient.phone || '—' }}</p>
            <p class="mb-1"><strong>Age:</strong> {{ patient.age || '—' }} &middot; {{ patient.gender || '—' }}</p>
            <p class="mb-0"><strong>Address:</strong> {{ patient.address || '—' }}</p>
          </div>

          <button
            @click="toggleBlacklist"
            class="btn btn-outline-secondary btn-sm fw-bold align-self-start"
            style="width: fit-content;"
          >
            {{ patient.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}
          </button>
        </div>

        <div class="card border-0 shadow-sm p-4 mb-4">
          <div class="d-flex justify-content-between align-items-center border-bottom pb-2 mb-3">
            <h3 class="h6 fw-bold text-dark mb-0">
              Clinical Summary
            </h3>
            <button
              @click="generateSummary"
              :disabled="summaryLoading"
              class="btn btn-outline-primary btn-sm fw-bold"
            >
              {{ summaryLoading ? 'Generating...' : 'Generate' }}
            </button>
          </div>

          <div v-if="!summary && !summaryLoading && !summaryError" class="small text-muted">
            Generate a summary from patient history.
          </div>

          <div v-if="summaryLoading" class="small text-muted fst-italic">
            Analysing history...
          </div>

          <div v-if="summaryError" class="small text-danger fw-medium">
            {{ summaryError }}
          </div>

          <div v-if="summary" class="small text-dark" style="white-space: pre-wrap;">
            {{ summary }}
          </div>
        </div>

        <h3 class="h6 fw-bold text-muted text-uppercase mb-3 mt-4">
          Appointments
        </h3>

        <div v-if="appointments.length === 0" class="small text-muted text-center py-4">
          No appointments found.
        </div>

        <div v-else class="d-flex flex-column gap-3">
          <div
            v-for="a in appointments"
            :key="a.app_id"
            class="card border border-secondary-subtle shadow-none p-3"
          >
            <div class="d-flex justify-content-between mb-2">
              <div>
                <p class="small fw-bold text-dark mb-0">
                  {{ a.date }} &middot; {{ a.time }}
                </p>
                <p class="text-muted mb-0" style="font-size: 0.75rem;">
                  {{ a.visit_type }}
                </p>
              </div>
              <span :class="statusBadge(a.status)">
                {{ a.status }}
              </span>
            </div>

            <div v-if="a.treatment" class="small bg-light p-2 rounded mt-2 border">
              <p class="mb-1"><strong>Diagnosis:</strong> {{ a.treatment.diagnosis || '—' }}</p>
              <p class="mb-1"><strong>Prescription:</strong> {{ a.treatment.prescription || '—' }}</p>
              <p class="mb-1"><strong>Medication:</strong> {{ a.treatment.medication || '—' }}</p>
              <p class="mb-0"><strong>Tests:</strong> {{ a.treatment.tests_done || '—' }}</p>
            </div>

            <div v-else class="small text-muted mt-2 fst-italic">
              No treatment recorded
            </div>
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

const patient        = ref({})
const appointments   = ref([])
const loading        = ref(false)

const summary        = ref('')
const summaryLoading = ref(false)
const summaryError   = ref('')

onMounted(loadPatient)

async function loadPatient() {
  loading.value = true
  try {
    const res          = await api.get(`/api/doctor/patients/${route.params.id}`)
    patient.value      = res.data.data.patient
    appointments.value = res.data.data.appointments
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

async function generateSummary() {
  summaryLoading.value = true
  summaryError.value   = ''
  summary.value        = ''
  try {
    const res      = await api.post(`/api/doctor/patients/${route.params.id}/summary`)
    summary.value  = res.data.data.summary
  } catch (e) {
    summaryError.value = e.response?.data?.message
      || 'Failed to generate summary. Make sure the patient has completed appointments with treatment recorded.'
  } finally {
    summaryLoading.value = false
  }
}

async function toggleBlacklist() {
  const action = patient.value.is_blacklisted ? 'unblacklist' : 'blacklist'
  try {
    await api.post(`/api/doctor/patients/${route.params.id}/${action}`)
    loadPatient()
  } catch (e) { console.error(e) }
}

function statusBadge(status) {
  if (status === 'COMPLETED') return 'badge bg-success'
  if (status === 'CANCELLED') return 'badge bg-danger'
  if (status === 'BOOKED') return 'badge bg-primary'
  return 'badge bg-secondary'
}
</script>