import { createRouter, createWebHistory } from 'vue-router';
import ConfigurationSearch from '../views/ConfigurationSearch.vue';
import LandingPage from '../views/LandingPage.vue';
import LoginView from '../views/LoginView.vue';
import MainLayout from '../layouts/MainLayout.vue';
import { useAuthStore } from '@/stores/auth';

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'landing',
            component: LandingPage,
        },
        {
            path: '/login',
            name: 'login',
            component: LoginView,
        },
        {
            path: '/app',
            component: MainLayout,
            meta: { requiresAuth: true },
            children: [
                {
                    path: 'admin/upload',
                    name: 'admin-upload',
                    component: () => import('../views/AdminUpload.vue'),
                },
                {
                    path: 'history',
                    name: 'history',
                    component: () => import('../views/HistoryLog.vue'),
                },
                {
                    path: 'admin',
                    name: 'admin',
                    component: () => import('../views/AdminDashboard.vue'),
                },
                {
                    path: '', // /app
                    name: 'search',
                    component: ConfigurationSearch,
                },
            ]
        },
    ],
});

router.beforeEach((to, _from, next) => {
    const authStore = useAuthStore();

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        next('/login');
    } else {
        next();
    }
});

export default router;
