<template>
  <div class="min-vh-100 bg-light">
    <DoctorNavbar />

    <div class="container py-5" style="max-width: 800px;">
      <div class="mb-4">
        <h2 class="h5 fw-bold text-dark">Set Your Availability</h2>
        <p class="small text-muted mt-1">
          Toggle the slots you are available for over the next 7 days. Click Save when done.
        </p>
      </div>

      <div v-if="loading" class="text-center text-muted py-5">Loading...</div>

      <div v-else class="d-flex flex-column gap-3">
        <div
          v-for="day in days" :key="day.date"
          class="card border-0 shadow-sm p-3 d-flex flex-row align-items-center justify-content-between"
        >
          <div style="width: 150px;">
            <p class="small fw-bold text-dark mb-0">{{ day.label }}</p>
            <p class="text-muted mb-0" style="font-size: 0.75rem;">{{ day.date }}</p>
          </div>
          <div class="d-flex gap-2">
            <button
              v-for="slot in slots" :key="slot"
              @click="toggleSlot(day.date, slot)"
              :class="[
                'btn btn-sm fw-medium px-3',
                map[day.date]?.[slot] ? 'btn-primary' : 'btn-outline-secondary'
              ]"
            >
              {{ slot }}
            </button>
          </div>
        </div>
      </div>

      <div class="mt-4 d-flex align-items-center gap-3">
        <button
          @click="save"
          :disabled="saving"
          class="btn btn-primary px-4 fw-bold shadow-sm"
        >
          {{ saving ? 'Saving...' : 'Save Availability' }}
        </button>
        <p v-if="successMsg" class="small text-success fw-medium mb-0">{{ successMsg }}</p>
        <p v-if="errorMsg"   class="small text-danger fw-medium mb-0">{{ errorMsg }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import DoctorNavbar from '../../components/DoctorNavbar.vue'
import api from '../../api/index.js'

const days       = ref([])
const map        = ref({})   
const slots      = ['Morning', 'Afternoon', 'Evening']
const loading    = ref(false)
const saving     = ref(false)
const successMsg = ref('')
const errorMsg   = ref('')

onMounted(loadAvailability)

async function loadAvailability() {
  loading.value = true
  try {
    const res = await api.get('/api/doctor/availability')
    const d   = res.data.data

    days.value = d.dates.map(dateStr => ({
      date:  dateStr,
      label: new Date(dateStr + 'T00:00:00').toLocaleDateString('en-US', {
        weekday: 'short', month: 'short', day: 'numeric'
      }),
    }))
    map.value = {}
    for (const dateStr of d.dates) {
      map.value[dateStr] = {
        Morning:   d.slots_map[dateStr]?.Morning   ?? false,
        Afternoon: d.slots_map[dateStr]?.Afternoon ?? false,
        Evening:   d.slots_map[dateStr]?.Evening   ?? false,
      }
    }
  } catch (e) {
    errorMsg.value = 'Failed to load availability.'
    console.error(e)
  } finally {
    loading.value = false
  }
}

function toggleSlot(date, slot) {
  if (!map.value[date]) map.value[date] = {}
  map.value[date][slot] = !map.value[date][slot]
}

async function save() {
  saving.value     = true
  successMsg.value = ''
  errorMsg.value   = ''

  const availability = {}
  for (const [date, slotsObj] of Object.entries(map.value)) {
    availability[date] = Object.entries(slotsObj)
      .filter(([, enabled]) => enabled)
      .map(([slot]) => slot)
  }

  try {
    await api.post('/api/doctor/availability', { availability })
    successMsg.value = 'Availability saved successfully.'
    setTimeout(() => successMsg.value = '', 3000)
  } catch (e) {
    errorMsg.value = 'Failed to save. Please try again.'
    console.error(e)
  } finally {
    saving.value = false
  }
}
</script>