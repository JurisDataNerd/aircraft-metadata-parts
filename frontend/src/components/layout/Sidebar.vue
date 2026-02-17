<script setup lang="ts">
import { useRoute } from 'vue-router';
import { Search, History, ShieldAlert, LogOut, UploadCloud, Plane } from 'lucide-vue-next';

const route = useRoute();

const navigation = [
  { name: 'Pencarian Konfigurasi', href: '/app', icon: Search },
  { name: 'Riwayat & Log', href: '/app/history', icon: History },
  { name: 'Upload Dokumen', href: '/app/admin/upload', icon: UploadCloud },
  { name: 'Dashboard Admin', href: '/app/admin', icon: ShieldAlert },
];

const isActive = (path: string) => route.path === path;
</script>

<template>
  <aside class="w-64 h-screen fixed left-0 top-0 bg-white border-r border-slate-200 flex flex-col z-50">
    <!-- Logo Area -->
    <div class="h-16 flex items-center px-6 border-b border-slate-100">
      <div class="flex items-center gap-2">
        <div class="w-8 h-8 rounded-xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-600/20">
            <Plane class="text-white w-5 h-5 transform -rotate-45" />
        </div>
        <span class="font-bold text-slate-800 tracking-tight">AirConfig</span>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 px-4 py-6 space-y-1">
      <router-link 
        v-for="item in navigation" 
        :key="item.name" 
        :to="item.href"
        class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group"
        :class="isActive(item.href) 
            ? 'bg-blue-50 text-blue-700' 
            : 'text-slate-500 hover:text-slate-900 hover:bg-slate-50'"
      >
        <component :is="item.icon" class="w-5 h-5" :class="isActive(item.href) ? 'text-blue-600' : 'text-slate-400 group-hover:text-slate-600'" />
        {{ item.name }}
      </router-link>
    </nav>

    <!-- User Profile / Footer -->
    <div class="p-4 border-t border-slate-100 bg-slate-50/50">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-full bg-white flex items-center justify-center border border-slate-200 shadow-sm">
          <span class="text-sm font-bold text-slate-600">JD</span>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-bold text-slate-800 truncate">John Doe</p>
          <p class="text-xs text-slate-500 truncate">Engineer</p>
        </div>
        <button class="text-slate-400 hover:text-red-500 transition-colors">
          <LogOut class="w-5 h-5" />
        </button>
      </div>
    </div>
  </aside>
</template>
