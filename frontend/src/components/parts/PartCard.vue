<script setup lang="ts">
import type { IPDPart } from '@/types';
import { ChevronRight } from 'lucide-vue-next';

defineProps<{
  part: IPDPart;
}>();

const emit = defineEmits<{
  (e: 'select', part: IPDPart): void;
}>();
</script>

<template>
  <div 
    @click="emit('select', part)"
    class="bg-slate-900 border border-slate-800 rounded-lg p-5 hover:border-blue-500/50 hover:bg-slate-800/50 transition-all cursor-pointer group relative overflow-hidden"
  >
    <div class="flex justify-between items-start relative z-10">
      <div class="flex-1">
        <div class="flex items-center gap-3 mb-2">
            <span class="text-xs font-bold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-mono">
                ITEM {{ part.item }}
            </span>
            <span v-if="part.change_type !== 'MODIFY'" 
                :class="{
                    'text-green-400 bg-green-400/10 border-green-400/20': part.change_type === 'ADD',
                    'text-red-400 bg-red-400/10 border-red-400/20': part.change_type === 'DELETE'
                }"
                class="text-[10px] font-bold px-1.5 py-px rounded border"
            >
                {{ part.change_type }}
            </span>
        </div>
        
        <h3 class="text-xl font-bold text-white group-hover:text-blue-400 transition-colors tracking-tight">
            {{ part.part_number }}
        </h3>
        <p class="text-slate-400 font-medium">{{ part.nomenclature }}</p>
      
        <div class="mt-4 flex gap-4 text-sm text-slate-500">
             <div class="flex flex-col">
                 <span class="text-[10px] uppercase tracking-wider text-slate-600">Effectivity</span>
                 <span class="text-slate-300 font-mono">
                     {{ part.effectivity_type === 'RANGE' 
                        ? `${part.effectivity_range?.from} - ${part.effectivity_range?.to}` 
                        : part.effectivity_values.join(', ') 
                     }}
                 </span>
             </div>
             <div class="flex flex-col">
                 <span class="text-[10px] uppercase tracking-wider text-slate-600">UPA</span>
                 <span class="text-slate-300">{{ part.upa }}</span>
             </div>
        </div>
      </div>
      
      <div class="flex flex-col items-end gap-2">
        <span class="text-xs text-slate-500">Fig. <span class="text-slate-300 font-mono">{{ part.figure }}</span></span>
        <div class="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center group-hover:bg-blue-600 group-hover:text-white transition-colors">
            <ChevronRight class="w-5 h-5" />
        </div>
      </div>
    </div>
  </div>
</template>
