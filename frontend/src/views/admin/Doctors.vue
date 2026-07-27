<template>
  <div class="min-vh-100 bg-light">
    <AdminNavbar />

    <div class="container py-4" style="max-width: 1140px;">
      <div class="d-flex flex-wrap gap-2 justify-content-between mb-3">
        <input
          v-model="searchQuery"
          @input="handleSearch"
          type="text"
          placeholder="Search doctors..."
          class="form-control form-control-sm shadow-sm"
          style="max-width: 250px;"
        />
        <button @click="openAddModal" class="btn btn-primary btn-sm fw-medium shadow-sm">
          + Add Doctor
        </button>
      </div>

      <div class="card border-0 shadow-sm overflow-hidden">
        <table class="table table-hover mb-0 small">
          <thead class="table-light">
            <tr>
              <th class="ps-3 py-2">Name</th>
              <th class="py-2">Username</th>
              <th class="py-2">Type</th>
              <th class="py-2">Dept</th>
              <th class="py-2">Exp</th>
              <th class="pe-3 py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="6" class="text-center py-4 text-muted">Loading...</td>
            </tr>
            <tr v-else-if="doctors.length === 0">
              <td colspan="6" class="text-center py-4 text-muted">No data</td>
            </tr>
            <tr v-for="d in doctors" :key="d.doctor_id">
              <td class="ps-3 align-middle fw-medium">Dr. {{ d.doctor_name }}</td>
              <td class="align-middle text-muted">{{ d.doctor_username }}</td>
              <td class="align-middle">{{ d.doctor_type || '—' }}</td>
              <td class="align-middle">{{ d.department_name || '—' }}</td>
              <td class="align-middle">{{ d.doctor_experience ? d.doctor_experience + ' yrs' : '—' }}</td>
              <td class="pe-3 align-middle">
                <div class="d-flex gap-2">
                  <button @click="openViewModal(d)" class="btn btn-link text-primary text-decoration-none p-0 small fw-bold">View</button>
                  <button @click="openEditModal(d)" class="btn btn-link text-warning text-decoration-none p-0 small fw-bold">Edit</button>
                  <button @click="openDeleteModal(d)" class="btn btn-link text-danger text-decoration-none p-0 small fw-bold">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="modal" @click="closeModal" class="position-fixed top-0 start-0 w-100 h-100 bg-dark bg-opacity-50 d-flex align-items-center justify-content-center p-3" style="z-index: 1050;">
      <div @click.stop class="card border-0 shadow-lg w-100" style="max-width: 450px; max-height: 90vh; overflow-y: auto;">
        <div class="card-body p-4">

          <template v-if="modal === 'form'">
            <h3 class="h6 fw-bold mb-3 border-bottom pb-2">{{ editing ? 'Edit Doctor' : 'Add Doctor' }}</h3>
            <div class="d-grid gap-2 small">
              <input v-model="form.name" placeholder="Name" class="form-control form-control-sm" />
              <input v-model="form.username" placeholder="Username" class="form-control form-control-sm" />
              <input v-if="!editing" v-model="form.password" type="password" placeholder="Password" class="form-control form-control-sm" />
              <input v-model="form.doctor_email" placeholder="Email" class="form-control form-control-sm" />
              <input v-model="form.type" placeholder="Type (e.g. Surgeon)" class="form-control form-control-sm" />
              <input v-model="form.qualification" placeholder="Qualification (e.g. MD)" class="form-control form-control-sm" />
              <input v-model="form.experience" type="number" placeholder="Experience (Years)" class="form-control form-control-sm" />
              <textarea v-model="form.description" placeholder="Description" class="form-control form-control-sm" rows="2"></textarea>
              <select v-model="form.dep_id" class="form-select form-select-sm">
                <option value="">No Department</option>
                <option v-for="dept in departments" :key="dept.dep_id" :value="dept.dep_id">
                  {{ dept.dep_name }}
                </option>
              </select>
            </div>
            <p v-if="formError" class="text-danger small mt-2 mb-0 fw-medium">{{ formError }}</p>
            <div class="d-flex gap-2 mt-4">
              <button @click="submitForm" class="btn btn-primary btn-sm flex-grow-1">{{ editing ? 'Save' : 'Add' }}</button>
              <button @click="closeModal" class="btn btn-outline-secondary btn-sm flex-grow-1">Cancel</button>
            </div>
          </template>

          <template v-if="modal === 'view'">
            <h3 class="h6 fw-bold mb-3 border-bottom pb-2">Doctor Details</h3>
            <div class="small mb-3">
              <p class="mb-1"><strong>Name:</strong> Dr. {{ selected.doctor_name }}</p>
              <p class="mb-1"><strong>Username:</strong> {{ selected.doctor_username }}</p>
              <p class="mb-1"><strong>Email:</strong> {{ selected.doctor_email || '—' }}</p>
              <p class="mb-1"><strong>Type:</strong> {{ selected.doctor_type || '—' }}</p>
              <p class="mb-1"><strong>Qualification:</strong> {{ selected.doctor_qualification || '—' }}</p>
              <p class="mb-1"><strong>Experience:</strong> {{ selected.doctor_experience ? selected.doctor_experience + ' years' : '—' }}</p>
              <p class="mb-1"><strong>Department:</strong> {{ selected.department_name || '—' }}</p>
              <p class="mb-1"><strong>Description:</strong> {{ selected.doctor_description || '—' }}</p>
            </div>
            <button @click="closeModal" class="btn btn-outline-secondary btn-sm w-100">Close</button>
          </template>

          <template v-if="modal === 'delete'">
            <h3 class="h6 fw-bold text-danger mb-2">Confirm Delete</h3>
            <p class="small mb-4">Delete Dr. <strong>{{ selected.doctor_name }}</strong> from the system?</p>
            <div class="d-flex gap-2">
              <button @click="deleteDoctor" class="btn btn-danger btn-sm flex-grow-1">Delete</button>
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

const doctors = ref([])
const departments = ref([])
const loading = ref(false)
const searchQuery = ref('')
const modal = ref(null)
const selected = ref({})
const editing = ref(null)
const formError = ref('')

const form = ref({
  name: '', username: '', password: '', doctor_email: '',
  type: '', qualification: '', experience: '', description: '', dep_id: '',
})

onMounted(() => {
  loadDoctors()
  loadDepartments()
})

async function loadDoctors() {
  loading.value = true
  try {
    const res = await api.get('/api/admin/doctors')
    doctors.value = res.data.data.doctors
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function loadDepartments() {
  try {
    const res = await api.get('/api/admin/departments')
    departments.value = res.data.data.departments
  } catch (e) {
    console.error(e)
  }
}

async function handleSearch() {
  if (!searchQuery.value.trim()) return loadDoctors()
  try {
    const res = await api.get('/api/admin/doctors/search', { params: { q: searchQuery.value } })
    doctors.value = res.data.data.doctors
  } catch (e) {
    console.error(e)
  }
}

function openAddModal() {
  editing.value = null
  form.value = { name: '', username: '', password: '', doctor_email: '', type: '', qualification: '', experience: '', description: '', dep_id: '' }
  formError.value = ''
  modal.value = 'form'
}

function openEditModal(d) {
  editing.value = d
  form.value = {
    name: d.doctor_name,
    username: d.doctor_username,
    doctor_email: d.doctor_email || '',
    type: d.doctor_type || '',
    qualification: d.doctor_qualification || '',
    experience: d.doctor_experience || '',
    description: d.doctor_description || '',
    dep_id: d.dep_id || '',
  }
  formError.value = ''
  modal.value = 'form'
}

function openViewModal(d) {
  selected.value = d
  modal.value = 'view'
}

function openDeleteModal(d) {
  selected.value = d
  modal.value = 'delete'
}

async function submitForm() {
  formError.value = ''
  try {
    if (editing.value) {
      await api.put(`/api/admin/doctors/${editing.value.doctor_id}`, form.value)
    } else {
      await api.post('/api/admin/doctors', form.value)
    }
    closeModal()
    loadDoctors()
  } catch (e) {
    formError.value = e.response?.data?.message || 'Error'
  }
}

async function deleteDoctor() {
  try {
    await api.delete(`/api/admin/doctors/${selected.value.doctor_id}`)
    closeModal()
    loadDoctors()
  } catch (e) {
    console.error(e)
  }
}

function closeModal() {
  modal.value = null
  editing.value = null
}
</script>