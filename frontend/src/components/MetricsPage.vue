<template>
  <div class="p-4">
    <h2 class="text-xl font-bold mb-4">Метрики</h2>

    <div v-if="metrics && isValidMetrics">
      <table class="vertical-table">
        <tbody>
          <tr v-for="(metric, index) in processedMetrics" :key="index">
            <th class="px-4 py-2 text-left">{{ metric.label }}</th>
            <td class="px-4 py-2">{{ metric.value }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-if="loading" class="info">Загрузка метрик...</p>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { useAuthStore } from '../stores/auth';

const metrics = ref(null);
const loading = ref(false);
const error = ref('');

const authStore = useAuthStore();

// Define two possible sets of labels for admin and user metrics
const adminMetricLabels = {
  files_processed: "Обработано файлов",
  min_time_processed: "Минимальное время обработки (сек)",
  avg_time_processed: "Среднее время обработки (сек)",
  max_time_processed: "Максимальное время обработки (сек)",
  latest_file_processed_timestamp: "Последняя дата обработки"
};

const userMetricLabels = {
  files_processed: "Обработано файлов",
  min_file_size: "Минимальный размер файла (байт)",
  avg_file_size: "Средний размер файла (байт)",
  max_file_size: "Максимальный размер файла (байт)",
  min_word_count: "Минимальное количество слов",
  avg_word_count: "Среднее количество слов",
  max_word_count: "Максимальное количество слов"
};

// Helper flag: check if received `metrics.value` is a valid object
const isValidMetrics = computed(() => {
  return metrics.value && typeof metrics.value === "object";
});

// Compute processed metrics using user-friendly labels.
// If the metrics are admin metrics, the object will contain "min_time_processed".
const processedMetrics = computed(() => {
  // Guard clause if data is not valid
  if (!isValidMetrics.value) return [];

  const isAdmin = 'min_time_processed' in metrics.value;
  const labels = isAdmin ? adminMetricLabels : userMetricLabels;

  return Object.entries(labels).map(([key, label]) => {
    let value = metrics.value[key];

    // For admin metrics, format timestamp to a readable string
    if (key === 'latest_file_processed_timestamp' && value) {
      value = new Date(value * 1000).toLocaleString();
    }

    // If the metric is missing, display an em dash
    if (value === undefined || value === null) {
      value = '—';
    }

    return { label, value };
  });
});

onMounted(async () => {
  loading.value = true;
  try {
    // Use the full API URL if needed:
    const response = await axios.get('api/metrics/', {
      headers: { Authorization: `Bearer ${authStore.token}` }
    });
    console.log(response)
    // Check if the response is in fact HTML rather than JSON.
    if (
      typeof response.data === 'string' &&
      response.data.trim().toLowerCase().startsWith('<!doctype html>')
    ) {
      throw new Error('Получен HTML вместо ожидаемого JSON. Проверьте URL или настройки сервера.');
    }

    metrics.value = response.data;
  } catch (err) {
    error.value = err.response?.data?.error || err.message || 'Ошибка загрузки метрик.';
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.vertical-table {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
  font-size: 0.95em;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.vertical-table th,
.vertical-table td {
  border: 1px solid #ddd;
  padding: 12px 15px;
}

.vertical-table th {
  background-color: #009879;
  color: #fff;
  text-align: left;
}

.info {
  font-style: italic;
  color: #333;
  margin-top: 10px;
}

.error {
  color: red;
  font-weight: bold;
  margin-top: 10px;
}
</style>
