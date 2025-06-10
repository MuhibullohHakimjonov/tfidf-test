<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-r from-green-400 to-blue-500">
    <!-- Red Notification Banner -->
    <div v-if="showNotification" class="fixed top-0 left-0 w-full bg-red-600 text-white p-4 flex justify-between items-center z-50 shadow-lg transition-all duration-300" :class="{ 'opacity-0 translate-y-[-100%]': !notificationVisible }">
      <span>{{ notificationMessage }}</span>
      <button @click="closeNotification" class="text-white hover:text-red-200 ml-4">×</button>
    </div>

    <div class="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md animate-fade-in">
      <h2 class="text-3xl font-bold text-center mb-6 text-gray-800">Создать аккаунт</h2>
      <form @submit.prevent="register" class="space-y-4">
        <div>
          <label class="block text-gray-700">Имя пользователя</label>
          <input
            v-model="username"
            type="text"
            placeholder="Введите имя пользователя"
            class="input-field"
          />
        </div>
        <div>
          <label class="block text-gray-700">Email</label>
          <input
            v-model="email"
            type="email"
            placeholder="Введите email"
            class="input-field"
          />
        </div>
        <div>
          <label class="block text-gray-700">Пароль</label>
          <input
            v-model="password"
            type="password"
            placeholder="Введите пароль"
            class="input-field"
          />
        </div>
        <button type="submit" class="btn-primary">Создать аккаунт</button>
      </form>
      <!-- Display success message -->
      <p v-if="message" class="mt-4 text-green-600 text-center">{{ message }}</p>
      <p class="mt-4 text-center text-gray-600">
        Уже есть аккаунт? <router-link to="/login" class="text-blue-600 hover:underline">Войти</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from '../api';
import { useRouter } from 'vue-router';

const router = useRouter();
const username = ref('');
const email = ref('');
const password = ref('');
const message = ref('');
const error = ref('');
const showNotification = ref(false);
const notificationVisible = ref(true);
const notificationMessage = ref('');

const register = async () => {
  message.value = '';
  error.value = '';
  showNotification.value = false; // Reset notification

  // Client-side validation
  if (!username.value.trim() || !email.value.trim() || !password.value) {
    notificationMessage.value = 'Пожалуйста, заполните все поля.';
    showNotification.value = true;
    notificationVisible.value = true;
    setTimeout(() => {
      notificationVisible.value = false;
      setTimeout(() => (showNotification.value = false), 300); // Allow fade-out animation
    }, 5000); // Show for 5 seconds
    return;
  }

  try {
    const response = await axios.post('user/register/', {
      username: username.value,
      email: email.value,
      password: password.value,
    });
    message.value = response.data.message;
    // Redirect to verification page after a short delay
    setTimeout(() => {
      router.push({ name: 'VerifyEmail', query: { email: email.value } });
    }, 1500);
  } catch (err) {
    console.error('Ошибка регистрации:', err);
    // Handle specific email error
    if (err.response?.data?.email && Array.isArray(err.response.data.email)) {
      notificationMessage.value = err.response.data.email[0]; // Display exact error: "custom user with this email already exists."
    } else {
      notificationMessage.value = err.response?.data?.message || 'Ошибка регистрации';
    }
    showNotification.value = true;
    notificationVisible.value = true;
    setTimeout(() => {
      notificationVisible.value = false;
      setTimeout(() => (showNotification.value = false), 300); // Allow fade-out animation
    }, 5000); // Show for 5 seconds
  }
};

const closeNotification = () => {
  notificationVisible.value = false;
  setTimeout(() => (showNotification.value = false), 300); // Allow fade-out animation
};
</script>

<style scoped>
.min-h-screen {
  min-height: 100vh;
}

.flex {
  display: flex;
}

.items-center {
  align-items: center;
}

.justify-center {
  justify-content: center;
}

.bg-gradient-to-r {
  background-image: linear-gradient(to right, #34d399, #3b82f6);
}

.bg-white {
  background-color: #ffffff;
}

.p-8 {
  padding: 2rem;
}

.rounded-2xl {
  border-radius: 1rem;
}

.shadow-xl {
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.w-full {
  width: 100%;
}

.max-w-md {
  max-width: 28rem;
}

.text-3xl {
  font-size: 1.875rem;
}

.font-bold {
  font-weight: 700;
}

.text-center {
  text-align: center;
}

.mb-6 {
  margin-bottom: 1.5rem;
}

.space-y-4 > * + * {
  margin-top: 1rem;
}

.block {
  display: block;
}

.text-gray-700 {
  color: #374151;
}

.input-field {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 1rem;
  color: #1f2937;
  background-color: #f9fafb;
  transition: border-color 0.2s ease-in-out;
}

.input-field:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.btn-primary {
  width: 100%;
  padding: 0.75rem 1rem;
  background-color: #3b82f6;
  color: white;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 0.375rem;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease-in-out;
}

.btn-primary:hover {
  background-color: #2563eb;
}

.mt-4 {
  margin-top: 1rem;
}

.text-green-600 {
  color: #10b981;
}

.text-red-600 {
  color: #dc2626;
}

.text-gray-600 {
  color: #4b5563;
}

.text-blue-600 {
  color: #2563eb;
}

.text-blue-600:hover {
  text-decoration: underline;
}

.animate-fade-in {
  animation: fade-in 0.3s ease-in-out;
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Notification Styles */
.fixed {
  position: fixed;
}

.top-0 {
  top: 0;
}

.left-0 {
  left: 0;
}

.w-full {
  width: 100%;
}

.bg-red-600 {
  background-color: #dc2626;
}

.text-white {
  color: #ffffff;
}

.p-4 {
  padding: 1rem;
}

.flex {
  display: flex;
}

.justify-between {
  justify-content: space-between;
}

.items-center {
  align-items: center;
}

.z-50 {
  z-index: 50;
}

.shadow-lg {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.transition-all {
  transition-property: all;
}

.duration-300 {
  transition-duration: 300ms;
}

.opacity-0 {
  opacity: 0;
}

.translate-y-\[-100\%\] {
  transform: translateY(-100%);
}

.ml-4 {
  margin-left: 1rem;
}

.hover\:text-red-200:hover {
  color: #f87171;
}
</style>