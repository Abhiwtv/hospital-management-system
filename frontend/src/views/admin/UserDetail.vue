<template>
    <table>
        <tr v-for="pat in patients" :key="pat.patient_id">
            <td>{{ pat.patient_id }}</td>
            <td>{{ pat.name }}</td>
            <td>{{ pat.email }}</td>
            <td><button @click="viewPatient(pat)">View</button></td>
        </tr>
    </table>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '../../api'
import { useRouter } from 'vue-router'

const router = useRouter()
const patients = ref([])


onMounted(() => {
    loadPatients()
})
async function loadPatients() {
    try {
        const res = await api.get('/api/admin/patients')
        patients.value = res.data.data.patients
    } catch (e) {
        console.error(e)
    }
}
async function viewPatient(pat){
    await router.push(`/admin/users/${pat.patient_id}`)
}


</script>