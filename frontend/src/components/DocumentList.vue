<template>
  <div class="p-4">
    <h2 class="text-xl mb-4">Список документов</h2>

    <table v-if="documents.length" class="documents-table">
      <thead>
        <tr>
          <th>Название</th>
          <th>Действия</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="doc in documents" :key="doc.id">
          <td>{{ doc.name }}</td>
          <td class="actions-cell">
            <router-link :to="`/documents/${doc.id}`" class="btn view-btn" title="Просмотреть">👁️</router-link>
            <router-link :to="`/documents/${doc.id}/statistics`" class="btn stats-btn" title="Статистика">📊</router-link>
            <button @click="openAddToCollection(doc.id)" class="btn add-btn" title="В коллекцию">➕</button>
            <button @click="deleteDocument(doc.id)" class="btn delete-btn" title="Удалить">🗑️</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Pagination -->
    <div v-if="documents.length" class="pagination mt-4 flex items-center">
      <button @click="fetchDocuments(currentPage - 1)"
              :disabled="!prevPage"
              class="btn pagination-btn">
        Предыдущая
      </button>
      <span class="mx-4">Страница {{ currentPage }}</span>
      <button @click="fetchDocuments(currentPage + 1)"
              :disabled="!nextPage"
              class="btn pagination-btn">
        Следующая
      </button>
    </div>

    <p v-else class="no-docs-text">Нет загруженных документов.</p>

    <!-- Modal for selecting collection -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-content">
        <h3 class="modal-title">Выберите коллекцию</h3>
        <select v-model="selectedCollectionId" class="select-modal">
          <option :value="null" disabled>Выберите коллекцию</option>
          <option v-for="collection in collections" :key="collection.id" :value="collection.id">
            {{ collection.name }}
          </option>
        </select>
        <div class="modal-buttons">
          <button @click="closeModal" class="btn modal-cancel">Отмена</button>
          <button @click="addToCollection" class="btn modal-add" :disabled="!selectedCollectionId">Добавить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from '../api';
import { computed } from 'vue';
import { useAuthStore } from '../stores/auth';

const authStore = useAuthStore();
const isAuthenticated = computed(() => authStore.isAuthenticated);
const router = useRouter();

// State
const documents = ref([]);
const collections = ref([]);
const showModal = ref(false);
const selectedDocumentId = ref(null);
const selectedCollectionId = ref(null);
const currentPage = ref(1);
const nextPage = ref(null);
const prevPage = ref(null);

// Fetch documents with pagination
async function fetchDocuments(page = 1) {
  try {
    const response = await axios.get(
      `http://37.9.53.228/api/documents/?page=${page}`,
      { withCredentials: true }
    );
    documents.value = response.data.results;
    nextPage.value = response.data.next;
    prevPage.value = response.data.previous;
    currentPage.value = page;
  } catch (error) {
    console.error('Error fetching documents:', error);
    documents.value = [];
  }
}

// Fetch collections (for modal)
async function fetchCollections() {
  try {
    const response = await axios.get(
      `http://37.9.53.228/api/collections/?page=1`
    );
    collections.value = response.data.results;
  } catch (error) {
    console.error('Error fetching collections:', error);
    collections.value = [];
  }
}

// Action handlers
async function deleteDocument(docId) {
  try {
    await axios.delete(
      `http://37.9.53.228/api/documents/${docId}/delete/`
    );
    fetchDocuments(currentPage.value);
    showNotification('Документ удален успешно!', 'green');
  } catch (error) {
    console.error('Ошибка удаления документа:', error);
    showNotification('Не удалось удалить документ!', 'red');
  }
}

function openAddToCollection(docId) {
  if (!isAuthenticated.value) {
    router.push('/login');
    return;
  }
  selectedDocumentId.value = docId;
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
  selectedCollectionId.value = null;
}

async function addToCollection() {
  if (!selectedCollectionId.value || !selectedDocumentId.value) return;
  try {
    await axios.post(
      `http://37.9.53.228/api/collection/${selectedCollectionId.value}/${selectedDocumentId.value}/`
    );
    showNotification('Документ добавлен в коллекцию!', 'green');
    closeModal();
  } catch (error) {
    console.error('Ошибка добавления документа:', error);
    showNotification('Не удалось добавить документ в коллекцию!', 'red');
  }
}

// Notification helper
function showNotification(message, color) {
  const notification = document.createElement('div');
  notification.innerText = message;
  Object.assign(notification.style, {
    position: 'fixed', top: '50px', right: '10px',
    background: color, color: 'white', padding: '12px',
    borderRadius: '6px', zIndex: '100'
  });
  document.body.appendChild(notification);
  setTimeout(() => notification.remove(), 3000);
}

// On mount
onMounted(() => {
  if (isAuthenticated.value) {
    fetchDocuments(1);
    fetchCollections();
  } else {
    router.push('/login');
  }
});
</script>

<style scoped>
/* Container styling */
.p-4 {
  min-height: calc(100vh - 4rem);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(to right, #e5e7eb, #f3f4f6);
}

/* Table structure */
.documents-table {
  width: 100%;
  max-width: 600px;
  border-collapse: collapse;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  background-color: #fff;
  border-radius: 0.5rem;
  overflow: hidden;
  margin-bottom: 1rem;
}

.documents-table thead tr {
  background-color: #f9fafb;
}

.documents-table th,
.documents-table td {
  border: 1px solid #e5e7eb;
  padding: 0.75rem;
  text-align: left;
  font-size: 0.875rem;
  color: #1f2937;
}

.actions-cell {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

/* No documents text */
.no-docs-text {
  font-size: 0.875rem;
  color: #4b5563;
}

/* Button base style */
.btn {
  padding: 0.5rem;
  border: none;
  border-radius: 0.375rem;
  font-weight: 600;
  transition: background-color 0.2s, opacity 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  text-decoration: none;
}

/* Button hover effect */
.btn:hover {
  opacity: 0.8;
}

/* Specific button styles */
.view-btn {
  background-color: #007bff;
  color: #fff;
}


.pagination-btn {
  padding: 6px 12px;
  margin: 0 4px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.pagination-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}





.stats-btn {
  background-color: #ff9800;
  color: #fff;
}

.add-btn {
  background-color: #10b981;
  color: #fff;
}

.delete-btn {
  background-color: #e63946;
  color: #fff;
}

/* Modal overlay and content */
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.modal-content {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 28rem;
}

.modal-title {
  font-size: 1.125rem;
  margin-bottom: 1rem;
  color: #1f2937;
}

.select-modal {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.modal-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.modal-cancel {
  background-color: #6b7280;
  color: #fff;
}

.modal-add {
  background-color: #3b82f6;
  color: #fff;
}

.modal-add:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .documents-table,
  .modal-content {
    margin: 0 1rem;
  }
  .actions-cell {
    flex-direction: column;
    gap: 0.25rem;
  }
}
</style>