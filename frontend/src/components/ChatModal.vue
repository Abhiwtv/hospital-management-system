<template>
  <div @click.self="$emit('close')"
    class="position-fixed top-0 start-0 w-100 h-100 bg-dark bg-opacity-50 d-flex align-items-center justify-content-center p-3"
    style="z-index: 1050; backdrop-filter: blur(2px);">

    <div class="card w-100 shadow-lg border-0 d-flex flex-column"
      style="max-width: 500px; height: 85vh; max-height: 600px; border-radius: 1rem;">

      <div class="card-header bg-white d-flex align-items-center justify-content-between p-3 border-bottom">
        <div>
          <h3 class="h6 fw-bold text-dark mb-1">Follow-up Chat</h3>
          <p class="small text-muted mb-0 fw-medium" style="font-size: 0.75rem;">
            Appt: {{ appointment.date }} &middot; {{ appointment.doctor_name || appointment.patient_name }}
          </p>
        </div>
        <div class="d-flex align-items-center gap-3">
          <button
            v-if="role === 'doctor' && !appointment.chat_closed"
            @click="closeChat"
            :disabled="closingChat"
            class="btn btn-link text-danger text-decoration-none fw-bold small p-0 text-uppercase"
            style="font-size: 0.75rem; letter-spacing: 0.5px;"
          >
            {{ closingChat ? 'Closing...' : 'End Chat' }}
          </button>
          
          <button @click="$emit('close')" class="btn-close shadow-none" aria-label="Close"></button>
        </div>
      </div>

      <div v-if="chatClosed" class="alert alert-warning rounded-0 m-0 py-2 text-center small fw-semibold border-start-0 border-end-0 border-top-0">
        This chat has been closed by the doctor.
      </div>
      <div v-else-if="windowExpired" class="alert alert-secondary rounded-0 m-0 py-2 text-center small fw-semibold border-start-0 border-end-0 border-top-0">
        The 48-hour follow-up window has passed.
      </div>
      <div v-else-if="appointment.status !== 'COMPLETED'" class="alert alert-info rounded-0 m-0 py-2 text-center small fw-semibold border-start-0 border-end-0 border-top-0">
        Chat will unlock once the appointment is marked as completed.
      </div>

      <div ref="messagesEl" class="flex-grow-1 overflow-auto p-3 bg-light d-flex flex-column gap-3">
        <div v-if="loading" class="text-center text-muted small fw-medium py-4">
          Loading messages...
        </div>
        <div v-else-if="messages.length === 0" class="text-center text-muted small py-4">
          No messages yet.
          <span v-if="canSend" class="fw-medium text-dark">Be the first to send one.</span>
        </div>

        <div v-for="m in messages" :key="m.id" :class="isOwnMessage(m) ? 'align-self-end' : 'align-self-start'" style="max-width: 85%;">
          <div :class="['p-3 shadow-sm', isOwnMessage(m) ? 'bg-dark text-white rounded-4 rounded-top-end-0' : 'bg-white border text-dark rounded-4 rounded-top-start-0']">
            <p class="mb-1 small" style="line-height: 1.4;">{{ m.message }}</p>
            <p :class="isOwnMessage(m) ? 'text-white-50' : 'text-muted'" class="mb-0 text-end" style="font-size: 0.65rem; font-weight: 600;">
              {{ formatTime(m.created_at) }}
            </p>
          </div>
        </div>
      </div>

      <div v-if="canSend" class="card-footer bg-white p-3 border-top">
        <div class="d-flex gap-2">
          <input
            v-model="newMessage"
            @keydown.enter.prevent="sendMessage"
            type="text"
            placeholder="Type your message..."
            :disabled="sending"
            class="form-control form-control-sm border-secondary-subtle"
          />
          <button
            @click="sendMessage"
            :disabled="sending || !newMessage.trim()"
            class="btn btn-dark btn-sm fw-bold px-4"
          >
            {{ sending ? '...' : 'Send' }}
          </button>
        </div>
        <p v-if="sendError" class="text-danger mt-2 mb-0" style="font-size: 0.75rem; font-weight: 600;">{{ sendError }}</p>
      </div>

      <div v-else class="card-footer bg-light p-3 text-center border-top">
        <span class="text-muted fw-semibold" style="font-size: 0.75rem;">This conversation is read-only.</span>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import api from '../api/index.js'

const props = defineProps({
  appointment: { type: Object, required: true },
  role:        { type: String, required: true },  
})

const emit = defineEmits(['close', 'chat-closed'])

let interval = null

const messages    = ref([])
const newMessage  = ref('')
const loading     = ref(false)
const sending     = ref(false)
const sendError   = ref('')
const closingChat = ref(false)
const chatClosed  = ref(props.appointment.chat_closed || false)
const messagesEl  = ref(null)

const windowExpired = computed(() => {
  const apptDate = new Date(props.appointment.date + 'T00:00:00')
  const cutoff   = new Date(apptDate.getTime() + 48 * 60 * 60 * 1000)
  return new Date() > cutoff
})

const canSend = computed(() =>
  props.appointment.status === 'COMPLETED' && !chatClosed.value && !windowExpired.value
)

function isOwnMessage(m) {
  const myRole = props.role.toUpperCase()
  return m.sender_role === myRole
}

function formatTime(isoStr) {
  if (!isoStr) return ''
  return new Date(isoStr).toLocaleTimeString('en-US', {
    hour: '2-digit', minute: '2-digit'
  })
}

async function scrollToBottom() {
  await nextTick()
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  }
}

async function loadMessages() {
  if (messages.value.length === 0) loading.value = true
  
  try {
    const res = await api.get(`/api/appointments/${props.appointment.app_id}/messages`)
    messages.value = res.data.data.messages
    
    if (!res.data.data.chat_open) {
      chatClosed.value = true
    }
    scrollToBottom()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function sendMessage() {
  if (!newMessage.value.trim() || sending.value) return
  sendError.value = ''
  sending.value   = true
  
  try {
    const res = await api.post(
      `/api/appointments/${props.appointment.app_id}/messages`,
      { message: newMessage.value.trim() }
    )
    messages.value.push(res.data.data)
    newMessage.value = ''
    scrollToBottom()
  } catch (e) {
    sendError.value = e.response?.data?.message || 'Failed to send message.'
  } finally {
    sending.value = false
  }
}

async function closeChat() {
  closingChat.value = true
  try {
    await api.post(`/api/doctor/appointments/${props.appointment.app_id}/close-chat`)
    chatClosed.value = true
    emit('chat-closed', props.appointment.app_id)
  } catch (e) {
    console.error(e)
  } finally {
    closingChat.value = false
  }
}

onMounted(() => {
  loadMessages()
  interval = setInterval(loadMessages, 3000)
})

onUnmounted(() => {
  if (interval) clearInterval(interval)
})
</script>