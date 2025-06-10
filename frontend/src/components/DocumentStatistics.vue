<template>
  <div class="p-4">
    <h2 class="text-xl mb-4">Статистика документа</h2>
    <div v-if="loading">Загрузка...</div>
    <div v-else-if="error" class="text-red-500">{{ error }}</div>
    <table v-else class="w-full border border-collapse text-sm">
      <thead class="bg-gray-100">
        <tr>
          <th class="border p-2 text-left">Слово</th>
          <th class="border p-2 text-left">TF</th>
          <th class="border p-2 text-left">IDF</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(stat, index) in statistics" :key="index">
          <td class="border p-2">{{ stat.word }}</td>
          <td class="border p-2">{{ stat.tf.toFixed(6) }}</td>
          <td class="border p-2">{{ stat.idf.toFixed(6) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import axios from '../api';

const route = useRoute();
const statistics = ref([]);
const loading = ref(true);
const error = ref(null);

onMounted(async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await axios.get(`/api/documents/${route.params.id}/statistics/`);
    statistics.value = response.data.tfidf_data; // Access the tfidf_data field
  } catch (err) {
    error.value = 'Не удалось загрузить статистику документа.';
    console.error(err);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.p-4 {
  min-height: calc(100vh - 4rem);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(to right, #e5e7eb, #f3f4f6);
}

.p-4 > div {
  background-color: #ffffff;
  padding: 2rem;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  width: 100%;
  max-width: 600px;
}

.text-xl {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  text-align: center;
  margin-bottom: 1.5rem;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

th, td {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  text-align: left;
  font-size: 0.875rem;
  color: #1f2937;
}

th {
  background-color: #f3f4f6;
  font-weight: 500;
}

tbody tr:nth-child(even) {
  background-color: #f9fafb;
}

tbody tr:hover {
  background-color: #f1f5f9;
}
</style>