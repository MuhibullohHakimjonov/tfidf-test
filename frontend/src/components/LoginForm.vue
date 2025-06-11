<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-r from-blue-400 to-indigo-500">
    <!-- Red Notification Banner -->
    <div v-if="showNotification" class="fixed top-0 left-0 w-full bg-red-600 text-white p-4 flex justify-between items-center z-50 shadow-lg transition-all duration-300" :class="{ 'opacity-0 translate-y-[-100%]': !notificationVisible }">
      <span>{{ notificationMessage }}</span>
    </div>

    <div class="bg-white p-8 rounded-2xl shadow-2xl w-full max-w-md animate-fade-in">
      <h2 class="text-3xl font-bold text-center text-gray-800 mb-6">Добро пожаловать</h2>
      <form @submit.prevent="login" class="space-y-4">
        <div>
          <label class="block text-gray-700 mb-1">Email</label>
          <input
            v-model="email"
            placeholder="Введите email"
            class="w-full border border-gray-300 rounded-xl px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-gray-700 mb-1">Пароль</label>
          <input
            type="password"
            v-model="password"
            placeholder="Введите пароль"
            class="w-full border border-gray-300 rounded-xl px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <button
          type="submit"
          class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-xl transition"
        >
          Войти
        </button>
      </form>
      <p class="mt-4 text-center text-gray-600">
        Нет аккаунта? 
        <router-link to="/register" class="text-blue-600 hover:underline">
          Создайте учетную запись
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from '../api';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth'; // <-- Import the store

const email = ref('');
const password = ref('');
const router = useRouter();
const authStore = useAuthStore(); // <-- Initialize the store
const showNotification = ref(false);
const notificationVisible = ref(true);
const notificationMessage = ref('');

const login = async () => {
  showNotification.value = false; // Reset notification
  try {
    const response = await axios.post('http://localhost:8000/api/user/login/', {
      email: email.value,
      password: password.value,
    });
    
    // Update both localStorage AND the Pinia store
    authStore.setToken(response.data.access); // <-- This updates the reactive state
    router.push('/');
    
  } catch (error) {
    console.error('Ошибка входа:', error);
    notificationMessage.value = error.response?.data?.detail || 'Неверный email или пароль';
    showNotification.value = true;
    notificationVisible.value = true;
    setTimeout(() => {
      notificationVisible.value = false;
      setTimeout(() => (showNotification.value = false), 300); // Allow fade-out animation
    }, 5000); // Show for 5 seconds
  }
};

</script>

<style scoped>
/* Base layout for the page */
.min-h-screen {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(to right, #e5e7eb, #f3f4f6); /* Neutral gray gradient */
}

/* Card container */
.bg-white {
  background-color: #ffffff;
  padding: 2rem;
  border-radius: 0.5rem; /* Softer rounded corners */
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  width: 100%;
  max-width: 400px; /* Slightly wider for balance */
}

/* Heading */
.text-3xl {
  font-size: 1.5rem; /* Slightly smaller for a cleaner look */
  font-weight: 600;
  color: #1f2937; /* Dark gray for text */
  text-align: center;
  margin-bottom: 1.5rem;
}

/* Form labels */
.text-gray-700 {
  font-size: 0.875rem; /* Smaller, professional font size */
  font-weight: 500;
  color: #4b5563;
  margin-bottom: 0.5rem;
}

/* Input fields */
input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db; /* Light gray border */
  border-radius: 0.375rem; /* Softer corners */
  font-size: 1rem;
  color: #1f2937;
  background-color: #f9fafb; /* Subtle background */
  transition: border-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

input:focus {
  outline: none;
  border-color: #3b82f6; /* Blue focus border */
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); /* Subtle glow */
}

/* Placeholder text */
input::placeholder {
  color: #9ca3af; /* Light gray placeholder */
}

/* Submit button */
button {
  width: 100%;
  padding: 0.75rem 1rem;
  background-color: #3b82f6; /* Standard blue */
  color: #ffffff;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 0.375rem;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease-in-out;
}

button:hover {
  background-color: #2563eb; /* Darker blue on hover */
}

button:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
}

/* Form spacing */
.space-y-4 > * + * {
  margin-top: 1rem;
}

/* Animation for card */
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-in-out;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .bg-white {
    padding: 1.5rem;
    margin: 1rem;
  }
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