import { createRouter, createWebHistory } from 'vue-router'


import PatientLogin   from '../views/auth/PatientLogin.vue'
import DoctorLogin    from '../views/auth/DoctorLogin.vue'
import AdminLogin     from '../views/auth/AdminLogin.vue'
import PatientRegister from '../views/auth/PatientRegister.vue'
import Home from '../views/auth/Home.vue'

import PatientDashboard    from '../views/patient/Dashboard.vue'
import BookAppointment     from '../views/patient/BookAppointment.vue'
import PatientHistory      from '../views/patient/History.vue'
import PatientProfile      from '../views/patient/Profile.vue'
import PatientDepartments from '../views/patient/Departments.vue'
import DoctorDetail       from '../views/patient/DoctorDetail.vue'
import DoctorDashboard  from '../views/doctor/Dashboard.vue'
import Availability     from '../views/doctor/Availability.vue'
import PatientDetail    from '../views/doctor/PatientDetail.vue'
import TreatmentForm    from '../views/doctor/TreatmentForm.vue'
import DoctorHistory    from '../views/doctor/History.vue'
import AdminDashboard  from '../views/admin/Dashboard.vue'
import AdminDoctors    from '../views/admin/Doctors.vue'
import AdminPatients   from '../views/admin/Patients.vue'
import AdminDepartments from '../views/admin/Departments.vue'
import AdminAppointments from '../views/admin/Appointments.vue'

import UserDetail from '../views/admin/UserDetail.vue'
import UserList from '../views/admin/UserList.vue'

const routes = [
  
  { path: '/', component: Home },

  { path: '/login/patient',  component: PatientLogin },
  { path: '/login/doctor',   component: DoctorLogin },
  { path: '/login/admin',    component: AdminLogin },
  { path: '/register',       component: PatientRegister },

  
  { path: '/patient/dashboard',    component: PatientDashboard,   meta: { role: 'patient' } },
  { path: '/patient/book',         component: BookAppointment,    meta: { role: 'patient' } },
  { path: '/patient/history',      component: PatientHistory,     meta: { role: 'patient' } },
  { path: '/patient/profile',      component: PatientProfile,     meta: { role: 'patient' } },

  
  { path: '/doctor/dashboard',             component: DoctorDashboard, meta: { role: 'doctor' } },
  { path: '/doctor/availability',          component: Availability,    meta: { role: 'doctor' } },
  { path: '/doctor/patients/:id',          component: PatientDetail,   meta: { role: 'doctor' } },
  { path: '/doctor/appointments/:id/treatment', component: TreatmentForm, meta: { role: 'doctor' } },
  { path: '/doctor/history',               component: DoctorHistory,   meta: { role: 'doctor' } },

 
  { path: '/admin/dashboard',    component: AdminDashboard,    meta: { role: 'admin' } },
  { path: '/admin/doctors',      component: AdminDoctors,      meta: { role: 'admin' } },
  { path: '/admin/patients',     component: AdminPatients,     meta: { role: 'admin' } },
  { path: '/admin/departments',  component: AdminDepartments,  meta: { role: 'admin' } },
  { path: '/admin/appointments', component: AdminAppointments, meta: { role: 'admin' } },
  { path: '/patient/departments',     component: PatientDepartments, meta: { role: 'patient' } },
{ path: '/patient/doctors/:id',     component: DoctorDetail,       meta: { role: 'patient' } },
{path:'/admin/users', component: UserDetail, meta: { role: 'admin' }},
{path:'/admin/users/:id', component: UserList, meta: { role: 'admin' }}
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})


router.beforeEach((to, from, next) => {
  const role  = localStorage.getItem('role')
  const token = localStorage.getItem('access_token')

  
  if (to.meta.role) {
    
    if (!token) {
      return next('/login/patient')
    }
    
    if (to.meta.role !== role) {
      return next(`/login/${role === 'admin' ? 'admin' : role}`)
    }
  }

  next()
})

export default router