<script setup lang="ts">
import AppSidebar from '@/components/layout/AppSidebar.vue';
import AppHeader from '@/components/layout/AppHeader.vue';
</script>

<template>
  <div class="flex h-screen bg-slate-950 overflow-hidden font-sans text-slate-200">
    <AppSidebar />
    
    <div class="flex-1 flex flex-col min-w-0">
      <AppHeader />
      
      <main class="flex-1 overflow-y-auto p-6 scroll-smooth">
        <div class="max-w-7xl mx-auto space-y-6">
            <router-view />
        </div>
      </main>
    </div>
  </div>
</template>

<style>
/* Custom Scrollbar for Webkit */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-track {
  background: transparent; 
}
::-webkit-scrollbar-thumb {
  background: #334155; 
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #475569; 
}
</style>
