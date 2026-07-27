<template>
  <div class="min-vh-100 bg-light">
    <AdminNavbar />

    <div class="container py-4" style="max-width: 1000px;">
      <h2 class="h5 fw-bold mb-4">Overview</h2>

      <div class="row row-cols-2 row-cols-md-4 g-3 mb-4">
        <div class="col">
          <div class="card border-0 shadow-sm p-3 h-100">
            <p class="small text-muted mb-1">Doctors</p>
            <p class="h4 fw-bold mb-0 text-dark">{{ stats.total_doctors }}</p>
          </div>
        </div>
        <div class="col">
          <div class="card border-0 shadow-sm p-3 h-100">
            <p class="small text-muted mb-1">Patients</p>
            <p class="h4 fw-bold mb-0 text-dark">{{ stats.total_patients }}</p>
          </div>
        </div>
        <div class="col">
          <div class="card border-0 shadow-sm p-3 h-100">
            <p class="small text-muted mb-1">Today</p>
            <p class="h4 fw-bold mb-0 text-dark">{{ stats.appointments_today }}</p>
          </div>
        </div>
        <div class="col">
          <div class="card border-0 shadow-sm p-3 h-100">
            <p class="small text-muted mb-1">Blacklisted</p>
            <p class="h4 fw-bold mb-0 text-dark">{{ stats.blacklisted }}</p>
          </div>
        </div>
      </div>

      <div class="row g-4 mb-4">
        <div class="col-md-4">
          <div class="card border-0 shadow-sm p-4 h-100">
            <p class="small fw-semibold mb-3">Status Breakdown</p>
            <div style="height: 220px; position: relative;">
              <canvas ref="doughnutRef"></canvas>
            </div>
          </div>
        </div>

        <div class="col-md-8">
          <div class="card border-0 shadow-sm p-4 h-100">
            <p class="small fw-semibold mb-3">Appointments Trend (Last 7 Days)</p>
            <div style="height: 220px; position: relative;">
              <canvas ref="lineRef"></canvas>
            </div>
          </div>
        </div>
      </div>

      <h2 class="h5 fw-bold mb-3">Recent Appointments</h2>
      <div class="card border-0 shadow-sm mb-4 overflow-hidden">
        <table class="table table-hover mb-0 small">
          <thead class="table-light">
            <tr>
              <th class="ps-4 py-3">Patient</th>
              <th class="py-3">Doctor</th>
              <th class="py-3">Date</th>
              <th class="pe-4 py-3">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="recentAppointments.length === 0">
              <td colspan="4" class="text-center py-4 text-muted">No recent data available</td>
            </tr>
            <tr v-for="a in recentAppointments" :key="a.app_id">
              <td class="ps-4 py-3 align-middle">{{ a.patient_name }}</td>
              <td class="py-3 align-middle">{{ a.doctor_name }}</td>
              <td class="py-3 align-middle">{{ a.date }}</td>
              <td class="pe-4 py-3 align-middle">
                <span :class="statusBadge(a.status)">{{ a.status }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <h2 class="h5 fw-bold mb-3">System Actions</h2>
      <div class="card border-0 shadow-sm p-4 mb-5">
        <div class="d-flex gap-3 mb-2">
          <button @click="triggerReminders" :disabled="jobLoading" class="btn btn-primary btn-sm px-4">
            Trigger Daily Reminders
          </button>
          <button @click="triggerMonthlyReport" :disabled="jobLoading" class="btn btn-success btn-sm px-4">
            Generate Monthly Reports
          </button>
        </div>
        <div class="mt-2 min-h-[24px]">
          <p v-if="jobMessage" class="small text-success fw-medium mb-0">{{ jobMessage }}</p>
          <p v-if="jobError" class="small text-danger fw-medium mb-0">{{ jobError }}</p>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  Chart,
  ArcElement, DoughnutController,
  CategoryScale, LinearScale,
  LineElement, LineController, PointElement,
  Tooltip, Legend
} from 'chart.js'
import AdminNavbar from '../../components/AdminNavbar.vue'
import api from '../../api/index.js'

// Removed BarElement and BarController
Chart.register(
  ArcElement, DoughnutController,
  CategoryScale, LinearScale,
  LineElement, LineController, PointElement,
  Tooltip, Legend
)

const doughnutRef = ref(null)
const lineRef = ref(null)

let doughnutChart = null
let lineChart = null

const stats = ref({
  total_doctors: 0,
  total_patients: 0,
  appointments_today: 0,
  blacklisted: 0,
})

const recentAppointments = ref([])
const jobLoading = ref(false)
const jobMessage = ref('')
const jobError = ref('')

onMounted(async () => {
  await loadDashboard()
  await buildCharts()
})

async function loadDashboard() {
  try {
    const res = await api.get('/api/admin/dashboard')
    const d = res.data.data

    stats.value.total_doctors = d.doctors.length
    stats.value.total_patients = d.patients.length
    stats.value.blacklisted = d.patients.filter(p => p.is_blacklisted).length

    const today = new Date().toISOString().split('T')[0]
    stats.value.appointments_today = d.recent_appointments.filter(
      a => a.date === today && a.status === 'BOOKED'
    ).length

    recentAppointments.value = d.recent_appointments
  } catch (e) {
    console.error("Failed to load dashboard stats", e)
  }
}

async function buildCharts() {
  try {
    const res = await api.get('/api/admin/appointments')
    const appts = res.data.data.appointments

    buildDoughnut(appts)
    buildLine(appts)
  } catch (e) {
    console.error("Failed to load chart data", e)
  }
}

function buildDoughnut(appts) {
  const booked = appts.filter(a => a.status === 'BOOKED').length
  const completed = appts.filter(a => a.status === 'COMPLETED').length
  const cancelled = appts.filter(a => a.status === 'CANCELLED').length

  if (doughnutChart) doughnutChart.destroy()

  doughnutChart = new Chart(doughnutRef.value, {
    type: 'doughnut',
    data: {
      // Appending the numbers directly to the labels so they show in the legend
      labels: [`Booked (${booked})`, `Completed (${completed})`, `Cancelled (${cancelled})`],
      datasets: [{
        data: [booked, completed, cancelled],
        backgroundColor: ['#0d6efd', '#198754', '#dc3545'], // Bootstrap primary, success, danger
        borderWidth: 0 
      }]
    },
    options: { 
      responsive: true, 
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom' }
      }
    }
  })
}

function buildLine(appts) {
  
  const days = []
  for (let i = 6; i >= 0; i--) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    days.push(d.toISOString().split('T')[0])
  }

  const countsByDate = {}
  days.forEach(d => countsByDate[d] = 0)

  appts.forEach(a => {
    if (countsByDate[a.date] !== undefined) countsByDate[a.date]++
  })

  
  const labels = days.map(d => d.split('-').slice(1).join('/')) 
  const values = days.map(d => countsByDate[d])

  if (lineChart) lineChart.destroy()

  lineChart = new Chart(lineRef.value, {
    type: 'line',
    data: {
      labels,
      datasets: [{ 
        label: 'Appointments',
        data: values, 
        borderColor: '#0d6efd',
        backgroundColor: 'rgba(13, 110, 253, 0.1)',
        borderWidth: 2,
        tension: 0.3, // Slight curve
        fill: true
      }]
    },
    options: { 
      responsive: true, 
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, ticks: { stepSize: 1 } }
      }
    }
  })
}

async function triggerReminders() {
  jobMessage.value = ''
  jobError.value = ''
  jobLoading.value = true

  try {
    await api.post('/api/admin/reminders/trigger')
    jobMessage.value = 'Reminders triggered successfully.'
  } catch {
    jobError.value = 'Failed to trigger reminders.'
  } finally {
    jobLoading.value = false
  }
}

async function triggerMonthlyReport() {
  jobMessage.value = ''
  jobError.value = ''
  jobLoading.value = true

  try {
    await api.post('/api/admin/reports/trigger')
    jobMessage.value = 'Monthly reports generated and sent.'
  } catch {
    jobError.value = 'Failed to generate reports.'
  } finally {
    jobLoading.value = false
  }
}

function statusBadge(status) {
  if (status === 'COMPLETED') return 'badge bg-success'
  if (status === 'CANCELLED') return 'badge bg-danger'
  if (status === 'BOOKED') return 'badge bg-primary'
  return 'badge bg-secondary'
}
</script>