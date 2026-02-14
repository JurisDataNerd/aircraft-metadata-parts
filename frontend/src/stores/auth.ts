import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useAuthStore = defineStore('auth', () => {
    const isAuthenticated = ref(false);
    const user = ref<{ name: string; role: string } | null>(null);

    const login = async () => {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 800));

        isAuthenticated.value = true;
        user.value = {
            name: 'Prince of Darkness',
            role: 'Senior Engineer'
        };

        return true;
    };

    const logout = () => {
        isAuthenticated.value = false;
        user.value = null;
        // router.push('/login') handled by component or guard
    };

    return {
        isAuthenticated,
        user,
        login,
        logout
    };
});
