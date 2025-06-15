<template>
  <div class="p-4">
    <h2 class="text-xl mb-4">Содержимое документа</h2>
    <div v-if="loading">Загрузка...</div>
    <div v-else-if="error" class="text-red-500">{{ error }}</div>
    <pre v-else class="bg-gray-100 p-4 rounded">{{ content }}</pre>
    <button
      v-if="!isEnd && !loadingMore"
      @click="loadMore"
      class="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
    >
      Загрузить ещё
    </button>
    <div v-if="loadingMore">Загрузка ещё...</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import axios from '../api';

const route = useRoute();
const content = ref('');
const loading = ref(true);
const error = ref(null);
const offset = ref(0);
const limit = 5000; // загружать по 5000 символов
const totalSize = ref(0);
const isEnd = ref(false);
const loadingMore = ref(false);

const loadContent = async (isLoadMore = false) => {
  try {
    const response = await axios.get(`documents/${route.params.id}/`, {
      params: { offset: offset.value, limit }
    });
    if (isLoadMore) {
      content.value += response.data.content;
    } else {
      content.value = response.data.content;
    }
    totalSize.value = response.data.total_size;
    isEnd.value = response.data.is_end;
    offset.value += limit;
  } catch (err) {
    error.value = 'Не удалось загрузить содержимое документа.';
    console.error(err);
  }
};

onMounted(async () => {
  loading.value = true;
  await loadContent();
  loading.value = false;
});

const loadMore = async () => {
  loadingMore.value = true;
  await loadContent(true);
  loadingMore.value = false;
};
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

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: monospace;
}

button {
  cursor: pointer;
}
</style>
