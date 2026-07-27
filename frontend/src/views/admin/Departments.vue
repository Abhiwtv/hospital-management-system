<template>
  <div class="min-vh-100 bg-light">
    <AdminNavbar />

    <div class="container py-4" style="max-width: 900px;">
      <div class="d-flex justify-content-end mb-3">
        <button @click="openAddModal" class="btn btn-primary btn-sm fw-medium shadow-sm">
          + Add Department
        </button>
      </div>

      <div class="card border-0 shadow-sm overflow-hidden">
        <table class="table table-hover mb-0 small">
          <thead class="table-light">
            <tr>
              <th class="ps-3 py-2">Name</th>
              <th class="py-2">Description</th>
              <th class="py-2">Doctors</th>
              <th class="pe-3 py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="4" class="text-center py-4 text-muted">Loading...</td>
            </tr>
            <tr v-else-if="departments.length === 0">
              <td colspan="4" class="text-center py-4 text-muted">No data</td>
            </tr>
            <tr v-for="d in departments" :key="d.dep_id">
              <td class="ps-3 align-middle fw-medium">{{ d.dep_name }}</td>
              <td class="align-middle text-muted">{{ d.dep_des || '—' }}</td>
              <td class="align-middle">{{ d.no_docs_registered }}</td>
              <td class="pe-3 align-middle">
                <div class="d-flex gap-3">
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
      <div @click.stop class="card border-0 shadow-lg w-100" style="max-width: 450px;">
        <div class="card-body p-4">
          
          <template v-if="modal === 'form'">
            <h3 class="h6 fw-bold mb-3">{{ editing ? 'Edit Department' : 'Add Department' }}</h3>
            <div class="d-grid gap-3">
              <input v-model="form.dep_name" type="text" placeholder="Name" class="form-control form-control-sm" />
              <textarea v-model="form.dep_des" placeholder="Description" class="form-control form-control-sm" rows="3"></textarea>
            </div>
            <p v-if="formError" class="text-danger small mt-2 mb-0 fw-medium">{{ formError }}</p>
            <div class="d-flex gap-2 mt-4">
              <button @click="submitForm" class="btn btn-primary btn-sm flex-grow-1">{{ editing ? 'Save Changes' : 'Add' }}</button>
              <button @click="closeModal" class="btn btn-outline-secondary btn-sm flex-grow-1">Cancel</button>
            </div>
          </template>

          <template v-if="modal === 'delete'">
            <h3 class="h6 fw-bold text-danger mb-2">Confirm Delete</h3>
            <p class="small mb-4">Are you sure you want to delete <strong>{{ selected.dep_name }}</strong>?</p>
            <div class="d-flex gap-2">
              <button @click="deleteDepartment" class="btn btn-danger btn-sm flex-grow-1">Delete</button>
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

const departments = ref([])
const loading = ref(false)
const modal = ref(null)
const selected = ref({})
const editing = ref(null)
const formError = ref('')
const form = ref({ dep_name: '', dep_des: '' })

onMounted(loadDepartments)

async function loadDepartments() {
  loading.value = true
  try {
    const res = await api.get('/api/admin/departments')
    departments.value = res.data.data.departments
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function openAddModal() {
  editing.value = null
  form.value = { dep_name: '', dep_des: '' }
  formError.value = ''
  modal.value = 'form'
}

function openEditModal(d) {
  editing.value = d
  form.value = { dep_name: d.dep_name, dep_des: d.dep_des || '' }
  formError.value = ''
  modal.value = 'form'
}

function openDeleteModal(d) {
  selected.value = d
  modal.value = 'delete'
}

async function submitForm() {
  formError.value = ''
  if (!form.value.dep_name.trim()) {
    formError.value = 'Name required'
    return
  }
  try {
    if (editing.value) {
      await api.put(`/api/admin/departments/${editing.value.dep_id}`, form.value)
    } else {
      await api.post('/api/admin/departments', form.value)
    }
    closeModal()
    loadDepartments()
  } catch (e) {
    formError.value = e.response?.data?.message || 'Error'
  }
}

async function deleteDepartment() {
  try {
    await api.delete(`/api/admin/departments/${selected.value.dep_id}`)
    closeModal()
    loadDepartments()
  } catch (e) {
    console.error(e)
  }
}

function closeModal() {
  modal.value = null
  editing.value = null
}
</script>