<template>
  <div class="login-wrapper">
    <div class="login-container">
      <!-- Tabs -->
      <div class="tabs">
        <button 
          class="tab" 
          :class="{ active: !isRegistering }"
          @click="isRegistering = false"
        >
          Iniciar Sesión
        </button>
        <button 
          class="tab" 
          :class="{ active: isRegistering }"
          @click="isRegistering = true"
        >
          Registro
        </button>
      </div>

      <!-- Login Form -->
      <form v-if="!isRegistering" @submit.prevent="handleLogin" class="form-content">
        <h2>Bienvenido de nuevo</h2>
        <p class="subtitle">Ingresa tus credenciales para continuar</p>

        <div class="form-group">
          <label>Correo electrónico</label>
          <input 
            v-model="email" 
            type="email" 
            placeholder="ejemplo@correo.com" 
            required 
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label>Contraseña</label>
          <div class="password-input">
            <input 
              v-model="password" 
              :type="showPassword ? 'text' : 'password'"
              placeholder="••••••••" 
              required 
              :disabled="loading"
            />
            <button 
              type="button" 
              class="toggle-password"
              @click="showPassword = !showPassword"
            >
              {{ showPassword ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>
        </div>

        <div class="forgot-password">
          <a href="#">¿Olvidaste tu contraseña?</a>
        </div>

        <button type="submit" class="btn-login" :disabled="loading">
          {{ loading ? 'Iniciando sesión...' : 'Iniciar Sesión' }}
        </button>

        <p v-if="error" class="error-message">{{ error }}</p>
      </form>

      <!-- Register Form -->
      <form v-else @submit.prevent="handleRegister" class="form-content">
        <h2>Crear cuenta</h2>
        <p class="subtitle">Regístrate para acceder al sistema</p>

        <div class="form-group">
          <label>Correo electrónico</label>
          <input 
            v-model="email" 
            type="email" 
            placeholder="ejemplo@correo.com" 
            required 
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label>Contraseña</label>
          <div class="password-input">
            <input 
              v-model="password" 
              :type="showPassword ? 'text' : 'password'"
              placeholder="Mínimo 8 caracteres" 
              required 
              minlength="8"
              :disabled="loading"
            />
            <button 
              type="button" 
              class="toggle-password"
              @click="showPassword = !showPassword"
            >
              {{ showPassword ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>
        </div>

        <div class="form-group">
          <label>Confirmar contraseña</label>
          <div class="password-input">
            <input 
              v-model="passwordConfirm" 
              :type="showPassword ? 'text' : 'password'"
              placeholder="Repite tu contraseña" 
              required 
              minlength="8"
              :disabled="loading"
            />
            <button 
              type="button" 
              class="toggle-password"
              @click="showPassword = !showPassword"
            >
              {{ showPassword ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>
        </div>

        <button 
          type="submit" 
          class="btn-login" 
          :disabled="loading || password !== passwordConfirm"
        >
          {{ loading ? 'Registrando...' : 'Registrarse' }}
        </button>

        <p v-if="error" class="error-message">{{ error }}</p>
        <p v-if="success" class="success-message">{{ success }}</p>
      </form>

      <!-- System Status -->
      <div class="system-status">
        <span class="status-dot"></span>
        Sistema activo
      </div>
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
const showPassword = ref(false)

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
  success.value = null
  loading.value = true
  try {
    await register(email.value, password.value)
    success.value = 'Registro exitoso. Verifica tu email y luego inicia sesión.'
    setTimeout(() => {
      isRegistering.value = false
      email.value = ''
      password.value = ''
      passwordConfirm.value = ''
      success.value = null
    }, 2500)
  } catch (e) {
    error.value = e.data?.detail || 'Error en el registro'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  background: linear-gradient(135deg, #1a1f3a 0%, #16213e 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  z-index: 1000;
}

.login-container {
  background: #1e293b;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  width: 100%;
  max-width: 420px;
  overflow: hidden;
}

/* Tabs */
.tabs {
  display: flex;
  border-bottom: 1px solid #334155;
}

.tab {
  flex: 1;
  padding: 1rem;
  background: none;
  border: none;
  color: #94a3b8;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.tab:hover {
  color: #cbd5e1;
  background: rgba(255, 255, 255, 0.02);
}

.tab.active {
  color: #60a5fa;
}

.tab.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: #60a5fa;
}

/* Form Content */
.form-content {
  padding: 2rem;
}

h2 {
  font-size: 1.5rem;
  color: #f1f5f9;
  margin: 0 0 0.5rem 0;
  font-weight: 600;
}

.subtitle {
  color: #94a3b8;
  margin: 0 0 1.5rem 0;
  font-size: 0.95rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

label {
  display: block;
  color: #e2e8f0;
  font-weight: 500;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

input {
  width: 100%;
  padding: 0.75rem;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 6px;
  color: #f1f5f9;
  font-size: 0.95rem;
  transition: all 0.2s ease;
  box-sizing: border-box;
}

input::placeholder {
  color: #64748b;
}

input:focus {
  outline: none;
  border-color: #60a5fa;
  box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.1);
  background: #0f172a;
}

input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.password-input {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input input {
  padding-right: 2.5rem;
}

.toggle-password {
  position: absolute;
  right: 0.75rem;
  background: none;
  border: none;
  cursor: pointer;
  color: #94a3b8;
  font-size: 1.1rem;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toggle-password:hover {
  color: #cbd5e1;
}

.forgot-password {
  text-align: right;
  margin-bottom: 1.5rem;
}

.forgot-password a {
  color: #10b981;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  transition: color 0.2s ease;
}

.forgot-password a:hover {
  color: #34d399;
}

.btn-login {
  width: 100%;
  padding: 0.85rem;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 1rem;
}

.btn-login:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);
}

.btn-login:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid #ef4444;
  color: #fca5a5;
  padding: 0.75rem;
  border-radius: 6px;
  font-size: 0.9rem;
  margin: 0;
}

.success-message {
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid #10b981;
  color: #86efac;
  padding: 0.75rem;
  border-radius: 6px;
  font-size: 0.9rem;
  margin: 0;
}

/* System Status */
.system-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.02);
  color: #10b981;
  font-size: 0.9rem;
  font-weight: 500;
}

.status-dot {
  width: 8px;
  height: 8px;
  background: #10b981;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* Responsive */
@media (max-width: 480px) {
  .login-container {
    max-width: 100%;
    border-radius: 0;
  }

  .form-content {
    padding: 1.5rem;
  }

  h2 {
    font-size: 1.25rem;
  }
}
</style>

