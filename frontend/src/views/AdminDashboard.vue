<script setup lang="ts">
import { onMounted, computed } from 'vue';
import { usePartsStore } from '@/stores/parts';
import { ShieldAlert, AlertTriangle, Activity, FileText, ArrowUpRight } from 'lucide-vue-next';

const partsStore = usePartsStore();

onMounted(() => {
    partsStore.fetchStatistics();
});

// Computed Stats from Real Backend Data
const stats = computed(() => {
    const s = partsStore.statistics;
    if (!s) return [];

    return [
        { 
            title: 'Total Parts', 
            value: s.total_parts?.toLocaleString() || '0', 
            change: '', 
            trend: 'neutral', 
            icon: ShieldAlert,
            color: 'text-blue-600',
            bg: 'bg-blue-50'
        },
        { 
            title: 'Total Dokumen', 
            value: s.documents?.toString() || '0', 
            change: `+${s.recent_uploads || 0} hari ini`, 
            trend: 'up', 
            icon: FileText,
            color: 'text-emerald-600',
            bg: 'bg-emerald-50'
        },
        { 
            title: 'Tipe Range', 
            value: s.parts_by_type?.RANGE?.toLocaleString() || '0', 
            change: 'Parts', 
            trend: 'neutral', 
            icon: Activity,
            color: 'text-indigo-600',
            bg: 'bg-indigo-50'
        },
         { 
            title: 'Sticker/Placard', 
            value: s.sticker_count?.toLocaleString() || '0', 
            change: 'Parts', 
            trend: 'neutral', 
            icon: AlertTriangle,
            color: 'text-yellow-600',
            bg: 'bg-yellow-50'
        }
    ];
});

// Add to onMounted
onMounted(async () => {
    await partsStore.fetchStatistics();
    await partsStore.fetchDocuments();
});

const topLines = computed(() => partsStore.statistics?.top_lines || []);
const recentUploads = computed(() => {
    return partsStore.documents.slice(0, 3).map(doc => ({
        id: doc.document_id,
        title: `Upload Dokumen: ${doc.document_number}`,
        subtitle: `User: System • ${new Date(doc.uploaded_at).toLocaleString('id-ID')}`,
        status: doc.parsing_status,
        color: doc.parsing_status === 'completed' ? 'bg-emerald-500' : (doc.parsing_status === 'failed' ? 'bg-red-500' : 'bg-blue-500'),
        bg: doc.parsing_status === 'completed' ? 'bg-emerald-50 border-emerald-100' : (doc.parsing_status === 'failed' ? 'bg-red-50 border-red-100' : 'bg-blue-50 border-blue-100')
    }));
});
</script>

<template>
  <div class="space-y-8 animate-fade-in">
    <!-- Header -->
    <div>
        <h1 class="text-3xl font-bold text-slate-800 mb-2">Analitik Admin</h1>
        <p class="text-slate-500">Pemantauan sistem terhadap keputusan konfigurasi dan pola risiko.</p>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div v-for="stat in stats" :key="stat.title" class="bg-white border border-slate-200 rounded-xl p-6 relative overflow-hidden group hover:border-blue-200 hover:shadow-md transition-all">
            <div class="flex items-start justify-between mb-4">
                <div class="p-3 rounded-lg" :class="stat.bg">
                    <component :is="stat.icon" class="w-6 h-6" :class="stat.color" />
                </div>
                <div class="flex items-center gap-1 text-xs font-bold" :class="stat.trend === 'up' && stat.title !== 'Rata-rata Waktu Keputusan' ? 'text-emerald-600' : 'text-slate-500'">
                    {{ stat.change }}
                    <ArrowUpRight v-if="stat.trend === 'up'" class="w-3 h-3" />
                </div>
            </div>
            <h3 class="text-slate-500 text-sm font-medium mb-1">{{ stat.title }}</h3>
            <p class="text-3xl font-bold text-slate-800">{{ stat.value }}</p>
        </div>
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- Top Lines Table -->
        <div class="lg:col-span-2 bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <div class="flex items-center justify-between mb-6">
                <h3 class="text-lg font-bold text-slate-800 flex items-center gap-2">
                    <TrendingUp class="w-5 h-5 text-blue-500" />
                    Top Line Conf. (Effectivity LIST)
                </h3>
            </div>
            
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="border-b border-slate-100 text-slate-500 text-xs uppercase tracking-wider">
                            <th class="py-3 font-semibold">Line Number</th>
                            <th class="py-3 font-semibold text-right">Jumlah Part</th>
                        </tr>
                    </thead>
                    <tbody class="text-sm">
                        <tr v-if="topLines.length === 0">
                            <td colspan="2" class="py-4 text-center text-slate-500 italic">Belum ada data...</td>
                        </tr>
                        <tr v-for="item in topLines" :key="item.line" class="border-b border-slate-50 hover:bg-slate-50 transition-colors">
                            <td class="py-4 font-mono text-slate-700 font-bold">L-{{ item.line }}</td>
                            <td class="py-4 text-right text-slate-600 font-mono">{{ item.count }} Parts</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Recent Activity / Drift Log -->
        <div class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <h3 class="text-lg font-bold text-slate-800 mb-6">Aktivitas Upload Terkini</h3>
            <div class="space-y-6">
                 
                 <div v-if="recentUploads.length === 0" class="text-center py-8 text-slate-400 text-sm italic">
                    Belum ada aktivitas upload.
                 </div>

                 <div v-for="item in recentUploads" :key="item.id" class="relative pl-6 border-l-2 border-slate-200 pb-2">
                    <div class="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-white border-2" :class="item.color === 'bg-emerald-500' ? 'border-emerald-500' : (item.color === 'bg-red-500' ? 'border-red-500' : 'border-blue-500')"></div>
                    <p class="text-sm font-bold text-slate-800 mb-1">{{ item.title }}</p>
                    <p class="text-xs text-slate-500 mb-2">{{ item.subtitle }}</p>
                    <p class="text-xs text-slate-600 p-2 rounded border" :class="item.bg">Status: {{ item.status }}</p>
                 </div>
            </div>
        </div>

    </div>
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
