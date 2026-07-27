<template>
  <div class="min-vh-100 bg-light d-flex align-items-center justify-content-center p-3">
    
    <div class="container" style="max-width: 1000px;">
      
      <div class="row row-cols-1 row-cols-md-3 g-4 justify-content-center">
        
        <div class="col">
          <div 
            @click="router.push('/login/patient')" 
            class="card h-100 border-2 shadow-sm p-5 text-center role-card"
            style="cursor: pointer; border-radius: 2rem; aspect-ratio: 1/1;"
          >
            <div class="d-flex align-items-center justify-content-center mb-4 flex-grow-1">
              <img 
                src="https://cdn1.iconfinder.com/data/icons/doctor-5/100/01-1Patient_1-1024.png" 
                style="width: 110px; height: 110px; object-fit: contain;" 
                alt="Patient"
              >
            </div>
            <h2 class="h4 fw-bold text-dark">Patient</h2>
          </div>
        </div>

        <div class="col">
          <div 
            @click="router.push('/login/doctor')" 
            class="card h-100 border-2 shadow-sm p-5 text-center role-card"
            style="cursor: pointer; border-radius: 2rem; aspect-ratio: 1/1;"
          >
            <div class="d-flex align-items-center justify-content-center mb-4 flex-grow-1">
              <img 
                src="https://img.icons8.com/ios-filled/100/000000/doctor-male.png" 
                style="width: 110px; height: 110px; object-fit: contain;" 
                alt="Doctor"
              >
            </div>
            <h2 class="h4 fw-bold text-dark">Doctor</h2>
          </div>
        </div>

        <div class="col">
          <div 
            @click="router.push('/login/admin')" 
            class="card h-100 border-2 shadow-sm p-5 text-center role-card"
            style="cursor: pointer; border-radius: 2rem; aspect-ratio: 1/1;"
          >
            <div class="d-flex align-items-center justify-content-center mb-4 flex-grow-1">
              <img 
                src="https://img.icons8.com/ios-filled/100/000000/admin-settings-male.png" 
                style="width: 110px; height: 110px; object-fit: contain;" 
                alt="Admin"
              >
            </div>
            <h2 class="h4 fw-bold text-dark">Admin</h2>
          </div>
        </div>

      </div>

      <div class="mt-5 text-center">
        <p class="text-muted small">
          New patient? 
          <RouterLink to="/register" class="text-primary fw-bold text-decoration-none ms-1">
            Create an account
          </RouterLink>
        </p>
      </div>

    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<style scoped>
.role-card {
  transition: all 0.2s ease-in-out;
  border-color: #dee2e6;
}
.role-card:hover {
  border-color: #0d6efd !important;
  transform: translateY(-5px);
  background-color: #f8f9fa;
}
</style>