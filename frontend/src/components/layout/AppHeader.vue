<script setup lang="ts">
import { Bell } from 'lucide-vue-next';
</script>

<template>
  <header class="h-16 bg-slate-900/50 backdrop-blur-md border-b border-slate-700/50 flex items-center justify-between px-6 sticky top-0 z-10 transition-colors">
    <div class="flex items-center gap-4 flex-1">
        <!-- Breadcrumbs or Page Title could go here -->
    </div>

    <div class="flex items-center gap-4">
      <button class="w-10 h-10 rounded-full flex items-center justify-center text-slate-400 hover:bg-slate-800 hover:text-white transition-colors relative">
        <Bell class="w-5 h-5" />
        <span class="absolute top-2.5 right-2.5 w-2 h-2 bg-red-500 rounded-full border border-slate-900"></span>
      </button>
    </div>
  </header>
</template>
