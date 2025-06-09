<template>
  <div class="profile-page min-h-screen flex items-center justify-center bg-gradient-to-r from-gray-200 to-gray-400 p-4">
    <!-- Notification Banner -->
    <div v-if="showNotification" class="fixed top-10 right-4 bg-green-500 text-white p-4 rounded-lg shadow-lg z-50" :class="notificationType">
      {{ notificationMessage }}
    </div>

    <div class="card bg-white p-8 rounded-2xl shadow-xl w-full max-w-md animate-fade-in">
      <h2 class="header text-3xl font-bold text-center mb-6 text-gray-800">Профиль пользователя</h2>

      <!-- Profile Update Form -->
      <form @submit.prevent="updateProfile" class="space-y-4">
        <div>
          <label class="label">Имя пользователя</label>
          <input v-model="form.username" type="text" class="input-field" />
        </div>
        <div>
          <label class="label">Email</label>
          <input v-model="form.email" type="email" class="input-field" disabled />
        </div>
        <button type="submit" class="btn-primary w-full">Сохранить изменения</button>
      </form>

      <!-- Action Buttons -->
      <div class="mt-6 space-y-3">
        <button @click="showPasswordModal = true" class="btn-secondary w-full">Изменить пароль</button>
        <button @click="confirmDeleteAccount" class="btn-danger w-full">Удалить аккаунт</button>
        <button @click="logout" class="btn-secondary w-full">Выйти</button>
      </div>

      <!-- Password Change Modal -->
      <div v-if="showPasswordModal" class="modal">
        <div class="modal-content">
          <h3 class="modal-header text-xl font-bold mb-4 text-gray-800">Изменить пароль</h3>
          <form @submit.prevent="changePassword" class="space-y-4">
            <div>
              <label class="label">Старый пароль</label>
              <input v-model="passwordForm.oldPassword" type="password" class="input-field" />
            </div>
            <div>
              <label class="label">Новый пароль</label>
              <input v-model="passwordForm.newPassword" type="password" class="input-field" />
            </div>
            <div>
              <label class="label">Подтверждение</label>
              <input v-model="passwordForm.confirmPassword" type="password" class="input-field" />
            </div>
            <div class="flex justify-end space-x-2">
              <button type="button" @click="showPasswordModal = false" class="btn-secondary">Отмена</button>
              <button type="submit" class="btn-primary">Сохранить</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from '../api';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const user = ref({});
const form = ref({
  username: '',
  email: ''
});
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
});
const showPasswordModal = ref(false);
const showNotification = ref(false);
const notificationMessage = ref('');
const notificationType = ref('bg-green-500');

const fetchUserDetails = async () => {
  try {
    const response = await axios.get('api/user/user/me/');
    user.value = response.data;
    form.value.username = response.data.username;
    form.value.email = response.data.email;
  } catch (err) {
    console.error('Ошибка загрузки профиля:', err);
    triggerNotification('Не удалось загрузить профиль.', 'bg-red-500');
  }
};

const updateProfile = async () => {
  try {
    const response = await axios.put('api/user/user/me/', form.value);
    user.value = response.data;
    triggerNotification('Изменения успешно сохранены.', 'bg-green-500');
  } catch (err) {
    console.error('Ошибка обновления профиля:', err);
    triggerNotification('Не удалось обновить профиль.', 'bg-red-500');
  }
};

const changePassword = async () => {
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    triggerNotification('Пароли не совпадают', 'bg-red-500');
    return;
  }
  try {
    await axios.put('api/user/user/change-password/', {
      old_password: passwordForm.value.oldPassword,
      new_password: passwordForm.value.newPassword,
    });
    triggerNotification('Пароль успешно изменён.', 'bg-green-500');
    showPasswordModal.value = false;
    passwordForm.value.oldPassword = '';
    passwordForm.value.newPassword = '';
    passwordForm.value.confirmPassword = '';
  } catch (err) {
    console.error('Ошибка изменения пароля:', err);
    if (err.response?.data?.new_password && Array.isArray(err.response.data.new_password)) {
      // Combine multiple error messages into a single notification
      triggerNotification('Этот пароль слишком короткий. Он должен содержать не менее 8 символов.Этот пароль слишком распространен.Этот пароль полностью состоит из цифр.', 'bg-red-500');
    } else if (err.response?.data?.old_password) {
      triggerNotification(err.response.data.old_password[0], 'bg-red-500');
    } else {
      triggerNotification('Не удалось изменить пароль.', 'bg-red-500');
    }
  }
};

const confirmDeleteAccount = async () => {
  try {
    await axios.delete('api/user/user/me/');
    triggerNotification('Аккаунт удален', 'bg-green-500');
    authStore.clearToken();
    router.push('/login');
  } catch (err) {
    console.error('Ошибка удаления аккаунта:', err);
    if (err.response?.data?.password) {
      triggerNotification(err.response.data.password, 'bg-red-500');
    } else {
      triggerNotification('Не удалось удалить аккаунт. Проверьте пароль.', 'bg-red-500');
    }
  }
};

const logout = () => {
  authStore.clearToken();
  router.push('/login');
};

const triggerNotification = (message, color) => {
  notificationMessage.value = message;
  notificationType.value = color;
  showNotification.value = true;
  setTimeout(() => {
    showNotification.value = false;
  }, 5000); // Extended to 5 seconds for multiple error messages
};

onMounted(() => {
  fetchUserDetails();
});
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(to right, #e5e7eb, #f3f4f6);
}

.card {
  background-color: #ffffff;
  padding: 2rem;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  width: 100%;
  max-width: 400px;
}

.header {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  text-align: center;
  margin-bottom: 1.5rem;
}

.label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #4b5563;
  margin-bottom: 0.5rem;
}

.input-field {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 1rem;
  color: #1f2937;
  background-color: #f9fafb;
  transition: border-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.input-field:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.btn-primary {
  background-color: #3b82f6;
  color: #ffffff;
  padding: 0.75rem 1rem;
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
  background-color: #6b7280;
  color: #ffffff;
  padding: 0.75rem 1rem;
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

.btn-danger {
  background-color: #ef4444;
  color: #ffffff;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 0.375rem;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease-in-out;
}

.btn-danger:hover {
  background-color: #dc2626;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(0, 0, 0, 0.5);
}

.modal-content {
  background-color: #ffffff;
  padding: 2rem;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  width: 100%;
  max-width: 400px;
}

.bg-green-500 {
  background-color: #10b981;
}

.bg-red-500 {
  background-color: #ef4444;
}

.fixed {
  position: fixed;
}

.top-10 {
  top: 2.5rem;
}

.right-4 {
  right: 1rem;
}

.p-4 {
  padding: 1rem;
}

.rounded-lg {
  border-radius: 0.5rem;
}

.shadow-lg {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.text-white {
  color: #ffffff;
}

.z-50 {
  z-index: 50;
}

.animate-fade-in {
  animation: fade-in 0.3s ease-in-out;
}

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
</style>