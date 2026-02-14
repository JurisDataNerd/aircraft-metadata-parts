<script setup lang="ts">
import { ref, computed } from 'vue';
import type { IPDPart, RiskProfile } from '@/types';
import { X, CheckCircle, AlertTriangle, ShieldCheck } from 'lucide-vue-next';

const props = defineProps<{
  part: IPDPart;
  riskProfile: RiskProfile | null;
  isOpen: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'confirm', part: IPDPart): void;
}>();

const isVerified = ref(false);

const riskColor = computed(() => {
  const score = props.riskProfile?.risk_score || 0;
  if (score < 30) return 'text-green-500';
  if (score < 70) return 'text-yellow-500';
  return 'text-red-500';
});

const handleConfirm = () => {
  if (isVerified.value) {
    emit('confirm', props.part);
  }
};
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <!-- Backdrop -->
    <div @click="emit('close')" class="absolute inset-0 bg-slate-950/80 backdrop-blur-sm transition-opacity"></div>

    <!-- Modal Content -->
    <div class="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-2xl shadow-2xl relative overflow-hidden flex flex-col max-h-[90vh]">
        
      <!-- Header -->
      <div class="p-6 border-b border-slate-800 flex justify-between items-start bg-slate-900/50">
        <div>
           <div class="flex items-center gap-2 mb-1">
             <span class="px-2 py-0.5 rounded textxs font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20">Decision Preview</span>
             <span v-if="part.sb_reference" class="px-2 py-0.5 rounded text-xs font-bold bg-yellow-500/10 text-yellow-500 border border-yellow-500/20">SB RELATED</span>
           </div>
           <h2 class="text-2xl font-bold text-white">{{ part.part_number }}</h2>
           <p class="text-slate-400">{{ part.nomenclature }}</p>
        </div>
        <button @click="emit('close')" class="text-slate-500 hover:text-white transition-colors">
          <X class="w-6 h-6" />
        </button>
      </div>

      <!-- Body -->
      <div class="p-6 overflow-y-auto space-y-6">
         <!-- Risk Indicator -->
         <div class="bg-slate-800/50 rounded-xl p-4 border border-slate-700 flex items-center justify-between">
            <div class="flex items-center gap-3">
               <div class="w-12 h-12 rounded-full bg-slate-700 flex items-center justify-center font-bold text-xl" :class="riskColor">
                  {{ riskProfile?.risk_score ?? '-' }}
               </div>
               <div>
                  <h4 class="font-bold text-slate-200">Risk Score</h4>
                  <p class="text-xs text-slate-500">Based on historical data & volatility</p>
               </div>
            </div>
            
            <div class="text-right">
               <span class="block text-sm text-slate-400">Volatility</span>
               <span class="font-bold" :class="{'text-red-400': riskProfile?.volatility_index === 'High', 'text-green-400': riskProfile?.volatility_index === 'Low'}">
                   {{ riskProfile?.volatility_index ?? 'Unknown' }}
               </span>
            </div>
         </div>

         <!-- Warnings -->
         <div v-if="(riskProfile?.similar_part_count || 0) > 0" class="bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-4 flex gap-3 text-yellow-500">
             <AlertTriangle class="w-5 h-5 shrink-0" />
             <div class="text-sm">
                 <strong class="block mb-1">Similar Parts Detected</strong>
                 <p class="opacity-80">There are {{ riskProfile?.similar_part_count }} other parts with similar nomenclature or number. Please verify carefully.</p>
             </div>
         </div>

         <!-- Details Grid -->
         <div class="grid grid-cols-2 gap-4 text-sm">
             <div class="p-3 rounded bg-slate-800/30">
                 <span class="block text-slate-500 mb-1">Figure / Item</span>
                 <span class="font-mono text-slate-300">{{ part.figure }} / {{ part.item }}</span>
             </div>
             <div class="p-3 rounded bg-slate-800/30">
                 <span class="block text-slate-500 mb-1">Effectivity</span>
                 <span class="font-mono text-slate-300">
                     {{ part.effectivity_type === 'RANGE' 
                        ? `${part.effectivity_range?.from} - ${part.effectivity_range?.to}` 
                        : part.effectivity_values.join(', ') }}
                 </span>
             </div>
         </div>
      </div>

      <!-- Footer (Guardrail) -->
      <div class="p-6 border-t border-slate-800 bg-slate-900/80 backdrop-blur pb-8">
          <label class="flex items-start gap-3 cursor-pointer group mb-6">
              <div class="relative flex items-center">
                  <input type="checkbox" v-model="isVerified" class="peer sr-only" />
                  <div class="w-6 h-6 border-2 border-slate-500 rounded peer-checked:bg-blue-600 peer-checked:border-blue-600 transition-all flex items-center justify-center">
                      <CheckCircle class="w-4 h-4 text-white opacity-0 peer-checked:opacity-100 transition-opacity" />
                  </div>
              </div>
              <div>
                  <span class="font-medium text-slate-200 group-hover:text-white transition-colors">I verify this selection against official documents</span>
                  <p class="text-xs text-slate-500 mt-1">By confirming, you acknowledge that you have cross-referenced the drawing/IPD.</p>
              </div>
          </label>

          <button 
             @click="handleConfirm"
             :disabled="!isVerified"
             class="w-full py-4 rounded-xl font-bold flex items-center justify-center gap-2 transition-all"
             :class="isVerified 
                ? 'bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-600/20' 
                : 'bg-slate-800 text-slate-500 cursor-not-allowed'"
          >
             <ShieldCheck class="w-5 h-5" />
             Confirm Selection
          </button>
      </div>

    </div>
  </div>
</template>
