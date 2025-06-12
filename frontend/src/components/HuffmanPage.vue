<template>
  <div class="p-4">
    <h2 class="text-xl font-bold mb-4">Код Хаффмана для документа</h2>

    <p v-if="loading">Загрузка данных...</p>
    <p v-if="error" class="error">{{ error }}</p>

    <div v-if="huffmanData">
      <h3 class="font-semibold mt-4">Словарь Хаффмана:</h3>
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

      <h3 class="font-semibold mt-4">Закодированное содержимое:</h3>
      <pre class="bg-gray-100 p-2 rounded">{{ huffmanData.encoded_content }}</pre>

      <h3 class="font-semibold mt-4">Закодированный текст (encoded_text):</h3>
      <pre class="bg-gray-100 p-2 rounded break-all">{{ huffmanData.encoded_text }}</pre>
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

onMounted(async () => {
  const documentId = route.params.id;
  loading.value = true;
  try {
    const response = await axios.get(`documents/${documentId}/huffman/`, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    });
    huffmanData.value = response.data;
  } catch (err) {
    error.value = err.response?.data?.error || 'Ошибка загрузки данных.';
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.error {
  color: red;
  margin-top: 10px;
}
.huffman-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}
.huffman-table th,
.huffman-table td {
  border: 1px solid #ccc;
  padding: 8px;
  text-align: center;
}
pre {
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
