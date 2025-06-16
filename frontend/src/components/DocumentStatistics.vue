<template>
  <div class="p-4">
    <h2 class="text-xl mb-4">Статистика документа</h2>

    <!-- Select collection -->
    <div class="mb-4" v-if="collections.length > 0">
      <label for="collectionSelect" class="mr-2">Выбрать коллекцию:</label>
      <select id="collectionSelect" v-model="selectedCollectionId" @change="fetchStatistics"
              class="border p-2 rounded">
        <option v-for="collection in collections" :value="collection.id" :key="collection.id">
          {{ collection.name }}
        </option>
      </select>
    </div>

    <div v-if="loading">Загрузка...</div>
    <div v-else-if="error" class="text-red-500">{{ error }}</div>

    <!-- Statistics table -->
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

    <!-- Pagination -->
    <div class="mt-4 flex justify-center space-x-2" v-if="totalPages > 1">
      <button
        @click="changePage(page - 1)"
        :disabled="page === 1"
        class="px-3 py-1 bg-gray-200 rounded disabled:opacity-50"
      >
        Назад
      </button>
      <span>Страница {{ page }} из {{ totalPages }}</span>
      <button
        @click="changePage(page + 1)"
        :disabled="page === totalPages"
        class="px-3 py-1 bg-gray-200 rounded disabled:opacity-50"
      >
        Вперёд
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import axios from '../api';

const route = useRoute();
const statistics = ref([]);
const collections = ref([]);
const selectedCollectionId = ref(null);
const loading = ref(true);
const error = ref(null);
const page = ref(1);
const totalPages = ref(1);

const fetchDocumentCollections = async () => {
  try {
    const res = await axios.get('/documents/');
    const doc = res.data.results.find(d => d.id === parseInt(route.params.id));
    collections.value = doc ? doc.collections : [];
    if (collections.value.length > 0) {
      selectedCollectionId.value = collections.value[0].id;
      await fetchStatistics(); // load statistics for the first collection
    } else {
      error.value = 'Коллекции не найдены для документа.';
    }
  } catch (err) {
    error.value = 'Ошибка загрузки коллекций.';
    console.error(err);
  }
};

const fetchStatistics = async () => {
  if (!selectedCollectionId.value) return;
  loading.value = true;
  error.value = null;
  try {
    const params = { page: page.value, collection_id: selectedCollectionId.value };
    const res = await axios.get(`/documents/${route.params.id}/statistics/`, { params });
    statistics.value = res.data.tfidf_data;
    totalPages.value = res.data.total_pages || 1;
  } catch (err) {
    error.value = 'Ошибка загрузки статистики документа.';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const changePage = (newPage) => {
  if (newPage >= 1 && newPage <= totalPages.value) {
    page.value = newPage;
  }
};

// Watch page & collection changes
watch([page, selectedCollectionId], fetchStatistics);

onMounted(() => {
  fetchDocumentCollections();
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