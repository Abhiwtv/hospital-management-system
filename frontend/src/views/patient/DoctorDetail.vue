<template>
  <div class="min-vh-100 bg-light">
    <PatientNavbar />

    <div class="container py-4 py-md-5" style="max-width: 800px;">

      <button @click="router.back()" class="btn btn-link text-decoration-none p-0 text-muted small fw-bold text-uppercase mb-4">
        &larr; Return to list
      </button>

      <div v-if="loading" class="py-5 text-muted small border-top">
        Loading practitioner profile...
      </div>

      <template v-else>
        <section class="mb-5 bg-white p-4 p-md-5 rounded shadow-sm">
          <div class="border-bottom pb-4 mb-4">
            <h2 class="h3 fw-bold text-dark mb-1">Dr. {{ doctor.doctor_name }}</h2>
            <p class="small text-muted text-uppercase fw-bold mb-0">
              {{ doctor.doctor_type }} &middot; {{ doctor.department_name }}
            </p>
          </div>

          <div class="row g-4 mb-4">
            <div class="col-6 col-md-4">
              <p class="small fw-bold text-muted text-uppercase mb-1" style="font-size: 0.75rem;">Qualification</p>
              <p class="small text-dark fw-medium mb-0">{{ doctor.doctor_qualification || 'General Practitioner' }}</p>
            </div>
            <div class="col-6 col-md-4">
              <p class="small fw-bold text-muted text-uppercase mb-1" style="font-size: 0.75rem;">Experience</p>
              <p class="small text-dark fw-medium mb-0">{{ doctor.doctor_experience ? doctor.doctor_experience + ' Years Clinical' : '—' }}</p>
            </div>
          </div>

          <p v-if="doctor.doctor_description" class="small text-muted mb-0" style="line-height: 1.6;">
            {{ doctor.doctor_description }}
          </p>
        </section>

        <section class="mb-5 pb-5">
          <h3 class="h6 fw-bold text-dark text-uppercase mb-4">Schedule Availability</h3>

          <div v-if="availability.length === 0" class="card border border-2 border-dashed bg-white p-5 text-center shadow-none">
            <p class="small text-muted mb-0">No active booking windows found for this practitioner.</p>
          </div>

          <div v-else class="d-flex flex-column gap-5">
            <div v-for="(slots, date) in groupedSlots" :key="date" class="ps-3 border-start border-2 border-primary">
              <p class="fw-bold text-dark mb-3">{{ formatDate(date) }}</p>
              
              <div class="row row-cols-2 row-cols-sm-3 row-cols-md-4 g-2">
                <div v-for="slot in slots" :key="slot.availability_id" class="col">
                  <button
                    @click="selectSlot(slot)"
                    :disabled="slotBookings[slot.availability_id] >= 10"
                    class="btn w-100 h-100 text-start shadow-sm border"
                    :class="[
                      slotBookings[slot.availability_id] >= 10
                        ? 'btn-light text-muted border-light'
                        : selectedSlot?.availability_id === slot.availability_id
                          ? 'btn-dark'
                          : 'btn-white text-dark border-secondary-subtle'
                    ]"
                  >
                    <span class="d-block small fw-bold">{{ slot.slot_name }}</span>
                    <span class="d-block text-opacity-75 fst-italic mb-2" style="font-size: 0.7rem;">{{ slot.start_time }}</span>
                    
                    <div class="pt-2 border-top border-opacity-25" :class="selectedSlot?.availability_id === slot.availability_id ? 'border-light' : 'border-secondary'">
                      <span v-if="slotBookings[slot.availability_id] >= 10" class="d-block fw-bold text-uppercase" style="font-size: 0.65rem;">
                        Full
                      </span>
                      <span v-else class="d-block fw-bold text-uppercase" style="font-size: 0.65rem;">
                        {{ 10 - (slotBookings[slot.availability_id] || 0) }} Spots
                      </span>
                    </div>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>

        <div v-if="selectedSlot" class="position-fixed bottom-0 start-0 w-100 bg-white border-top shadow-lg p-3 z-3">
          <div class="container d-flex flex-column flex-md-row align-items-md-center justify-content-between gap-3" style="max-width: 800px;">
            <div>
              <p class="small fw-bold text-muted text-uppercase mb-1" style="font-size: 0.7rem;">Review Appointment</p>
              <p class="small text-dark mb-0">
                {{ formatDate(selectedSlot.date) }} at {{ selectedSlot.start_time }} with <strong>Dr. {{ doctor.doctor_name }}</strong>
              </p>
            </div>
            
            <div class="d-flex align-items-center gap-3">
              <button @click="selectedSlot = null" class="btn btn-link text-muted text-decoration-none small fw-bold p-0">
                Reset
              </button>
              <button @click="bookAppointment" :disabled="booking" class="btn btn-dark fw-bold text-uppercase px-4 py-2" style="font-size: 0.8rem; letter-spacing: 0.5px;">
                {{ booking ? 'Processing...' : 'Confirm Appointment' }}
              </button>
            </div>
          </div>
          
          <div v-if="bookingError || bookingSuccess" class="container mt-2" style="max-width: 800px;">
             <p v-if="bookingError" class="text-danger small fw-bold mb-0">{{ bookingError }}</p>
             <p v-if="bookingSuccess" class="text-success small fw-bold mb-0">{{ bookingSuccess }}</p>
          </div>
        </div>

      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PatientNavbar from '../../components/PatientNavbar.vue'
import api from '../../api/index.js'

const route  = useRoute()
const router = useRouter()

const doctor       = ref({})
const availability = ref([])
const slotBookings = ref({})
const selectedSlot = ref(null)
const loading      = ref(false)
const booking      = ref(false)
const bookingError   = ref('')
const bookingSuccess = ref('')

const groupedSlots = computed(() => {
  const groups = {}
  for (const av of availability.value) {
    if (!groups[av.date]) groups[av.date] = []
    groups[av.date].push(av)
  }
  return groups
})

onMounted(loadDoctor)

async function loadDoctor() {
  loading.value = true
  try {
    const res          = await api.get(`/api/patient/doctors/${route.params.id}`)
    doctor.value       = res.data.data.doctor
    availability.value = res.data.data.availability
    slotBookings.value = res.data.data.slot_bookings
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

function selectSlot(slot) {
  selectedSlot.value   = slot
  bookingError.value   = ''
  bookingSuccess.value = ''
}

async function bookAppointment() {
  booking.value      = true
  bookingError.value = ''
  try {
    await api.post(`/api/patient/book/${selectedSlot.value.availability_id}`)
    bookingSuccess.value = '✓ Appointment booked! Check your dashboard.'
    selectedSlot.value   = null
    loadDoctor()
  } catch (e) {
    bookingError.value = e.response?.data?.message || 'Booking failed. Please try again.'
  } finally {
    booking.value = false
  }
}

function formatDate(dateStr) {
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('en-US', {
    weekday: 'long', month: 'short', day: 'numeric'
  })
}
</script>