<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-r from-green-400 to-blue-500">
    <!-- Red Notification Banner for Errors -->
    <div v-if="showErrorNotification" class="fixed top-0 left-0 w-full bg-red-600 text-white p-4 flex justify-between items-center z-50 shadow-lg transition-all duration-300" :class="{ 'opacity-0 translate-y-[-100%]': !errorNotificationVisible }">
      <span>{{ errorNotificationMessage }}</span>
      <button @click="closeErrorNotification" class="text-white hover:text-red-200 ml-4">×</button>
    </div>
    <!-- Green Notification Banner for Success -->
    <div v-if="showSuccessNotification" class="fixed top-0 left-0 w-full bg-green-600 text-white p-4 flex justify-between items-center z-50 shadow-lg transition-all duration-300" :class="{ 'opacity-0 translate-y-[-100%]': !successNotificationVisible }">
      <span>{{ successNotificationMessage }}</span>
      <button @click="closeSuccessNotification" class="text-white hover:text-green-200 ml-4">×</button>
    </div>

    <div class="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md animate-fade-in">
      <h2 class="text-3xl font-bold text-center mb-6 text-gray-800">Подтвердите Email</h2>
      <p class="text-center text-gray-600 mb-4">
        Мы отправили код подтверждения на {{ email }}.
      </p>
      <form @submit.prevent="verifyEmail" class="space-y-4">
        <div>
          <label class="block text-gray-700">Код подтверждения</label>
          <input
            v-model="code"
            type="text"
            placeholder="Введите код"
            class="input-field"
          />
        </div>
        <button type="submit" class="btn-primary">Подтвердить</button>
      </form>
      <button @click="resendCode" class="btn-secondary mt-4">Отправить код еще раз</button>
      <p class="mt-4 text-center text-gray-600">
        Уже есть аккаунт? <router-link to="/login" class="text-blue-600 hover:underline">Войти</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from '../api';

const router = useRouter();
const route = useRoute();
const email = ref(route.query.email || '');
const code = ref('');
const showErrorNotification = ref(false);
const errorNotificationVisible = ref(true);
const errorNotificationMessage = ref('');
const showSuccessNotification = ref(false);
const successNotificationVisible = ref(true);
const successNotificationMessage = ref('');

const verifyEmail = async () => {
  showErrorNotification.value = false;
  showSuccessNotification.value = false;

  if (!code.value.trim()) {
    errorNotificationMessage.value = 'Пожалуйста, введите код подтверждения.';
    showErrorNotification.value = true;
    errorNotificationVisible.value = true;
    setTimeout(() => {
      errorNotificationVisible.value = false;
      setTimeout(() => (showErrorNotification.value = false), 300);
    }, 5000);
    return;
  }

  try {
    const response = await axios.post('api/user/verify-email/', {
      email: email.value,
      code: code.value,
    });
    successNotificationMessage.value = response.data.message || 'Email успешно подтвержден!';
    showSuccessNotification.value = true;
    successNotificationVisible.value = true;
    setTimeout(() => {
      successNotificationVisible.value = false;
      setTimeout(() => (showSuccessNotification.value = false), 300);
    }, 5000);
    // Redirect to login after success
    setTimeout(() => {
      router.push('/login');
    }, 1500);
  } catch (err) {
    console.error('Ошибка подтверждения:', err);
    errorNotificationMessage.value = err.response?.data?.message || 'Ошибка подтверждения';
    showErrorNotification.value = true;
    errorNotificationVisible.value = true;
    setTimeout(() => {
      errorNotificationVisible.value = false;
      setTimeout(() => (showErrorNotification.value = false), 300);
    }, 5000);
  }
};

const resendCode = async () => {
  showErrorNotification.value = false;
  showSuccessNotification.value = false;

  try {
    const response = await axios.post('api/user/resend-code/', {
      email: email.value,
    });
    successNotificationMessage.value = response.data.message || 'Новый код отправлен на ваш email.';
    showSuccessNotification.value = true;
    successNotificationVisible.value = true;
    setTimeout(() => {
      successNotificationVisible.value = false;
      setTimeout(() => (showSuccessNotification.value = false), 300);
    }, 5000);
  } catch (err) {
    console.error('Ошибка повторной отправки кода:', err);
    errorNotificationMessage.value = err.response?.data?.message || 'Пожалуйста, подождите 1 минуту перед повторной отправкой кода..';
    showErrorNotification.value = true;
    errorNotificationVisible.value = true;
    setTimeout(() => {
      errorNotificationVisible.value = false;
      setTimeout(() => (showErrorNotification.value = false), 300);
    }, 5000);
  }
};

const closeErrorNotification = () => {
  errorNotificationVisible.value = false;
  setTimeout(() => (showErrorNotification.value = false), 300);
};

const closeSuccessNotification = () => {
  successNotificationVisible.value = false;
  setTimeout(() => (showSuccessNotification.value = false), 300);
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

.mb-4 {
  margin-bottom: 1rem;
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

.btn-secondary {
  width: 100%;
  padding: 0.75rem 1rem;
  background-color: #6b7280;
  color: white;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 0.375rem;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease-in-out;
}

.btn-secondary:hover {
  background-color: #4b5563;
}

.mt-4 {
  margin-top: 1rem;
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

.bg-green-600 {
  background-color: #16a34a;
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

.hover\:text-green-200:hover {
  color: #86efac;
}
</style>