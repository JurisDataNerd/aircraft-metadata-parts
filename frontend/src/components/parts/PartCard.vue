<script setup lang="ts">
import { computed } from 'vue';
import type { IPDPart } from '@/types';
import { ChevronRight } from 'lucide-vue-next';

const props = defineProps<{
  part: IPDPart;
}>();

const emit = defineEmits<{
  (e: 'select', part: IPDPart): void;
}>();

const changeTypeLabel = computed(() => {
    switch (props.part.change_type) {
        case 'ADD': return 'TAMBAH';
        case 'DELETE': return 'HAPUS';
        case 'MODIFY': return 'UBAH';
        default: return props.part.change_type;
    }
});
</script>

<template>
  <div 
    @click="emit('select', part)"
    class="bg-white border border-slate-200 rounded-xl p-5 hover:border-blue-400 hover:shadow-md transition-all cursor-pointer group relative overflow-hidden"
  >
    <div class="flex justify-between items-start relative z-10">
      <div class="flex-1">
        <div class="flex items-center gap-3 mb-2">
            <span class="text-xs font-bold px-2 py-0.5 rounded bg-blue-50 text-blue-600 border border-blue-100 font-mono">
                ITEM {{ part.item }}
            </span>
            <span v-if="part.change_type !== 'MODIFY'" 
                :class="{
                    'text-green-600 bg-green-50 border-green-200': part.change_type === 'ADD',
                    'text-red-600 bg-red-50 border-red-200': part.change_type === 'DELETE'
                }"
                class="text-[10px] font-bold px-1.5 py-px rounded border"
            >
                {{ changeTypeLabel }}
            </span>
        </div>
        
        <h3 class="text-xl font-bold text-slate-800 group-hover:text-blue-600 transition-colors tracking-tight">
            {{ part.part_number }}
        </h3>
        <p class="text-slate-500 font-medium">{{ part.nomenclature }}</p>
      
        <div class="mt-4 flex gap-6 text-sm">
             <div class="flex flex-col">
                 <span class="text-[10px] uppercase tracking-wider text-slate-400 font-bold">Efektivitas</span>
                 <span class="text-slate-700 font-mono font-medium">
                     {{ part.effectivity_type === 'RANGE' 
                        ? `${part.effectivity_range?.from} - ${part.effectivity_range?.to}` 
                        : (part.effectivity_values?.join(', ') || '-') 
                     }}
                 </span>
             </div>
             <div class="flex flex-col">
                 <span class="text-[10px] uppercase tracking-wider text-slate-400 font-bold">UPA</span>
                 <span class="text-slate-700 font-medium">{{ part.upa }}</span>
             </div>
        </div>
      </div>
      
      <div class="flex flex-col items-end gap-2">
        <span class="text-xs text-slate-400 font-medium">Gbr. <span class="text-slate-600 font-mono text-sm">{{ part.figure }}</span></span>
        <div class="w-8 h-8 rounded-full bg-slate-50 flex items-center justify-center text-slate-400 group-hover:bg-blue-600 group-hover:text-white transition-colors">
            <ChevronRight class="w-5 h-5" />
        </div>
      </div>
    </div>
  </div>
</template>
