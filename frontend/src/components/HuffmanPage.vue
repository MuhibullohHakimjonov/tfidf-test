<template>
  <div class="p-4">
    <h2 class="text-xl font-bold mb-4">Код Хаффмана для документа</h2>

    <p v-if="loading" class="info">🔄 Загрузка данных...</p>
    <p v-if="error" class="error">❌ {{ error }}</p>

    <div v-if="huffmanData">
      <h3 class="font-semibold mt-4">📜 Словарь Хаффмана:</h3>
      <table class="huffman-table">
        <thead>
          <tr>
            <th>Символ</th>
            <th>Код</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(code, char) in huffmanData.huffman_codes" :key="char">
            <td>{{ char === ' ' ? '[space]' : char }}</td>
            <td>{{ code }}</td>
          </tr>
        </tbody>
      </table>

      <h3 class="font-semibold mt-4">📄 Закодированный текст (encoded_text):</h3>
      <pre class="encoded-text">{{ huffmanData.encoded_text }}</pre>

      <!-- Pagination controls -->
      <div class="mt-4 flex justify-center space-x-4">
        <button
          @click="prevPage"
          :disabled="offset === 0"
          class="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
        >
          Назад
        </button>
        <span>Показано с {{ offset }} до {{ Math.min(offset + limit, huffmanData.total_size) }} из {{ huffmanData.total_size }}</span>
        <button
          @click="nextPage"
          :disabled="huffmanData.is_end"
          class="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
        >
          Вперёд
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from '../api';
import { useRoute } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const route = useRoute();
const authStore = useAuthStore();

const huffmanData = ref(null);
const loading = ref(false);
const error = ref('');
const errorDetails = ref(null);

const limit = 10000; // сколько символов показывать за раз
const offset = ref(0);

const fetchHuffmanData = async () => {
  const documentId = route.params.id;
  loading.value = true;
  error.value = '';
  try {
    const response = await axios.get(`documents/${documentId}/huffman/`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
      params: { offset: offset.value, limit }
    });

    if (!response.data || typeof response.data !== 'object' || !response.data.huffman_codes) {
      throw new Error('Некорректные данные от сервера.');
    }

    huffmanData.value = response.data;
  } catch (err) {
    if (err.response) {
      errorDetails.value = {
        status: err.response.status,
        statusText: err.response.statusText,
        data: err.response.data
      };
      error.value = `Ошибка загрузки данных: ${err.response.status} ${err.response.statusText}`;
    } else if (err.request) {
      error.value = 'Сервер не ответил. Проверьте подключение.';
    } else {
      error.value = `Непредвиденная ошибка: ${err.message}`;
    }
  } finally {
    loading.value = false;
  }
};

const nextPage = () => {
  if (!huffmanData.value.is_end) {
    offset.value += limit;
    fetchHuffmanData();
  }
};

const prevPage = () => {
  if (offset.value >= limit) {
    offset.value -= limit;
    fetchHuffmanData();
  }
};

onMounted(() => {
  fetchHuffmanData();
});
</script>

<style scoped>
.error {
  color: red;
  font-weight: bold;
  margin-top: 10px;
}

.info {
  font-style: italic;
  color: #0077cc;
}

.huffman-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
  font-size: 1rem;
  text-align: center;
}

.huffman-table th {
  background-color: #009879;
  color: white;
  padding: 12px;
  font-weight: bold;
}

.huffman-table td {
  border: 1px solid #ddd;
  padding: 10px;
}

.huffman-table tbody tr:nth-child(even) {
  background-color: #f3f3f3;
}

.encoded-content, .encoded-text {
  background-color: #f8f8f8;
  padding: 10px;
  border-radius: 5px;
  font-family: monospace;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
