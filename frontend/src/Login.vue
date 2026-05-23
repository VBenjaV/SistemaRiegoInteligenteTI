<template>
  <div class="login-page">
    <div class="login-box">
      <h1>Sistema de Riego</h1>
      
      <!-- Form Login -->
      <form @submit.prevent="handleLogin" v-if="!isRegistering">
        <input v-model="email" type="email" placeholder="Email" required />
        <input v-model="password" type="password" placeholder="Contraseña" required />
        <button type="submit" :disabled="loading">{{ loading ? 'Cargando...' : 'Entrar' }}</button>
        
        <p class="toggle">¿No tienes cuenta? <a href="#" @click.prevent="isRegistering = true">Regístrate</a></p>
      </form>

      <!-- Form Register -->
      <form @submit.prevent="handleRegister" v-else>
        <input v-model="email" type="email" placeholder="Email" required />
        <input v-model="password" type="password" placeholder="Contraseña (8+ caracteres)" required minlength="8" />
        <input v-model="passwordConfirm" type="password" placeholder="Confirmar contraseña" required minlength="8" />
        <button type="submit" :disabled="loading || password !== passwordConfirm">
          {{ loading ? 'Registrando...' : 'Registrarse' }}
        </button>
        
        <p class="toggle">¿Ya tienes cuenta? <a href="#" @click.prevent="isRegistering = false">Inicia sesión</a></p>
      </form>

      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="success">{{ success }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { login, register } from './api'

const emit = defineEmits(['login-success'])

const email = ref('')
const password = ref('')
const passwordConfirm = ref('')
const loading = ref(false)
const error = ref(null)
const success = ref(null)
const isRegistering = ref(false)

async function handleLogin() {
  error.value = null
  loading.value = true
  try {
    await login(email.value, password.value)
    emit('login-success')
  } catch (e) {
    error.value = 'Email o contraseña incorrectos'
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  if (password.value !== passwordConfirm.value) {
    error.value = 'Las contraseñas no coinciden'
    return
  }
  
  error.value = null
  loading.value = true
  try {
    await register(email.value, password.value)
    success.value = 'Registrado. Verifica tu email y luego inicia sesión.'
    setTimeout(() => {
      isRegistering.value = false
      email.value = ''
      password.value = ''
      passwordConfirm.value = ''
      success.value = null
    }, 2000)
  } catch (e) {
    error.value = e.data?.detail || 'Error en el registro'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  width: 100%;
  max-width: 350px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

h1 {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
}

form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

input {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
  font-family: inherit;
}

input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

button {
  padding: 0.75rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: 0.2s;
}

button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.toggle {
  text-align: center;
  font-size: 0.9rem;
  color: #666;
}

.toggle a {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
}

.toggle a:hover {
  text-decoration: underline;
}

.error {
  color: #d32f2f;
  background: #ffebee;
  padding: 0.75rem;
  border-radius: 5px;
  margin-top: 1rem;
}

.success {
  color: #388e3c;
  background: #e8f5e9;
  padding: 0.75rem;
  border-radius: 5px;
  margin-top: 1rem;
}
</style>

