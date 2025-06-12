<template>
  <nav class="p-4 bg-gray-100 flex justify-center space-x-4 border-b">
    <router-link to="/" class="nav-link">Загрузить</router-link>
    <router-link to="/documents" class="nav-link">Документы</router-link>
    <router-link to="/collections" class="nav-link">Коллекции</router-link>
    <router-link v-if="isAuthenticated" to="/metrics" class="nav-link">Метрики</router-link>
    <router-link v-if="isAuthenticated" to="/profile" class="nav-link ml-auto">Профиль</router-link>
    <div class="ml-auto" v-else>
      <router-link to="/login" class="nav-link">Войти</router-link>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const router = useRouter();
const authStore = useAuthStore();
const isAuthenticated = computed(() => authStore.isAuthenticated);

function handleLogout() {
  authStore.clearToken();
  router.push('/login');
}
</script>

<style scoped>
nav {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f3f4f6;
  border-bottom: 1px solid #e5e7eb;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.nav-link {
  text-decoration: none;
  color: #1f2937;
  font-weight: 500;
  padding: 0.5rem 1rem;
  transition: color 0.2s ease-in-out;
}
.nav-link:hover {
  color: #3b82f6;
}
.ml-auto {
  margin-left: auto;
}
</style>
