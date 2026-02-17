<script setup lang="ts">
import { ref } from 'vue';
import { usePartsStore } from '@/stores/parts';
import { Search, Filter } from 'lucide-vue-next';
import PartCard from '@/components/parts/PartCard.vue';
import PartDetailModal from '@/components/parts/PartDetailModal.vue';
import type { IPDPart } from '@/types';

const partsStore = usePartsStore();
const searchQuery = ref('');
const searchType = ref<'line' | 'part'>('line');
const selectedPart = ref(null as IPDPart | null);

const handleSearch = async () => {
  if (!searchQuery.value) return;
  await partsStore.searchParts(searchQuery.value);
};

const openDetailModal = async (part: IPDPart) => {
  selectedPart.value = part;
  await partsStore.selectPart(part);
};

const closeDetailModal = () => {
    partsStore.clearSelection();
    selectedPart.value = null;
};

const handleConfirmSelection = (part: IPDPart) => {
    console.log('Confirmed:', part);
    closeDetailModal();
    // In real app, save selection to backend
    alert(`Pilihan dikonfirmasi: ${part.part_number}`);
};

const handleBrowseStickers = async () => {
    searchQuery.value = 'Browsing Stickers...';
    await partsStore.searchParts('stickers');
};
</script>

<template>
  <div class="space-y-8 animate-fade-in">
    <!-- Header Section -->
    <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-100 p-8 md:p-12 shadow-sm">
      <div class="absolute top-0 right-0 w-96 h-96 bg-blue-200/20 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>
      
      <div class="relative z-10 max-w-2xl">
        <h1 class="text-4xl md:text-5xl font-bold text-slate-900 mb-4 tracking-tight">
            Intelijen <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">Konfigurasi</span>
        </h1>
        <p class="text-lg text-slate-600 leading-relaxed mb-8">
            Akses data IPD dan Engineering Drawing terpadu dengan penilaian risiko real-time dan deteksi pergeseran konfigurasi.
        </p>

        <!-- Search Bar -->
        <div class="flex flex-col md:flex-row gap-2 bg-white p-2 rounded-xl border border-slate-200 shadow-lg shadow-slate-200/50">
             <div class="flex-1 relative group">
                <Search class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
                <input 
                  v-model="searchQuery"
                  type="text" 
                  class="w-full bg-transparent border-none text-slate-800 pl-12 pr-4 py-4 focus:ring-0 placeholder-slate-400 font-medium"
                  :placeholder="searchType === 'line' ? 'Masukkan Nomor Line (cth. 1234)' : 'Masukkan Nomor Part...'"
                  @keyup.enter="handleSearch"
                />
            </div>
            
            <div class="flex items-center gap-2 px-2">
                <select 
                  v-model="searchType"
                  class="bg-slate-50 border-none text-slate-600 rounded-lg py-3 px-4 focus:ring-2 focus:ring-blue-500/50 cursor-pointer hover:bg-slate-100 transition-colors"
                >
                  <option value="line">Line No.</option>
                  <option value="part">Part No.</option>
                </select>
                
                <button 
                  @click="handleSearch"
                  class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg transition-all duration-200 shadow-md flex items-center gap-2"
                >
                  Cari
                </button>
            </div>
        </div>

        <!-- Browse Shortcuts -->
        <div class="flex gap-4 mt-6">
             <button @click="handleBrowseStickers" class="flex items-center gap-2 bg-white/50 hover:bg-white border border-slate-200 px-4 py-2 rounded-lg text-slate-600 hover:text-blue-600 transition-all text-sm font-bold shadow-sm">
                <Filter class="w-4 h-4" />
                Browse Stickers (787-8)
             </button>
        </div>
      </div>
    </div>

    <!-- Active Filters & Stats (Placeholder for now) -->
    <div v-if="partsStore.searchResults.length > 0" class="flex items-center justify-between px-2">
        <h2 class="text-xl font-bold text-slate-800">Hasil Pencarian <span class="text-slate-500 font-normal">({{ partsStore.searchResults.length }})</span></h2>
        <button class="flex items-center gap-2 text-slate-500 hover:text-blue-600 px-4 py-2 rounded-lg hover:bg-blue-50 transition-all">
             <Filter class="w-4 h-4" />
             <span>Filter Hasil</span>
        </button>
    </div>

    <!-- Results Area -->
    <div v-if="!partsStore.loading && partsStore.searchResults.length === 0" class="flex flex-col items-center justify-center py-24 text-center">
      <div class="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center mb-6 ring-1 ring-slate-200">
        <Search class="w-10 h-10 text-slate-400" />
      </div>
      <h3 class="text-xl font-bold text-slate-800 mb-2">Belum Ada Konfigurasi Dimuat</h3>
      <p class="text-slate-500 max-w-md">Mulai dengan mencari Nomor Line atau Nomor Part spesifik untuk melihat matriks konfigurasi.</p>
    </div>

    <div v-else-if="partsStore.loading" class="flex flex-col items-center justify-center py-32">
       <div class="relative w-16 h-16">
          <div class="absolute inset-0 border-4 border-slate-200 rounded-full"></div>
          <div class="absolute inset-0 border-4 border-blue-600 rounded-full border-t-transparent animate-spin"></div>
       </div>
       <p class="mt-4 text-slate-500 font-medium animate-pulse">Menganalisis Data Konfigurasi...</p>
    </div>

    <div v-else class="grid grid-cols-1 gap-4 pb-20">
       <PartCard 
         v-for="part in partsStore.searchResults" 
         :key="part.ipd_part_id" 
         :part="part"
         @select="openDetailModal"
       />
    </div>

    <!-- Detail Modal -->
    <PartDetailModal
      v-if="selectedPart"
      :part="selectedPart"
      :risk-profile="partsStore.riskProfile"
      :is-open="!!selectedPart"
      @close="closeDetailModal"
      @confirm="handleConfirmSelection"
    />
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
