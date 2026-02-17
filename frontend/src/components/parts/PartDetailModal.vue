<script setup lang="ts">
import { ref, computed } from 'vue';
import type { IPDPart, RiskProfile } from '@/types';
import { X, CheckCircle, ShieldCheck, FileText, Activity, AlertOctagon } from 'lucide-vue-next';

const props = defineProps<{
  part: IPDPart;
  riskProfile: RiskProfile | null;
  isOpen: boolean;
}>();

const emit = defineEmits(['close', 'confirm']);

const isGuardrailChecked = ref(false);

const riskColor = computed(() => {
    const score = props.riskProfile?.risk_score || 0;
    if (score >= 80) return 'text-red-600 bg-red-50 border-red-200';
    if (score >= 50) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-emerald-600 bg-emerald-50 border-emerald-200';
});

const progressColor = computed(() => {
    const score = props.riskProfile?.risk_score || 0;
    if (score >= 80) return 'text-red-500';
    if (score >= 50) return 'text-yellow-500';
    return 'text-emerald-500';
});

const formattedEffectivity = computed(() => {
    if (props.part.effectivity_type === 'RANGE' && props.part.effectivity_range) {
        return `${props.part.effectivity_range.from} - ${props.part.effectivity_range.to}`;
    }
    return props.part.effectivity_values.join(', ');
});

const handleConfirm = () => {
    if (isGuardrailChecked.value) {
        emit('confirm', props.part);
    }
};
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <!-- Backdrop -->
    <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm transition-opacity" @click="emit('close')"></div>

    <!-- Modal Content -->
    <div class="relative w-full max-w-4xl bg-white rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh] animate-scale-in border border-slate-200">
        
        <!-- Header -->
        <div class="p-6 border-b border-slate-100 flex items-start justify-between bg-slate-50/50">
            <div>
                <div class="flex items-center gap-3 mb-2">
                    <span class="px-2.5 py-1 rounded-md bg-blue-100 text-blue-700 text-xs font-bold font-mono tracking-wide">
                        {{ part.part_number }}
                    </span>
                    <span v-if="part.is_extracting" class="flex items-center gap-1 text-xs text-blue-600 animate-pulse">
                        <Activity class="w-3 h-3" /> Memproses Data...
                    </span>
                </div>
                <h2 class="text-2xl font-bold text-slate-800">{{ part.nomenclature }}</h2>
            </div>
            <button @click="emit('close')" class="p-2 rounded-full hover:bg-slate-200 text-slate-400 hover:text-slate-600 transition-colors">
                <X class="w-6 h-6" />
            </button>
        </div>

        <!-- Body -->
        <div class="flex-1 overflow-y-auto p-6 space-y-8">
            
            <!-- Risk & Status Section -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <!-- Risk Score Card -->
                <div class="col-span-1 p-5 rounded-xl border flex flex-col items-center justify-center text-center relative overflow-hidden" :class="riskColor">
                    <h3 class="text-sm font-bold uppercase tracking-wider mb-2 opacity-80">Skor Risiko</h3>
                    
                    <!-- Circular Progress (Simple Implementation) -->
                    <div class="relative w-24 h-24 flex items-center justify-center mb-2">
                        <svg class="w-full h-full transform -rotate-90">
                            <circle cx="48" cy="48" r="40" stroke="currentColor" stroke-width="8" fill="transparent" class="text-slate-200" />
                            <circle cx="48" cy="48" r="40" stroke="currentColor" stroke-width="8" fill="transparent" 
                                :stroke-dasharray="251.2" 
                                :stroke-dashoffset="251.2 - (251.2 * (riskProfile?.risk_score || 0) / 100)" 
                                class="transition-all duration-1000 ease-out"
                                :class="progressColor"
                            />
                        </svg>
                        <span class="absolute text-3xl font-bold">{{ riskProfile?.risk_score || 0 }}</span>
                    </div>

                    <div v-if="(riskProfile?.volatility_index === 'High')" class="flex items-center gap-1 text-xs font-bold text-red-600 bg-red-100 px-2 py-1 rounded-full mt-2">
                        <Activity class="w-3 h-3" /> Volatilitas Tinggi
                    </div>
                </div>

                <!-- Technical Details -->
                <div class="col-span-2 space-y-4">
                    <div class="grid grid-cols-2 gap-4">
                        <div class="p-4 bg-slate-50 rounded-xl border border-slate-100">
                             <div class="flex items-center gap-2 mb-1 text-slate-500 text-xs font-bold uppercase">
                                <FileText class="w-4 h-4" /> Item Number
                            </div>
                            <p class="font-mono text-lg font-semibold text-slate-800">{{ part.item }}</p>
                        </div>
                        <div class="p-4 bg-slate-50 rounded-xl border border-slate-100">
                             <div class="flex items-center gap-2 mb-1 text-slate-500 text-xs font-bold uppercase">
                                <ShieldCheck class="w-4 h-4" /> Efektivitas
                            </div>
                            <p class="font-mono text-lg font-semibold text-slate-800">{{ formattedEffectivity }}</p>
                        </div>
                    </div>

                    <!-- Warning / Similar Parts -->
                    <div v-if="(riskProfile?.similar_part_count || 0) > 0" class="p-4 bg-yellow-50 rounded-xl border border-yellow-200">
                        <h4 class="flex items-center gap-2 text-yellow-800 font-bold mb-3">
                            <AlertOctagon class="w-5 h-5" />
                            Deteksi Part Serupa
                        </h4>
                        <p class="text-sm text-yellow-700">
                            Terdeteksi <span class="font-bold">{{ riskProfile?.similar_part_count }}</span> part serupa yang mungkin relevan dengan konfigurasi ini.
                        </p>
                    </div>
                </div>
            </div>

             <!-- Description -->
             <div>
                <h3 class="text-sm font-bold text-slate-500 uppercase tracking-wider mb-2">Deskripsi Teknis</h3>
                <p class="text-slate-700 leading-relaxed bg-slate-50 p-4 rounded-xl border border-slate-100">
                    Ini adalah komponen konfigurasi standar. Pastikan untuk memverifikasi referensi silang dengan dokumen IPD terbaru sebelum instalasi. Periksa drawing engineering untuk toleransi dimensi spesifik.
                </p>
            </div>
        </div>

        <!-- Guardrail Footer -->
        <div class="p-6 bg-slate-50 border-t border-slate-200 flex flex-col md:flex-row items-center justify-between gap-4">
             <label class="flex items-center gap-3 cursor-pointer group">
                <div class="relative">
                    <input type="checkbox" v-model="isGuardrailChecked" class="peer sr-only">
                    <div class="w-6 h-6 border-2 border-slate-300 rounded bg-white peer-checked:bg-blue-600 peer-checked:border-blue-600 transition-all flex items-center justify-center">
                        <CheckCircle class="w-4 h-4 text-white opacity-0 peer-checked:opacity-100 transition-opacity" />
                    </div>
                </div>
                <span class="text-sm font-medium text-slate-600 group-hover:text-slate-800 select-none">
                    Saya telah memverifikasi kecocokan part ini dengan persyaratan konfigurasi.
                </span>
            </label>

            <div class="flex gap-3 w-full md:w-auto">
                <button @click="emit('close')" class="flex-1 md:flex-none px-6 py-2.5 rounded-lg border border-slate-300 text-slate-700 font-medium hover:bg-slate-100 transition-colors">
                    Batal
                </button>
                <button 
                    @click="handleConfirm"
                    :disabled="!isGuardrailChecked"
                    class="flex-1 md:flex-none px-6 py-2.5 rounded-lg bg-blue-600 text-white font-bold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-blue-600/20 active:scale-95 flex items-center justify-center gap-2"
                >
                    <ShieldCheck class="w-4 h-4" />
                    Konfirmasi Pilihan
                </button>
            </div>
        </div>

    </div>
  </div>
</template>

<style scoped>
.animate-scale-in {
  animation: scaleIn 0.2s ease-out;
}

@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
</style>
