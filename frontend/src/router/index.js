
import { createRouter, createWebHistory } from 'vue-router';
import RegisterPage from '../components/RegisterPage.vue';
import VerifyEmailPage from '../components/VerifyEmailPage.vue';
import LoginForm from '../components/LoginForm.vue';
import FileUpload from '../components/FileUpload.vue';
import DocumentList from '../components/DocumentList.vue';
import DocumentDetail from '../components/DocumentDetail.vue';
import DocumentStatistics from '../components/DocumentStatistics.vue';
import CollectionList from '../components/CollectionList.vue';
import ProfilePage from '../components/ProfilePage.vue';
import CollectionDetail from '../components/CollectionDetail.vue';

const routes = [
  { path: '/register', component: RegisterPage },
  { path: '/verify-email', name: 'VerifyEmail', component: VerifyEmailPage },
  { path: '/login', component: LoginForm },
  { path: '/', component: FileUpload, meta: { requiresAuth: true } },
  { path: '/documents', component: DocumentList, meta: { requiresAuth: true } },
  { path: '/documents/:id', component: DocumentDetail, props: true, meta: { requiresAuth: true } },
  { path: '/documents/:id/statistics', component: DocumentStatistics, props: true, meta: { requiresAuth: true } },
  { path: '/collections', component: CollectionList, meta: { requiresAuth: true } },
  { path: '/collections/:id', component: CollectionDetail, meta: { requiresAuth: true } },
  { path: '/profile', name: 'Profile', component: ProfilePage, meta: { requiresAuth: true } }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Use localStorage as a backup check so you don’t need the store instantly
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('access_token');
    if (!token) {
      next('/login');
      return;
    }
  }
  next();
});

export default router;
