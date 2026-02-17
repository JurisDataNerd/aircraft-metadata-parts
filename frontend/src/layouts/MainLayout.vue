<script setup lang="ts">
import Sidebar from '@/components/layout/Sidebar.vue';
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-900 flex">
    <!-- Sidebar -->
    <Sidebar class="hidden md:flex" />

    <!-- Mobile Header Placeholder (Simulated for now) -->
    <div class="md:hidden fixed top-0 w-full h-16 bg-slate-900 z-50 px-4 flex items-center justify-between border-b border-slate-800">
        <span class="font-bold text-white">AirConfig</span>
        <!-- Mobile Menu Button would go here -->
    </div>

    <!-- Main Content -->
    <main class="flex-1 md:ml-64 p-4 md:p-8 pt-20 md:pt-8 min-h-screen transition-all duration-300 ease-in-out">
      <div class="max-w-7xl mx-auto">
         <router-view v-slot="{ Component }">
            <transition name="page" mode="out-in">
              <component :is="Component" />
            </transition>
         </router-view>
      </div>
    </main>
  </div>
</template>
