<template>
  <div class="app-container">
    <!-- Navbar shown except on /login -->
    <Navbar v-if="showNavbar" />
    <div class="content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import Navbar from './components/Navbar.vue';

const route = useRoute();

// Hide Navbar on /login route
const showNavbar = computed(() => route.path !== '/login');
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background: linear-gradient(to right, #e5e7eb, #f3f4f6); /* Gradient background */
  display: flex;
  flex-direction: column;
}

.content {
  flex: 1;
  display: flex;
  justify-content: center;
  padding: 20px;
}

.content > * {
  width: 100%;
  max-width: 600px; /* Match card width */
}
</style>