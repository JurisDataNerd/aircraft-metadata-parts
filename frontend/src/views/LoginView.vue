<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { Plane, Lock, ArrowRight, Loader2 } from 'lucide-vue-next';

const router = useRouter();
const authStore = useAuthStore();

const isLoading = ref(false);
const username = ref('admin');
const password = ref('password');

const handleLogin = async () => {
  isLoading.value = true;
  await authStore.login();
  isLoading.value = false;
  router.push('/app');
};
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex items-center justify-center p-6 relative overflow-hidden font-sans">
    <!-- Abstract Background -->
    <div class="absolute inset-0 pointer-events-none">
       <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-100 rounded-full blur-[120px] animate-pulse opacity-60"></div>
       <div class="absolute bottom-1/4 right-1/4 w-96 h-96 bg-indigo-100 rounded-full blur-[120px] opacity-60"></div>
    </div>

    <div class="relative z-10 w-full max-w-md">
      <!-- Logo Area -->
      <div class="text-center mb-8">
         <div class="w-16 h-16 rounded-2xl bg-blue-600 flex items-center justify-center shadow-xl shadow-blue-600/20 mx-auto mb-4 transform -rotate-6">
           <Plane class="text-white w-8 h-8 transform -rotate-45" />
         </div>
         <h1 class="text-2xl font-bold text-slate-800 tracking-tight">Access Control</h1>
         <p class="text-slate-500">Aircraft Configuration Intelligence</p>
      </div>

      <!-- Login Card -->
      <div class="bg-white border border-slate-100 rounded-2xl p-8 shadow-2xl shadow-slate-200">
         <form @submit.prevent="handleLogin" class="space-y-6">
            <div class="space-y-2">
               <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Username</label>
               <input 
                 v-model="username" 
                 type="text" 
                 class="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 text-slate-800 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all font-medium"
                 placeholder="Enter username"
               />
            </div>
            
            <div class="space-y-2">
               <label class="text-xs font-bold text-slate-500 uppercase tracking-wider">Password</label>
               <input 
                 v-model="password" 
                 type="password" 
                 class="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 text-slate-800 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all font-medium"
                 placeholder="••••••••"
               />
            </div>

            <button 
              type="submit" 
              :disabled="isLoading"
              class="w-full bg-slate-900 hover:bg-slate-800 text-white font-bold py-3.5 rounded-lg transition-all flex items-center justify-center gap-2 group shadow-lg shadow-slate-900/10 disabled:opacity-70 disabled:cursor-not-allowed"
            >
               <Loader2 v-if="isLoading" class="w-5 h-5 animate-spin" />
               <span v-else>Authenticate</span>
               <ArrowRight v-if="!isLoading" class="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
         </form>

         <!-- Footer -->
         <div class="mt-6 text-center">
            <p class="text-xs text-slate-400 flex items-center justify-center gap-1 font-medium">
               <Lock class="w-3 h-3" />
               Restricted Area. Authorized Personnel Only.
            </p>
         </div>
      </div>
    </div>
  </div>
</template>
