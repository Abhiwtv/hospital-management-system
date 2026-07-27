<template>
    <h1>USER: {{ user.patient_name }}</h1>
    <h3>EMAIL: {{ user.email }}</h3>
    <h3>Patient ID: {{ user.patient_id }}</h3>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '../../api'
import { useRoute } from 'vue-router'

const route = useRoute()
const user = ref({})


onMounted(() => {
    loadUser()
})

async function loadUser() {
    try {
        const res = await api.get(`/api/admin/users/${route.params.id}`)
        user.value = res.data.data.user
    } catch (e) {
        console.error(e)
    }
}
</script>