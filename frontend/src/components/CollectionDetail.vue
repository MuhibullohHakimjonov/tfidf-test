<template>
  <div class="p-4">
    <h1 class="text-2xl font-bold mb-4">Collection Detail: {{ collection.name }}</h1>
    <p class="mb-4">Number of Documents: {{ collection.documents.length }}</p>

    <h2 class="text-xl font-semibold mb-2">Documents:</h2>
    <ul class="list-disc pl-5">
      <li v-for="doc in collection.documents" :key="doc.id" class="mb-2">
        {{ doc.name }} ({{ doc.word_count }} words)
        <button
          @click="deleteDocument(doc.id)"
          class="ml-4 px-2 py-1 bg-red-500 text-white rounded"
        >
          Delete
        </button>
      </li>
    </ul>

    <h2 class="text-xl font-semibold mt-6 mb-2">Statistics:</h2>
    <div v-if="statistics">
      <p>Documents Count: {{ statistics.documents_count }}</p>
      <h3 class="font-semibold mt-2">Top Words:</h3>
      <ul class="list-disc pl-5">
        <li v-for="word in statistics.top_words" :key="word.word">
          {{ word.word }} (TF: {{ word.total_tf }}, IDF: {{ word.idf }})
        </li>
      </ul>
    </div>
    <div v-else>Loading statistics...</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const collection = ref({ documents: [] });
const statistics = ref(null);

const fetchCollection = async () => {
  try {
    const response = await fetch(`/api/collections/${route.params.id}/`);
    collection.value = await response.json();
  } catch (error) {
    console.error('Failed to load collection:', error);
  }
};

const fetchStatistics = async () => {
  try {
    const response = await fetch(`/api/collections/${route.params.id}/statistics/`);
    statistics.value = await response.json();
  } catch (error) {
    console.error('Failed to load statistics:', error);
  }
};

const deleteDocument = async (documentId) => {
  try {
    const response = await fetch(`/api/documents/${documentId}/`, {
      method: 'DELETE',
    });

    if (response.ok) {
      collection.value.documents = collection.value.documents.filter(doc => doc.id !== documentId);
      // Refresh statistics after deletion
      fetchStatistics();
    } else {
      console.error('Failed to delete document');
    }
  } catch (error) {
    console.error('Error deleting document:', error);
  }
};

onMounted(() => {
  fetchCollection();
  fetchStatistics();
});
</script>

<style scoped>
/* optional custom styling */
</style>





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