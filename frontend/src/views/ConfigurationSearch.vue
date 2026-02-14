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
const selectedPart = ref<IPDPart | null>(null);

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
    alert(`Confirmed selection: ${part.part_number}`);
};
</script>

<template>
  <div class="space-y-6">
    <!-- Header Section -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-white">Configuration Search</h1>
        <p class="text-slate-400">Search by Line Number or Part Number to view configuration status.</p>
      </div>
    </div>

    <!-- Search Card -->
    <div class="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl relative overflow-hidden">
      <!-- Background Abstract -->
      <div class="absolute top-0 right-0 w-64 h-64 bg-blue-600/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>

      <div class="relative z-10 flex flex-col md:flex-row gap-4 items-end">
        <div class="flex-1 w-full space-y-2">
          <label class="text-sm font-medium text-slate-300">Search Parameter</label>
          <div class="flex">
            <div class="relative flex-1">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search class="h-5 w-5 text-slate-500" />
              </div>
              <input 
                v-model="searchQuery"
                type="text" 
                class="block w-full pl-10 pr-3 py-3 bg-slate-950 border border-slate-700 rounded-l-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                :placeholder="searchType === 'line' ? 'Enter Line Number (e.g. 1234)' : 'Enter Part Number...'"
                @keyup.enter="handleSearch"
              />
            </div>
            <select 
              v-model="searchType"
              class="bg-slate-800 border-y border-r border-slate-700 text-slate-300 py-3 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            >
              <option value="line">Line No.</option>
              <option value="part">Part No.</option>
            </select>
            <button 
              @click="handleSearch"
              class="bg-blue-600 hover:bg-blue-500 text-white font-medium py-3 px-6 rounded-r-lg transition-all duration-200 flex items-center gap-2 shadow-lg shadow-blue-600/20"
            >
              Search
            </button>
          </div>
        </div>
        
        <div class="hidden md:block">
           <button class="flex items-center gap-2 text-slate-400 hover:text-white px-4 py-3 rounded-lg border border-slate-800 hover:border-slate-700 transition-all">
             <Filter class="w-4 h-4" />
             <span>Filters</span>
           </button>
        </div>
      </div>
    </div>

    <!-- Results Area (Empty State or Results) -->
    <div v-if="!partsStore.loading && partsStore.searchResults.length === 0" class="flex flex-col items-center justify-center py-20 bg-slate-900/50 border border-slate-800/50 rounded-xl border-dashed">
      <div class="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mb-4">
        <Search class="w-8 h-8 text-slate-500" />
      </div>
      <h3 class="text-lg font-medium text-slate-300">No Search Results</h3>
      <p class="text-slate-500 max-w-sm text-center mt-2">Enter a line number or part number above to see configuration details.</p>
    </div>

    <div v-else-if="partsStore.loading" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
    </div>

    <div v-else class="grid grid-cols-1 gap-4">
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
