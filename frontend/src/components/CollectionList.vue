<template>
  <div class="p-4">
    <h2 class="text-xl mb-4">Коллекции</h2>
    <div class="input-group mb-4">
      <input
        v-model="newCollectionName"
        placeholder="Введите название коллекции"
        class="input-field flex-1"
      />
      <button @click="createCollection" class="btn create-btn">
        Создать
      </button>
    </div>
    <table v-if="collections.length" class="collections-table">
      <thead>
        <tr>
          <th>Название коллекции</th>
          <th>Действия</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="collection in collections" :key="collection.id">
          <td>
            <router-link
              :to="`/collections/${collection.id}`"
              class="collection-link"
            >
              {{ collection.name }}
            </router-link>
          </td>
          <td class="actions-cell">
            <button
              @click="deleteCollection(collection.id)"
              class="btn delete-btn"
              title="Удалить"
            >
              🗑️
            </button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else class="no-data">
      Нет коллекций.
    </p>
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
const newCollectionName = ref('');
const collections = ref([]);

const fetchCollections = async () => {
  try {
    const response = await axios.get('api/collections/');
    collections.value = response.data;
    console.log('Fetched collections:', collections.value);
  } catch (error) {
    console.error('Failed to fetch collections:', error);
    collections.value = [];
  }
};
const deleteCollection = async (collectionId) => {
  try {
    await axios.delete(`api/collection/${collectionId}/delete/`);
    collections.value = collections.value.filter(collection => collection.id !== collectionId);
    showNotification("Коллекция удалена успешно!", "green");
  } catch (error) {
    console.error("Ошибка удаления коллекции:", error);
    showNotification("Не удалось удалить коллекцию!", "red");
  }
};
const showNotification = (message, color) => {
  const notification = document.createElement("div");
  notification.innerText = message;
  notification.style.position = "fixed";
  notification.style.top = "60px";
  notification.style.right = "10px";
  notification.style.background = color;
  notification.style.color = "white";
  notification.style.padding = "20px";
  notification.style.borderRadius = "6px";
  notification.style.zIndex = "100";
  
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.remove();
  }, 3000);
};



const createCollection = async () => {
  if (!newCollectionName.value) {
    alert('Пожалуйста, введите название коллекции.');
    return;
  }
  try {
    await axios.post('api/collections/create/', { name: newCollectionName.value });
    newCollectionName.value = '';
    await fetchCollections();
  } catch (error) {
    console.error('Failed to create collection:', error);
    alert('Не удалось создать коллекцию.');
  }
};

onMounted(() => {
  if (isAuthenticated.value) {
    fetchCollections();
  } else {
    console.warn('User not authenticated, redirecting to login.');
    router.push('/login');
  }
});
</script>

<style scoped>
.p-4 {
  min-height: calc(100vh - 4rem);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(to right, #e5e7eb, #f3f4f6);
}

/* Title */
.text-xl {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  text-align: center;
  margin-bottom: 1.5rem;
}

/* Input group styling */
.input-group {
  width: 100%;
  max-width: 600px;
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.input-field {
  border: 1px solid #d1d5db;
  padding: 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  flex: 1;
  transition: border-color 0.2s ease-in-out;
}

.input-field:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Button styling */
.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  transition: background-color 0.2s ease-in-out, opacity 0.2s;
  cursor: pointer;
}

.create-btn {
  background-color: #3b82f6;
  color: #fff;
}

.create-btn:hover {
  background-color: #2563eb;
}

.delete-btn {
  background-color: #e63946;
  color: #fff;
  padding: 8px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: bold;
}

.delete-btn:hover {
  opacity: 0.7;
}

/* Table styling */
.collections-table {
  width: 100%;
  max-width: 600px;
  border-collapse: collapse;
  background-color: #fff;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border-radius: 0.5rem;
  overflow: hidden;
  margin-bottom: 1rem;
}

.collections-table th,
.collections-table td {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  font-size: 0.875rem;
  color: #1f2937;
}

.collections-table th {
  background-color: #f3f4f6;
  font-weight: 500;
  text-align: left;
}

.collections-table tbody tr:nth-child(even) {
  background-color: #f9fafb;
}

.collections-table tbody tr:hover {
  background-color: #f1f5f9;
}

/* Link styling */
.collection-link {
  color: #3b82f6;
  text-decoration: none;
}

.collection-link:hover {
  text-decoration: underline;
}

/* Actions cell styling */
.actions-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  justify-content: center;
}

/* No data text */
.no-data {
  font-size: 0.875rem;
  color: #4b5563;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .p-4 {
    padding: 1rem;
  }
  
  .input-group {
    flex-direction: column;
  }
  
  .collections-table {
    font-size: 0.75rem;
  }
  
  .collections-table th,
  .collections-table td {
    padding: 0.5rem;
  }
}
</style>