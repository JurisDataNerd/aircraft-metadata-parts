<script setup lang="ts">
import { 
  Search, 
  History, 
  AlertTriangle, 
  Settings, 
  FileText 
} from 'lucide-vue-next';
import { useRoute } from 'vue-router';

const route = useRoute();

const menuItems = [
  { name: 'Configuration Search', icon: Search, path: '/' },
  { name: 'Decision History', icon: History, path: '/history' },
  { name: 'Risk Intelligence', icon: AlertTriangle, path: '/risk' },
  { name: 'Documentation', icon: FileText, path: '/docs' },
  { name: 'Admin Settings', icon: Settings, path: '/admin' },
];

const isActive = (path: string) => route.path === path;
</script>

<template>
  <aside class="w-64 bg-slate-900 border-r border-slate-700 flex flex-col h-screen transition-all duration-300">
    <div class="p-6 flex items-center gap-3">
      <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
        <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
        </svg>
      </div>
      <span class="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
        Aircraft<span class="font-light">Config</span>
      </span>
    </div>

    <nav class="flex-1 px-3 py-4 space-y-1">
      <router-link
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        class="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group relative overflow-hidden"
        :class="isActive(item.path) ? 'bg-blue-600/10 text-blue-400' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'"
      >
        <component 
          :is="item.icon" 
          class="w-5 h-5 transition-transform group-hover:scale-110" 
          :class="isActive(item.path) ? 'text-blue-400' : 'text-slate-500 group-hover:text-slate-300'"
        />
        <span class="font-medium text-sm">{{ item.name }}</span>
        
        <!-- Active Indicator -->
        <div 
          v-if="isActive(item.path)"
          class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-blue-500 rounded-r-full shadow-[0_0_10px_rgba(59,130,246,0.5)]"
        ></div>
      </router-link>
    </nav>

    <div class="p-4 border-t border-slate-800">
      <div class="flex items-center gap-3 px-3 py-2 rounded-lg bg-slate-800/50 hover:bg-slate-800 transition-colors cursor-pointer">
        <div class="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center border border-slate-600">
          <span class="text-xs font-bold text-slate-300">ENG</span>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-slate-200 truncate">Prince of Darkness</p>
          <p class="text-xs text-slate-500 truncate">Senior Engineer</p>
        </div>
      </div>
    </div>
  </aside>
</template>
