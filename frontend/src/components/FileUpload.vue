<template>
  <div class="container p-4 min-h-screen">
    <!-- Red Notification Banner -->
    <div v-if="showNotification" class="fixed top-0 left-0 w-full bg-red-600 text-white p-4 flex justify-between items-center z-50 shadow-lg transition-all duration-300" :class="{ 'opacity-0 translate-y-[-100%]': !notificationVisible }">
      <span>{{ notificationMessage }}</span>
      <button @click="closeNotification" class="text-white hover:text-red-200 ml-4">×</button>
    </div>

    <div class="card">
      <h2 class="text-xl mb-4">Загрузить документ(ы)</h2>
      <p>*Общий размер файлов не должно превышать 10 мб</p>

      <div class="file-input-wrapper">
        <input type="file" multiple @change="handleFile" ref="fileInput" class="mb-2 file-input" />
        <p class="text-sm text-gray-600 mb-2">Выберите один или несколько файлов. Все файлы будут сохранены до нажатия на "Загрузить".</p>
      </div>

      <p v-if="allFiles.length" class="text-sm text-gray-600 mb-2">
        Выбрано файлов: {{ allFiles.length }}
      </p>

      <ul v-if="allFiles.length" class="mb-4 list-disc list-inside text-sm text-gray-800">
        <li v-for="(f, i) in allFiles" :key="i">{{ f.name }}</li>
      </ul>

      <div class="button-group flex space-x-4 mb-4">
        <button @click="upload" class="bg-blue-500 text-white px-4 py-2 flex-1">Загрузить</button>
        <button @click="clear" class="bg-gray-400 text-white px-4 py-2 flex-1">Очистить</button>
      </div>

      <div v-if="topWords.length" class="mt-6">
        <h3 class="text-lg font-semibold mb-2">Топ 50 слов</h3>
        <table class="w-full border border-collapse text-sm">
          <thead class="bg-gray-100">
            <tr>
              <th class="border p-2 text-left">Слово</th>
              <th class="border p-2 text-left">TF</th>
              <th class="border p-2 text-left">IDF</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(word, index) in topWords" :key="index">
              <td class="border p-2">{{ word.word }}</td>
              <td class="border p-2">
                {{ word.tf ? word.tf.toFixed(6) : (word.avg_tf ? word.avg_tf.toFixed(6) : '-') }}
              </td>
              <td class="border p-2">{{ word.idf.toFixed(6) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from '../api';

const allFiles = ref([]);
const topWords = ref([]);
const uploadedFiles = ref([]);
const fileInput = ref(null);
const showNotification = ref(false);
const notificationVisible = ref(true);
const notificationMessage = ref('');

function handleFile(e) {
  const newFiles = Array.from(e.target.files);
  allFiles.value = [...allFiles.value, ...newFiles];
  console.log('Selected files:', allFiles.value.map(f => f.name));
}

async function upload() {
  showNotification.value = false; // Reset notification
  try {
    const formData = new FormData();
    allFiles.value.forEach((file, index) => {
      formData.append('files', file);
      console.log(`Appending file ${index + 1}: ${file.name}`);
    });

    const response = await axios.post('upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      withCredentials: true,
    });

    console.log('Backend response:', response.data);
    topWords.value = response.data.top_words || [];
    uploadedFiles.value = response.data.files || [];
    allFiles.value = [];
    fileInput.value.value = '';
  } catch (error) {
    console.error('Upload error:', error.response?.data || error.message);
    notificationMessage.value = error.response?.data?.error || 'Неправильный формат файла';
    showNotification.value = true;
    notificationVisible.value = true;
    setTimeout(() => {
      notificationVisible.value = false;
      setTimeout(() => (showNotification.value = false), 300); // Allow fade-out animation
    }, 3000); // Show for 5 seconds
  }
}

function clear() {
  allFiles.value = [];
  uploadedFiles.value = [];
  topWords.value = [];
  fileInput.value.value = '';
  console.log('Cleared all data');
}

const closeNotification = () => {
  notificationVisible.value = false;
  setTimeout(() => (showNotification.value = false), 300); // Allow fade-out animation
};
</script>

<style scoped>
.container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(to right, #e5e7eb, #f3f4f6);
  padding: 1rem;
}

.card {
  background-color: #ffffff;
  padding: 2rem;
  border-radius: 0.75rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  width: 100%;
  max-width: 700px;
}

.text-xl {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1f2937;
  text-align: center;
  margin-bottom: 1.5rem;
}

.text-lg {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.text-sm.text-gray-600 {
  color: #4b5563;
  font-size: 0.875rem;
  line-height: 1.25rem;
}

.file-input-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.file-input {
  width: 100%;
  max-width: 400px;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background-color: #f9fafb;
  cursor: pointer;
  color: #1f2937;
  font-size: 1rem;
  transition: border-color 0.2s ease-in-out;
}

.file-input:hover {
  border-color: #9ca3af;
}

.file-input::file-selector-button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  background-color: #e5e7eb;
  color: #1f2937;
  cursor: pointer;
  transition: background-color 0.2s ease-in-out;
}

.file-input::file-selector-button:hover {
  background-color: #d1d5db;
}

.list-disc {
  padding-left: 1.5rem;
  color: #1f2937;
  font-size: 0.875rem;
}

.list-disc li {
  margin-bottom: 0.25rem;
}

.button-group {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

button {
  padding: 0.75rem 1rem;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 0.375rem;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease-in-out;
}

.bg-blue-500 {
  background-color: #3b82f6;
  color: #ffffff;
  flex: 1;
}

.bg-blue-500:hover {
  background-color: #2563eb;
}

.bg-gray-400 {
  background-color: #9ca3af;
  color: #ffffff;
  flex: 1;
}

.bg-gray-400:hover {
  background-color: #6b7280;
}

button:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
  border-radius: 0.375rem;
  overflow: hidden;
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
  font-weight: 600;
}

tbody tr:nth-child(even) {
  background-color: #f9fafb;
}

tbody tr:hover {
  background-color: #f1f5f9;
}

.mt-6 {
  margin-top: 1.5rem;
}

.mb-4 {
  margin-bottom: 1rem;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

@media (max-width: 640px) {
  .card {
    padding: 1.5rem;
    margin: 1rem;
  }

  .file-input {
    max-width: 100%;
  }

  .button-group {
    flex-direction: column;
    gap: 0.5rem;
  }

  button {
    width: 100%;
  }

  table {
    font-size: 0.75rem;
  }

  th, td {
    padding: 0.5rem;
  }
}

/* Notification Styles */
.fixed {
  position: fixed;
}

.top-0 {
  top: 0;
}

.left-0 {
  left: 0;
}

.w-full {
  width: 100%;
}

.bg-red-600 {
  background-color: #dc2626;
}

.text-white {
  color: #ffffff;
}

.p-4 {
  padding: 1rem;
}

.flex {
  display: flex;
}

.justify-between {
  justify-content: space-between;
}

.items-center {
  align-items: center;
}

.z-50 {
  z-index: 50;
}

.shadow-lg {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.transition-all {
  transition-property: all;
}

.duration-300 {
  transition-duration: 300ms;
}

.opacity-0 {
  opacity: 0;
}

.translate-y-\[-100\%\] {
  transform: translateY(-100%);
}

.ml-4 {
  margin-left: 1rem;
}

.hover\:text-red-200:hover {
  color: #f87171;
}
</style>