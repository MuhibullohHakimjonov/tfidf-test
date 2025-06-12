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
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRoute } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const route = useRoute();
const authStore = useAuthStore();

const huffmanData = ref(null);
const loading = ref(false);
const error = ref('');
const errorDetails = ref(null); // Store detailed error information

onMounted(async () => {
  const documentId = route.params.id;
  loading.value = true;
  try {
    const response = await axios.get(`documents/${documentId}/huffman/`, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    });

    // Ensure valid JSON response before setting data
    if (!response.data || typeof response.data !== 'object' || !response.data.huffman_codes) {
      throw new Error('Некорректные данные от сервера. Ожидался JSON-объект.');
    }

    huffmanData.value = response.data;
  } catch (err) {
    if (err.response) {
      // Capture detailed server response
      errorDetails.value = {
        status: err.response.status,
        statusText: err.response.statusText,
        data: err.response.data
      };
      error.value = `Ошибка загрузки данных: ${err.response.status} ${err.response.statusText}`;
    } else if (err.request) {
      // Capture request-related errors (no response from server)
      error.value = 'Сервер не ответил. Проверьте подключение.';
    } else {
      // Capture unexpected errors
      error.value = `Непредвиденная ошибка: ${err.message}`;
    }
  } finally {
    loading.value = false;
  }
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
