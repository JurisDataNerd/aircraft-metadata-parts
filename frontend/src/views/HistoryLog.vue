<script setup lang="ts">
import { onMounted, computed } from 'vue';
import { usePartsStore } from '@/stores/parts';
import { Calendar, Download, FileText, Loader2 } from 'lucide-vue-next';

const partsStore = usePartsStore();

onMounted(() => {
    partsStore.fetchDocuments();
});

const logs = computed(() => {
    return partsStore.documents.map(doc => ({
        id: doc.document_id,
        action: 'Upload Dokumen',
        user: 'System Admin', // Hardcoded for now as no auth
        line: '-',
        part: '-',
        timestamp: new Date(doc.uploaded_at).toLocaleString('id-ID'),
        status: doc.parsing_status,
        details: doc.document_number,
        type: doc.document_type
    }));
});

</script>

<template>
  <div class="space-y-8 animate-fade-in">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
            <h1 class="text-3xl font-bold text-slate-800 mb-2">Riwayat & Log Aktivitas</h1>
            <p class="text-slate-500">Jejak audit aktivitas sistem dan upload dokumen.</p>
        </div>
        <button class="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 hover:text-blue-600 transition-colors shadow-sm cursor-not-allowed opacity-50">
            <Download class="w-4 h-4" />
            <span>Ekspor Data (Soon)</span>
        </button>
    </div>

    <!-- Filters (Visual Only for Phase 1) -->
    <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex flex-col md:flex-row gap-4 items-end md:items-center opacity-75 pointer-events-none">
        <div class="flex-1 w-full grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="space-y-1">
                <label class="text-xs font-bold text-slate-500 uppercase">Rentang Tanggal</label>
                <div class="relative">
                    <Calendar class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                    <input disabled type="date" class="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-700" />
                </div>
            </div>
             <div class="space-y-1">
                <label class="text-xs font-bold text-slate-500 uppercase">Tipe Aktivitas</label>
                <select disabled class="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-700">
                    <option value="all">Semua Aktivitas</option>
                </select>
            </div>
        </div>
    </div>

    <!-- Log Table -->
    <div class="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
                <thead>
                    <tr class="bg-slate-50 border-b border-slate-200 text-slate-500 text-xs uppercase tracking-wider">
                        <th class="px-6 py-4 font-bold">Waktu</th>
                        <th class="px-6 py-4 font-bold">User</th>
                        <th class="px-6 py-4 font-bold">Aktivitas</th>
                        <th class="px-6 py-4 font-bold">Detail Dokumen</th>
                        <th class="px-6 py-4 font-bold text-right">Status</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
                    <tr v-if="logs.length === 0" class="hover:bg-slate-50">
                        <td colspan="5" class="px-6 py-8 text-center text-slate-500">Tidak ada riwayat aktivitas ditemukan.</td>
                    </tr>
                    <tr v-for="log in logs" :key="log.id" class="hover:bg-blue-50/30 transition-colors">
                        <td class="px-6 py-4 text-sm text-slate-500 whitespace-nowrap font-mono">{{ log.timestamp }}</td>
                        <td class="px-6 py-4 text-sm font-medium text-slate-800">
                            <div class="flex items-center gap-2">
                                <div class="w-6 h-6 rounded-full bg-slate-100 flex items-center justify-center text-xs font-bold text-slate-500">SA</div>
                                {{ log.user }}
                            </div>
                        </td>
                        <td class="px-6 py-4 text-sm text-slate-700">{{ log.action }}</td>
                        <td class="px-6 py-4 text-sm">
                            <div class="flex items-center gap-2">
                                <FileText class="w-4 h-4 text-blue-500" />
                                <span class="font-mono text-slate-600 font-medium">{{ log.details }}</span>
                                <span class="text-xs text-slate-400 uppercase border px-1 rounded">{{ log.type }}</span>
                            </div>
                        </td>
                        <td class="px-6 py-4 text-right">
                             <span v-if="log.status === 'completed'" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-600 border border-emerald-200">
                                Selesai
                            </span>
                            <span v-else-if="log.status === 'processing'" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-100 text-blue-600 border border-blue-200">
                                <Loader2 class="w-3 h-3 mr-1 animate-spin" /> Memproses
                            </span>
                            <span v-else-if="log.status === 'failed'" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-red-100 text-red-600 border border-red-200">
                                Gagal
                            </span>
                             <span v-else class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-slate-100 text-slate-500 border border-slate-200">
                                {{ log.status }}
                            </span>
                        </td>
                    </tr>
                </tbody>
            </table>
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
