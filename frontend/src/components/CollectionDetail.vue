<template>
  <div class="p-4">
    <h2 v-if="loading" class="text-xl mb-4">Загрузка...</h2>
    <div v-else-if="error" class="text-red-500 text-center">{{ error }}</div>
    <div v-else>
      <h2 class="text-xl mb-4">{{ collection.collections_id.name }}</h2>
      
      <!-- Documents in Collection -->
      <h3 class="text-lg mb-2">Документы в коллекции</h3>
      <table
        v-if="collection.collections_id.documents && collection.collections_id.documents.length"
        class="w-full border border-collapse text-sm mb-6"
      >
        <thead class="bg-gray-100">
          <tr>
            <th class="border p-2 text-left">Название документа</th>
            <th class="border p-2 text-left">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="doc in collection.collections_id.documents" :key="doc.id">
            <td class="border p-2">
              <router-link
                :to="`/documents/${doc.id}`"
                class="text-blue-500 hover:underline"
              >
                {{ doc.name }}
              </router-link>
            </td>
            <td class="border p-2 flex justify-end">
              <!-- Delete button with trash icon -->
              <button @click="removeDocument(doc.id)" class="btn btn-danger">
                🗑️
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else class="text-sm text-gray-600 mb-6">
        Нет документов в этой коллекции.
      </p>

      <!-- Collection Statistics (unchanged) -->
      <h3 class="text-lg mb-2">Статистика коллекции</h3>
      <p class="text-sm text-gray-600 mb-4">
        Количество документов: {{ collection.documents_count }}
      </p>
      <h4 class="text-md mb-2">Топ слова (по убыванию IDF)</h4>
      <table class="w-full border border-collapse text-sm">
        <thead class="bg-gray-100">
          <tr>
            <th class="border p-2 text-left">Слово</th>
            <th class="border p-2 text-left">TF</th>
            <th class="border p-2 text-left">IDF</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="word in sortedTopWords" :key="word.word">
            <td class="border p-2">{{ word.word }}</td>
            <td class="border p-2">{{ word.total_tf.toFixed(6) }}</td>
            <td class="border p-2">{{ word.idf.toFixed(6) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from '../api';
import { useAuthStore } from '../stores/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const isAuthenticated = computed(() => authStore.isAuthenticated);

const collection = ref({
  documents_count: 0,
  top_words: [],
  collections_id: {
    name: ''
  }
});

const loading = ref(true);
const error = ref(null);

const fetchCollection = async () => {
  try {
    const response = await axios.get(`api/collections/${route.params.id}/`);
    collection.value = response.data;
  } catch (err) {
    console.error('Не удалось загрузить коллекцию:', err);
    error.value = 'Не удалось загрузить коллекцию.';
  }
};

const fetchCollectionStatistics = async () => {
  try {
    const response = await axios.get(`api/collections/${route.params.id}/statistics/`);
    collection.value.documents_count = response.data.documents_count || 0;
    collection.value.top_words = response.data.top_words || [];
    if (!collection.value.collections_id.name) {
      const collResponse = await axios.get(`api/collections/${route.params.id}/`);
      collection.value.collections_id.name = collResponse.data.collections_id.name;
    }
  } catch (err) {
    console.error('Не удалось загрузить статистику коллекции:', err);
    error.value = 'Не удалось загрузить статистику коллекции.';
  }
};

const sortedTopWords = computed(() => {
  return [...collection.value.top_words].sort((a, b) => b.idf - a.idf);
});

const removeDocument = async (documentId) => {
  if (!confirm('Вы уверены, что хотите удалить этот документ из коллекции?')) return;
  try {
    await axios.delete(`api/collection/${route.params.id}/${documentId}/delete/`);
    collection.value.collections_id.documents = collection.value.collections_id.documents.filter(
      doc => doc.id !== documentId
    );
    await fetchCollectionStatistics();
    showNotification('Документ удален из коллекции!', 'green');
  } catch (err) {
    console.error('Не удалось удалить документ:', err);
    showNotification('Не удалось удалить документ!', 'red');
  }
};

const showNotification = (message, backgroundColor) => {
  const notification = document.createElement("div");
  notification.innerText = message;
  notification.style.position = "fixed";
  notification.style.top = "60px";
  notification.style.right = "10px";
  notification.style.background = backgroundColor;
  notification.style.color = "white";
  notification.style.padding = "20px";
  notification.style.borderRadius = "6px";
  notification.style.zIndex = "100";
  
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.remove();
  }, 3000);
};

onMounted(async () => {
  if (!isAuthenticated.value) {
    console.warn('Пользователь не авторизован, перенаправляем на страницу входа.');
    router.push('/login');
    return;
  }

  loading.value = true;
  error.value = null;
  await Promise.all([fetchCollection(), fetchCollectionStatistics()]);
  loading.value = false;
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

.text-lg {
  font-size: 1.125rem;
  font-weight: 500;
  color: #1f2937;
}

.text-md {
  font-size: 1rem;
  font-weight: 500;
  color: #1f2937;
}

.text-sm.text-gray-600 {
  color: #4b5563;
  font-size: 0.875rem;
  line-height: 1.25rem;
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

.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  color: #ffffff;
  transition: background-color 0.2s ease-in-out;
}

.btn-danger {
  background: #e63946;
  color: white;
  padding: 8px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: bold;
  transition: opacity 0.2s;
}

.btn-danger:hover {
  opacity: 0.7;
}


.text-blue-500 {
  color: #3b82f6;
}

.text-blue-500:hover {
  text-decoration: underline;
}

.mb-4 {
  margin-bottom: 1rem;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.mb-6 {
  margin-bottom: 1.5rem;
}

@media (max-width: 640px) {
  .p-4 > div {
    padding: 1.5rem;
    margin: 1rem;
  }

  table {
    font-size: 0.75rem;
  }

  th, td {
    padding: 0.5rem;
  }
}
</style>