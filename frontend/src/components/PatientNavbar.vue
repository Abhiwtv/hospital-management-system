<template>
  <nav class="navbar navbar-expand bg-white border-bottom px-4 py-2">
    <div class="container-fluid px-0">
      
      <div class="navbar-brand d-flex align-items-center gap-2 mb-0">
        <span class="fs-5 fw-bold text-dark">City Hospital</span>
      </div>

      <div class="navbar-nav flex-row align-items-center gap-1 ms-4 me-auto">
        <RouterLink
          v-for="link in links" :key="link.to"
          :to="link.to"
          :class="[
            'nav-link px-3 py-2 rounded text-decoration-none small fw-medium transition-all',
            $route.path === link.to
              ? 'bg-primary bg-opacity-10 text-primary'
              : 'text-secondary'
          ]"
        >
          {{ link.label }}
        </RouterLink>
      </div>

      <button @click="handleLogout" class="btn btn-link text-danger text-decoration-none fw-medium small p-0">
        Logout
      </button>

    </div>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const router = useRouter()
const auth   = useAuthStore()

const links = [
  { to: '/patient/dashboard',   label: 'Home'     },
  { to: '/patient/departments', label: 'Book'     },
  { to: '/patient/history',     label: 'History'  },
  { to: '/patient/profile',     label: 'Profile'  },
]

function handleLogout() {
  auth.logout()
  router.push('/')
}
</script>